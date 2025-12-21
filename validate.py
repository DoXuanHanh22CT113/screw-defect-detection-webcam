"""
=============================================================================
FILE: validate.py
=============================================================================
MÔ TẢ:
    Module validation để lọc các detections không hợp lệ.
    
MỤC ĐÍCH:
    - Loại bỏ các bounding boxes quá nhỏ, quá lớn, hoặc có tỉ lệ bất thường
    - Điều chỉnh ngưỡng confidence theo từng class
    - Giảm false positive (nhận nhầm ốc tốt thành lỗi)
    - Giảm false negative (bỏ sót ốc lỗi)

LOGIC CHÍNH:
    1. Kiểm tra confidence score có đủ cao không
    2. Kiểm tra kích thước box (diện tích, chiều rộng, chiều cao)
    3. Kiểm tra tỉ lệ aspect ratio (width/height)
    4. Kiểm tra vị trí (không quá sát mép ảnh)
    
THAM SỐ QUAN TRỌNG:
    - CLASS_CONFIDENCE_OFFSET: Điều chỉnh ngưỡng theo class
    - DEFAULT_RULES: Quy tắc mặc định cho mọi class
    - CLASS_RULE_OVERRIDES: Quy tắc riêng cho từng class
=============================================================================
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple, Union

# ============================================================================
# CẤU HÌNH CÁC QUY TẮC VALIDATION
# ============================================================================

# Quy tắc mặc định áp dụng cho mọi lớp (OK & defect)
# Các giá trị đã được tinh chỉnh để cân bằng giữa detection và false positive
DEFAULT_RULES: Dict[str, Union[float, Tuple[float, float]]] = {
    # Diện tích tối thiểu >= 0.02% diện tích frame (~60px² với 640x480)
    "min_area_ratio": 0.0002,
    
    # Diện tích tối đa <= 80% frame (cho phép box lớn khi vít gần camera)
    "max_area_ratio": 0.80,
    
    # Chiều rộng tối thiểu >= 1.5% chiều ngang frame
    "min_width_ratio": 0.015,
    
    # Chiều cao tối thiểu >= 1.5% chiều cao frame
    "min_height_ratio": 0.015,
    
    # Tỉ lệ aspect ratio (width/height) phải nằm trong khoảng [0.08, 15.0]
    # Nới lỏng để chấp nhận ốc nằm ngang hoặc đứng
    "aspect_ratio": (0.08, 15.0),
    
    # Tâm box phải cách mép frame ít nhất 0.5%
    # Tránh detect các object bị cắt mất ở mép
    "edge_buffer_ratio": 0.005,
}

# ============================================================================
# QUY TẮC RIÊNG THEO CLASS (6 classes từ best.pt)
# ============================================================================
# 0=ok, 1=manipulated_front, 2=scratch_head, 3=scratch_neck, 4=thread_side, 5=thread_top
CLASS_RULE_OVERRIDES: Dict[int, Dict[str, Union[float, Tuple[float, float]]]] = {
    # Class 0: OK - ốc bình thường
    # Yêu cầu box khá lớn để chắc chắn là vít hoàn chỉnh
    0: {
        "min_area_ratio": 0.001,     # Lớn hơn defect vì ốc OK thường rõ ràng hơn
        "max_area_ratio": 0.85,
        "aspect_ratio": (0.1, 10.0), # Chặt hơn một chút
    },
    
    # Class 1: Manipulated Front - vít bị biến dạng mặt trước
    # Nới lỏng vì defect có thể nhỏ và khó phát hiện
    1: {
        "min_area_ratio": 0.0001,
        "max_area_ratio": 0.85,
        "aspect_ratio": (0.03, 30.0),  # Rất lỏng
    },
    
    # Classes 2-5: Các loại scratch và thread defects
    # Chia sẻ cùng một bộ quy tắc lỏng
    # scratch_head, scratch_neck, thread_side, thread_top
    **{class_id: {
        "min_area_ratio": 0.00005,   # Rất nhỏ vì vết xước có thể rất nhỏ
        "max_area_ratio": 0.85,
        "aspect_ratio": (0.02, 50.0),  # Rất lỏng
    } for class_id in [2, 3, 4, 5]}
}

# ============================================================================
# ĐIỀU CHỈNH CONFIDENCE THEO CLASS
# ============================================================================
# Offset DƯƠNG (+) = yêu cầu cao hơn (khó phát hiện hơn)
# Offset ÂM (-) = yêu cầu thấp hơn (dễ phát hiện hơn)
#
# CHIẾN LƯỢC: CÂN BẰNG
# - OK (+0.10): Yêu cầu cao hơn để tránh nhận nhầm defect thành OK
# - Defect (-0.05): Giảm nhẹ để không bỏ sót defect
#
# VÍ DỤ với ngưỡng base = 0.35:
# - OK sẽ cần score >= 0.45 (0.35 + 0.10)
# - Defect chỉ cần score >= 0.30 (0.35 - 0.05)
CLASS_CONFIDENCE_OFFSET: Dict[int, float] = {
    0: +0.10,   # OK → yêu cầu cao hơn một chút để tăng độ tin cậy
    1: -0.05,   # manipulated_front - giảm nhẹ để phát hiện được
    2: -0.05,   # scratch_head - giảm nhẹ
    3: -0.05,   # scratch_neck - giảm nhẹ
    4: -0.05,   # thread_side - giảm nhẹ
    5: -0.05,   # thread_top - giảm nhẹ
}

# Giới hạn an toàn cho confidence
CONFIDENCE_MIN = 0.10   # Tối thiểu 10% - lọc bớt detections quá yếu
CONFIDENCE_MAX = 0.97   # Tối đa 97%

# -------------------------------------------------------------------------

BoxType = Sequence[Union[int, float]]
FrameShape = Sequence[int]


# ============================================================================
# CÁC HÀM HELPER
# ============================================================================

def _resolve_rules(class_id: int) -> Dict[str, Union[float, Tuple[float, float]]]:
    """
    Gộp rule mặc định với rule riêng của class.
    
    Logic:
    1. Bắt đầu với DEFAULT_RULES (quy tắc chung)
    2. Nếu class có rule riêng trong CLASS_RULE_OVERRIDES, ghi đè lên
    
    Ví dụ:
    - Class 0 (OK) sẽ dùng min_area_ratio=0.001 (từ CLASS_RULE_OVERRIDES)
      thay vì 0.0002 (từ DEFAULT_RULES)
    
    Args:
        class_id: ID của class (0-5)
    
    Returns:
        Dict chứa tất cả rules cho class đó
    """
    rules = dict(DEFAULT_RULES)
    overrides = CLASS_RULE_OVERRIDES.get(class_id)
    if overrides:
        rules.update(overrides)
    return rules


def _effective_conf_threshold(base_conf: float, class_id: int) -> float:
    """
    Tính ngưỡng confidence thực tế cho một class.
    
    Công thức: effective_threshold = base_conf + CLASS_CONFIDENCE_OFFSET[class_id]
    Kết quả được giới hạn trong [CONFIDENCE_MIN, CONFIDENCE_MAX]
    
    Ví dụ với base_conf = 0.35:
    - Class 0 (OK):     0.35 + 0.10 = 0.45 (yêu cầu cao hơn)
    - Class 1 (defect): 0.35 - 0.05 = 0.30 (dễ phát hiện hơn)
    
    Args:
        base_conf: Ngưỡng confidence cơ sở (được set bởi user qua slider)
        class_id: ID của class
    
    Returns:
        Ngưỡng confidence đã điều chỉnh
    """
    offset = CLASS_CONFIDENCE_OFFSET.get(class_id, 0.0)
    adjusted = base_conf + offset
    return max(CONFIDENCE_MIN, min(CONFIDENCE_MAX, adjusted))


def _clip_box_to_frame(box: BoxType, frame_w: int, frame_h: int) -> Tuple[float, float, float, float]:
    """
    Đảm bảo tọa độ box nằm trong frame và hợp lệ.
    
    Xử lý:
    1. Clip tọa độ vào trong giới hạn frame (không âm, không vượt frame)
    2. Đảm bảo x1 < x2 và y1 < y2 (hoán đổi nếu cần)
    
    Args:
        box: Bounding box [x1, y1, x2, y2]
        frame_w, frame_h: Kích thước frame
    
    Returns:
        (x1, y1, x2, y2) đã được clip và chuẩn hóa
    """
    x1, y1, x2, y2 = (float(box[i]) for i in range(4))
    
    # Clip vào giới hạn frame
    x1 = max(0.0, min(x1, frame_w - 1.0))
    x2 = max(0.0, min(x2, frame_w - 1.0))
    y1 = max(0.0, min(y1, frame_h - 1.0))
    y2 = max(0.0, min(y2, frame_h - 1.0))
    
    # Đảm bảo x1 < x2, y1 < y2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    
    return x1, y1, x2, y2


# ============================================================================
# HÀM KIỂM TRA DETECTION HỢP LỆ
# ============================================================================
def is_valid_detection(
    box: BoxType,
    frame_shape: FrameShape,
    *,
    rules: Dict[str, Union[float, Tuple[float, float]]],
    min_area: float = 30.0,
    max_area_ratio: float = 0.99,
    debug: bool = False,
    class_id: Union[int, None] = None,
) -> Tuple[bool, Union[str, Dict[str, float]]]:
    """
    Kiểm tra hình học của bounding box có hợp lệ không.
    
    CÁC KIỂM TRA:
    1. Diện tích: không quá nhỏ (noise) và không quá lớn (full frame)
    2. Chiều rộng/cao tối thiểu: box phải đủ lớn để thấy rõ
    3. Aspect ratio: tỉ lệ width/height trong khoảng hợp lý
    4. Vị trí: tâm box không quá sát mép ảnh
    
    Args:
        box: Bounding box [x1, y1, x2, y2]
        frame_shape: Kích thước frame (height, width, ...)
        rules: Các quy tắc kiểm tra (từ _resolve_rules)
        min_area: Diện tích tối thiểu (pixels)
        max_area_ratio: Tỉ lệ diện tích tối đa so với frame
        debug: In thông tin debug
        class_id: ID của class (để đưa vào kết quả)
    
    Returns:
        (is_valid, details): True nếu hợp lệ, kèm thông tin chi tiết
    """
    if len(box) < 4:
        return False, "box length < 4"

    if len(frame_shape) < 2:
        return False, "invalid frame_shape"

    frame_h, frame_w = int(frame_shape[0]), int(frame_shape[1])
    if frame_h <= 0 or frame_w <= 0:
        return False, "frame dims <= 0"

    x1, y1, x2, y2 = _clip_box_to_frame(box, frame_w, frame_h)
    width = x2 - x1
    height = y2 - y1
    if width <= 1.0 or height <= 1.0:
        return False, f"width/height too small (w={width:.1f}, h={height:.1f})"

    area = width * height
    frame_area = float(frame_h * frame_w)

    # ---- Area checks ----
    min_area_ratio = float(rules.get("min_area_ratio", 0.0))
    min_area_from_ratio = frame_area * min_area_ratio
    effective_min_area = max(float(min_area), min_area_from_ratio)
    if area < effective_min_area:
        return False, f"area={area:.0f} < min_area={effective_min_area:.0f}"

    area_ratio = area / frame_area
    rule_max_area_ratio = float(rules.get("max_area_ratio", max_area_ratio))
    effective_max_area_ratio = min(float(max_area_ratio), rule_max_area_ratio)
    if area_ratio > effective_max_area_ratio:
        return False, f"area_ratio={area_ratio:.3f} > max_area_ratio={effective_max_area_ratio:.3f}"

    # ---- Width/height checks ----
    min_width_ratio = float(rules.get("min_width_ratio", 0.0))
    min_height_ratio = float(rules.get("min_height_ratio", 0.0))
    min_width = max(rules.get("min_width_pixels", 0.0) or 0.0, frame_w * min_width_ratio)
    min_height = max(rules.get("min_height_pixels", 0.0) or 0.0, frame_h * min_height_ratio)

    if width < min_width:
        return False, f"width={width:.1f} < min_width={min_width:.1f}"
    if height < min_height:
        return False, f"height={height:.1f} < min_height={min_height:.1f}"

    # ---- Aspect ratio ----
    min_aspect, max_aspect = rules.get("aspect_ratio", (0.1, 10.0))  # type: ignore[assignment]
    aspect_ratio = width / height
    if aspect_ratio < float(min_aspect) or aspect_ratio > float(max_aspect):
        return False, (
            f"aspect_ratio={aspect_ratio:.2f} not in "
            f"[{float(min_aspect):.2f}, {float(max_aspect):.2f}]"
        )

    # ---- Edge proximity ----
    edge_buffer_ratio = float(rules.get("edge_buffer_ratio", 0.0))
    if edge_buffer_ratio > 0.0:
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        x_buffer = frame_w * edge_buffer_ratio
        y_buffer = frame_h * edge_buffer_ratio
        if not (x_buffer <= cx <= frame_w - x_buffer and y_buffer <= cy <= frame_h - y_buffer):
            return False, "center too close to frame edge"

    # Box hợp lệ - trả về True và thông tin chi tiết
    return True, {
        "area": area,
        "area_ratio": area_ratio,
        "aspect_ratio": aspect_ratio,
        "width": width,
        "height": height,
        "class_id": float(class_id) if class_id is not None else -1.0,
    }


# ============================================================================
# HÀM LỌC DETECTIONS CHÍNH
# ============================================================================
def filter_detections(
    boxes: Sequence[BoxType],
    scores: Sequence[float],
    class_ids: Sequence[int],
    frame_shape: FrameShape,
    min_conf: float = 0.25,
    min_area: float = 30.0,
    max_area_ratio: float = 0.99,
    debug: bool = False,
) -> Tuple[List[BoxType], List[float], List[int]]:
    """
    Lọc các detections không hợp lệ, giữ lại các detection tốt.
    
    LUỒNG XỬ LÝ CHO MỖI DETECTION:
    1. Kiểm tra confidence:
       - Tính ngưỡng thực tế theo class (_effective_conf_threshold)
       - Nếu score < ngưỡng → LOẠI
    
    2. Kiểm tra hình học:
       - Lấy rules của class (đã merge với DEFAULT_RULES)
       - Kiểm tra diện tích, aspect ratio, vị trí
       - Nếu không hợp lệ → LOẠI
    
    3. Nếu pass cả 2 bước → GIỮ LẠI
    
    Args:
        boxes: Danh sách các bounding boxes
        scores: Danh sách confidence scores tương ứng
        class_ids: Danh sách class IDs tương ứng
        frame_shape: Kích thước frame
        min_conf: Ngưỡng confidence cơ sở
        min_area: Diện tích tối thiểu
        max_area_ratio: Tỉ lệ diện tích tối đa
        debug: In thông tin debug
    
    Returns:
        (filtered_boxes, filtered_scores, filtered_class_ids)
    """
    filtered_boxes: List[BoxType] = []
    filtered_scores: List[float] = []
    filtered_class_ids: List[int] = []

    for i, (box, score, cid) in enumerate(zip(boxes, scores, class_ids)):
        try:
            score_float = float(score)
        except (TypeError, ValueError):
            if debug:
                print(f"   Detection {i}: ⚠️ invalid score {score}")
            continue

        conf_threshold = _effective_conf_threshold(min_conf, int(cid))
        if debug:
            print(
                f"   Detection {i}: score={score_float:.3f}, class={cid}, "
                f"threshold={conf_threshold:.3f}"
            )

        if score_float < conf_threshold:
            if debug:
                print("      → ❌ below confidence threshold")
            continue

        rules = _resolve_rules(int(cid))
        is_valid, details = is_valid_detection(
            box,
            frame_shape,
            rules=rules,
            min_area=min_area,
            max_area_ratio=max_area_ratio,
            debug=debug,
            class_id=int(cid),
        )

        if not is_valid:
            if debug:
                print(f"      → ❌ {details}")
            continue

        if debug and isinstance(details, dict):
            print(
                "      → ✅ area={area:.0f}px² ratio={area_ratio:.3f} "
                "aspect={aspect_ratio:.2f}".format(**details)
            )

        filtered_boxes.append(box)
        filtered_scores.append(score_float)
        filtered_class_ids.append(int(cid))

    return filtered_boxes, filtered_scores, filtered_class_ids