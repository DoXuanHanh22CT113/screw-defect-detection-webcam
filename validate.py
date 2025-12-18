"""
Validation logic to keep YOLO detections that look like screws/defects.

Được tinh chỉnh để giảm false-positive nhưng vẫn giữ lại lỗi thật.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple, Union

# ---- Configuration -------------------------------------------------------

# Các rule mặc định áp dụng cho mọi lớp (OK & defect)
# === THAM SỐ TỐI ƯU CHO PHÁT HIỆN DEFECT ===
# Các rule mặc định đã được tinh chỉnh kỹ lưỡng
DEFAULT_RULES: Dict[str, Union[float, Tuple[float, float]]] = {
    "min_area_ratio": 0.0002,   # >= 0.02% diện tích frame (~60px² với 640x480)
    "max_area_ratio": 0.80,     # Cho phép box lớn (vít gần camera)
    "min_width_ratio": 0.015,   # >= 1.5% chiều ngang frame
    "min_height_ratio": 0.015,  # >= 1.5% chiều cao frame
    "aspect_ratio": (0.08, 15.0),  # Nới lỏng aspect ratio
    "edge_buffer_ratio": 0.005,  # Tâm box cách mép >=0.5%
}

# Rule riêng theo class (6 classes từ best.pt)
# 0=ok, 1=manipulated_front, 2-5=various defects (scratch_head, scratch_neck, thread_side, thread_top)
CLASS_RULE_OVERRIDES: Dict[int, Dict[str, Union[float, Tuple[float, float]]]] = {
    0: {  # OK → yêu cầu box khá lớn để chắc chắn là vít hoàn chỉnh
        "min_area_ratio": 0.001,
        "max_area_ratio": 0.85,
        "aspect_ratio": (0.1, 10.0),
    },
    1: {  # manipulated_front → vít bị biến dạng mặt trước - NỚI LỎNG
        "min_area_ratio": 0.0001,
        "max_area_ratio": 0.85,
        "aspect_ratio": (0.03, 30.0),
    },
    # Classes 2-5 (scratch_head, scratch_neck, thread_side, thread_top) share same relaxed rules
    **{class_id: {
        "min_area_ratio": 0.00005,
        "max_area_ratio": 0.85,
        "aspect_ratio": (0.02, 50.0),
    } for class_id in [2, 3, 4, 5]}
}

# Điều chỉnh confidence theo class.
# Offset DƯƠNG = yêu cầu cao hơn, Offset ÂM = dễ phát hiện hơn
# ƯU TIÊN PHÁT HIỆN DEFECT: Ngưỡng defect THẤP, ngưỡng OK CAO
CLASS_CONFIDENCE_OFFSET: Dict[int, float] = {
    0: +0.25,   # OK → yêu cầu RẤT CAO để tránh nhận nhầm vít lỗi thành OK
    1: -0.25,   # manipulated_front - giảm nhiều để dễ phát hiện
    2: -0.25,   # scratch_head - giảm nhiều (khó detect)
    3: -0.25,   # scratch_neck - giảm nhiều (khó detect)
    4: -0.25,   # thread_side - giảm nhiều (khó detect)
    5: -0.25,   # thread_top - giảm nhiều (khó detect)
}

CONFIDENCE_MIN = 0.02   # Rất thấp để bắt được defect
CONFIDENCE_MAX = 0.97

# -------------------------------------------------------------------------

BoxType = Sequence[Union[int, float]]
FrameShape = Sequence[int]


def _resolve_rules(class_id: int) -> Dict[str, Union[float, Tuple[float, float]]]:
    """Gộp rule mặc định & rule riêng theo class."""
    rules = dict(DEFAULT_RULES)
    overrides = CLASS_RULE_OVERRIDES.get(class_id)
    if overrides:
        rules.update(overrides)
    return rules


def _effective_conf_threshold(base_conf: float, class_id: int) -> float:
    """Cộng offset theo class rồi ép trong khoảng an toàn."""
    offset = CLASS_CONFIDENCE_OFFSET.get(class_id, 0.0)
    adjusted = base_conf + offset
    return max(CONFIDENCE_MIN, min(CONFIDENCE_MAX, adjusted))


def _clip_box_to_frame(box: BoxType, frame_w: int, frame_h: int) -> Tuple[float, float, float, float]:
    """Đảm bảo toạ độ nằm trong frame và x1 < x2, y1 < y2."""
    x1, y1, x2, y2 = (float(box[i]) for i in range(4))
    x1 = max(0.0, min(x1, frame_w - 1.0))
    x2 = max(0.0, min(x2, frame_w - 1.0))
    y1 = max(0.0, min(y1, frame_h - 1.0))
    y2 = max(0.0, min(y2, frame_h - 1.0))
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return x1, y1, x2, y2


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
    """Kiểm tra hình học của bounding box."""
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

    return True, {
        "area": area,
        "area_ratio": area_ratio,
        "aspect_ratio": aspect_ratio,
        "width": width,
        "height": height,
        "class_id": float(class_id) if class_id is not None else -1.0,
    }


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
    """Lọc detections dựa trên confidence và hình học."""
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