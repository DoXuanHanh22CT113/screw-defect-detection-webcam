"""
=============================================================================
FILE: detect.py
=============================================================================
MÔ TẢ:
    Module chính để phát hiện khiếm khuyết ốc vít sử dụng YOLOv8.
    
CHỨC NĂNG CHÍNH:
    1. Load model YOLOv8 đã được train
    2. Tiền xử lý ảnh (cải thiện contrast, giảm nhiễu)
    3. Test-Time Augmentation (TTA) - xoay/flip ảnh để phát hiện tốt hơn
    4. Ensemble nhiều predictions để có kết quả chính xác nhất
    
CÁC LỚP PHÁT HIỆN (6 classes):
    - Class 0: OK (ốc vít bình thường)
    - Class 1: Manipulated Front (biến dạng mặt trước)
    - Class 2: Scratch Head (trầy xước đầu ốc)
    - Class 3: Scratch Neck (trầy xước cổ ốc)
    - Class 4: Thread Side (lỗi ren bên)
    - Class 5: Thread Top (lỗi ren trên)

LUỒNG XỬ LÝ:
    Frame gốc → Tiền xử lý → TTA (xoay/flip) → YOLO predict → 
    → Filter validations → Ensemble → Kết quả cuối cùng
=============================================================================
"""

import cv2
import numpy as np
from ultralytics import YOLO
from utils.visualize import draw_boxes
from validate import filter_detections
from typing import List, Tuple
from collections import defaultdict

# ============================================================================
# BIẾN TOÀN CỤC
# ============================================================================
_model = None       # Lưu trữ model YOLO (singleton pattern để không load lại)
_class_names = None # Danh sách tên các class

# ============================================================================
# HÀM LOAD MODEL
# ============================================================================
def load_model(model_path="best.pt", class_names=None):
    """
    Load model YOLOv8 đã được train.
    
    Sử dụng singleton pattern: model chỉ được load 1 lần duy nhất,
    các lần gọi sau sẽ trả về model đã load trước đó.
    
    Args:
        model_path: Đường dẫn đến file model (.pt)
        class_names: Danh sách tên các class ["OK", "Manipulated Front", ...]
    
    Returns:
        YOLO model object
    """
    global _model, _class_names
    _class_names = class_names
    if _model is None:
        _model = YOLO(model_path)
    return _model

# ============================================================================
# HÀM TIỀN XỬ LÝ ẢNH
# ============================================================================
def preprocess_frame(frame):
    """
    Tiền xử lý ảnh để tăng độ chính xác nhận diện.
    
    Các bước xử lý:
    1. CLAHE (Contrast Limited Adaptive Histogram Equalization):
       - Chuyển ảnh sang không gian màu LAB
       - Cân bằng histogram kênh L (độ sáng) với giới hạn contrast
       - Giúp ảnh rõ nét hơn, dễ phát hiện chi tiết nhỏ
    
    2. Bilateral Filter:
       - Giảm nhiễu nhưng giữ nguyên biên cạnh (edge)
       - Làm mịn các vùng đồng nhất, giữ chi tiết quan trọng
    
    Args:
        frame: Ảnh đầu vào (BGR format)
    
    Returns:
        Ảnh đã được tiền xử lý
    """
    # Bước 1: CLAHE - Cải thiện contrast
    # Chuyển sang LAB để xử lý riêng kênh độ sáng (L)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # CLAHE với clipLimit=2.0 (giới hạn độ tương phản, tránh over-enhancement)
    # tileGridSize=(8,8): chia ảnh thành lưới 8x8 để xử lý cục bộ
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Ghép lại các kênh và chuyển về BGR
    enhanced = cv2.merge([l, a, b])
    processed = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # Bước 2: Bilateral Filter - Giảm nhiễu giữ nguyên biên
    # d=5: đường kính vùng xử lý
    # sigmaColor=50: độ ảnh hưởng của màu sắc
    # sigmaSpace=50: độ ảnh hưởng của không gian
    processed = cv2.bilateralFilter(processed, 5, 50, 50)
    
    return processed

def rotate_image(image, angle):
    """Xoay ảnh theo góc cho trước và trả về ảnh đã xoay"""
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return rotated, M

def rotate_boxes_back(boxes, M, image_shape):
    """Chuyển đổi boxes từ ảnh xoay về ảnh gốc"""
    if not boxes:
        return boxes
    
    h, w = image_shape[:2]
    M_inv = cv2.invertAffineTransform(M)
    
    rotated_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box
        # Chuyển đổi 4 góc của box
        corners = np.array([
            [x1, y1, 1],
            [x2, y1, 1],
            [x2, y2, 1],
            [x1, y2, 1]
        ]).T
        
        transformed = M_inv @ corners
        xs = transformed[0]
        ys = transformed[1]
        
        # Tìm bounding box mới
        new_x1 = max(0, min(xs))
        new_y1 = max(0, min(ys))
        new_x2 = min(w, max(xs))
        new_y2 = min(h, max(ys))
        
        rotated_boxes.append([new_x1, new_y1, new_x2, new_y2])
    
    return rotated_boxes

def flip_boxes(boxes, image_width, flip_type='horizontal'):
    """Chuyển đổi boxes khi flip ảnh"""
    if not boxes:
        return boxes
    
    flipped_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box
        if flip_type == 'horizontal':
            new_x1 = image_width - x2
            new_x2 = image_width - x1
            flipped_boxes.append([new_x1, y1, new_x2, y2])
        else:  # vertical
            # Implement if needed
            flipped_boxes.append(box)
    
    return flipped_boxes

# ============================================================================
# HÀM ENSEMBLE DETECTIONS - GỘP KẾT QUẢ TỪ NHIỀU AUGMENTATIONS
# ============================================================================
def ensemble_detections(all_boxes, all_scores, all_class_ids, iou_threshold=0.5):
    """
    Gộp các detections từ nhiều augmentations (xoay, flip) thành kết quả cuối cùng.
    
    LOGIC CHÍNH:
    1. Gom tất cả detections từ các augmentations lại
    2. Áp dụng NMS (Non-Maximum Suppression) để loại bỏ box trùng lặp
    3. Xử lý conflict giữa OK và DEFECT:
       - Nếu cùng vùng có cả OK và DEFECT detection
       - CHỈ ưu tiên DEFECT nếu score cao hơn OK ít nhất 0.15
       - Nếu score tương đương hoặc OK cao hơn → giữ OK
       - Điều này giúp GIẢM FALSE POSITIVE (ốc OK bị nhận nhầm là lỗi)
    
    Args:
        all_boxes: List các list boxes từ mỗi augmentation
        all_scores: List các list scores tương ứng
        all_class_ids: List các list class IDs tương ứng
        iou_threshold: Ngưỡng IoU để xác định 2 box overlap
    
    Returns:
        final_boxes, final_scores, final_class_ids
    """
    if not all_boxes:
        return [], [], []
    
    # Gom tất cả detections lại
    combined_boxes = []
    combined_scores = []
    combined_class_ids = []
    
    for boxes, scores, cids in zip(all_boxes, all_scores, all_class_ids):
        combined_boxes.extend(boxes)
        combined_scores.extend(scores)
        combined_class_ids.extend(cids)
    
    if not combined_boxes:
        return [], [], []
    
    # NMS để loại bỏ duplicates - tăng score_threshold để giảm false positive
    indices = cv2.dnn.NMSBoxes(
        combined_boxes,
        combined_scores,
        score_threshold=0.20,  # Tăng lên để lọc bớt detections yếu
        nms_threshold=iou_threshold
    )
    
    if len(indices) == 0:
        return [], [], []
    
    # Apply class-based priority với điều kiện score
    # Chỉ ưu tiên DEFECT hơn OK khi DEFECT có score cao hơn đáng kể
    final_boxes = []
    final_scores = []
    final_class_ids = []
    
    # ========================================================================
    # NGƯỠNG ƯU TIÊN DEFECT
    # ========================================================================
    # Defect chỉ được ưu tiên hơn OK khi score cao hơn ít nhất ngưỡng này
    # Giá trị 0.15 nghĩa là:
    #   - Nếu OK score = 0.50, defect cần score > 0.65 mới được chọn
    #   - Nếu defect score = 0.40, OK score chỉ cần > 0.25 là thắng
    # Mục đích: Giảm false positive - ốc tốt bị nhận nhầm là lỗi
    DEFECT_PRIORITY_THRESHOLD = 0.15
    
    for i in indices.flatten():
        box = combined_boxes[i]
        score = combined_scores[i]
        cid = combined_class_ids[i]
        
        # Kiểm tra xem có box nào khác overlapping và có class khác không
        is_best = True
        for j in indices.flatten():
            if i == j:
                continue
            
            other_box = combined_boxes[j]
            other_cid = combined_class_ids[j]
            other_score = combined_scores[j]
            
            # Tính IoU
            iou = compute_iou(box, other_box)
            if iou > iou_threshold:
                # Nếu có overlap
                if cid == 0 and other_cid != 0:
                    # Box hiện tại là OK, box kia là defect
                    # CHỈ bỏ OK nếu defect có score cao hơn đáng kể
                    if other_score > score + DEFECT_PRIORITY_THRESHOLD:
                        is_best = False
                        break
                    # Nếu OK có score cao hơn hoặc tương đương, giữ OK
                elif cid != 0 and other_cid == 0:
                    # Box hiện tại là defect, box kia là OK
                    # Chỉ giữ defect nếu score cao hơn đáng kể
                    if other_score + DEFECT_PRIORITY_THRESHOLD > score:
                        # OK có score tương đương hoặc cao hơn -> bỏ defect
                        is_best = False
                        break
                elif cid == other_cid and other_score > score:
                    # Cùng class, chọn score cao hơn
                    is_best = False
                    break
        
        if is_best:
            final_boxes.append(box)
            final_scores.append(score)
            final_class_ids.append(cid)
    
    return final_boxes, final_scores, final_class_ids

def compute_iou(box1, box2):
    """Tính IoU giữa 2 boxes"""
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Tìm vùng giao
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union

# ============================================================================
# HÀM PREDICT VỚI TEST-TIME AUGMENTATION (TTA)
# ============================================================================
def predict_with_tta(model, frame, conf=0.25, use_tta=True):
    """
    Predict với Test-Time Augmentation (TTA) để tăng độ chính xác.
    
    TTA LÀ GÌ?
    - Thay vì chỉ predict trên ảnh gốc, ta predict trên nhiều phiên bản của ảnh:
      + Ảnh gốc (original)
      + Xoay 90°, 180°, 270° (rotations)
      + Lật ngang (horizontal flip)
    - Sau đó ensemble (gộp) tất cả kết quả lại
    
    TẠI SAO CẦN TTA?
    - Ốc vít có thể nằm ở nhiều hướng khác nhau trên camera
    - Model có thể detect tốt hơn ở một góc nhất định
    - TTA giúp bắt được defect mà ảnh gốc có thể bỏ sót
    
    NHƯỢC ĐIỂM:
    - Chậm hơn ~5 lần (predict 5 ảnh thay vì 1)
    - Có thể tạo ra nhiều detections trùng lặp → cần ensemble tốt
    
    Args:
        model: YOLO model object
        frame: Ảnh đầu vào
        conf: Ngưỡng confidence
        use_tta: True = dùng TTA, False = chỉ dùng ảnh gốc
    
    Returns:
        boxes, scores, class_ids sau khi ensemble
    """
    # Tiền xử lý ảnh (CLAHE + bilateral filter)
    processed_frame = preprocess_frame(frame)
    h, w = processed_frame.shape[:2]
    
    # Lists để lưu kết quả từ mỗi augmentation
    all_boxes = []
    all_scores = []
    all_class_ids = []
    
    # ========================================================================
    # AUGMENTATION 1: ẢNH GỐC (Original)
    # ========================================================================
    # Predict trên ảnh gốc với ngưỡng confidence đầy đủ
    results = model.predict(source=processed_frame, conf=conf, verbose=False, stream=False)
    boxes, scores, cids = extract_predictions(results)
    
    # Filter detections: loại bỏ box không hợp lệ (quá nhỏ, quá lớn, etc.)
    boxes, scores, cids = filter_detections(
        boxes, scores, cids,
        frame_shape=frame.shape,
        min_conf=conf,
        min_area=1,           # Diện tích tối thiểu (pixels)
        max_area_ratio=0.99,  # Tỉ lệ diện tích tối đa so với frame
        debug=False
    )
    all_boxes.append(boxes)
    all_scores.append(scores)
    all_class_ids.append(cids)
    
    if use_tta:
        # ====================================================================
        # AUGMENTATION 2: XOAY ẢNH (Rotations)
        # ====================================================================
        # Xoay ảnh 90°, 180°, 270° để bắt ốc ở các hướng khác nhau
        # Dùng confidence thấp hơn (conf * 0.8) vì rotations có thể làm
        # giảm chất lượng detection
        for angle in [90, 180, 270]:
            # Xoay ảnh và lấy ma trận biến đổi M
            rotated, M = rotate_image(processed_frame, angle)
            
            # Predict trên ảnh đã xoay với ngưỡng thấp hơn 20%
            results = model.predict(source=rotated, conf=conf * 0.8, verbose=False, stream=False)
            boxes, scores, cids = extract_predictions(results)
            
            # QUAN TRỌNG: Chuyển đổi tọa độ box từ ảnh xoay về ảnh gốc
            # Vì model detect trên ảnh xoay, box cũng ở tọa độ xoay
            # Cần đảo ngược phép xoay để box khớp với ảnh gốc
            boxes = rotate_boxes_back(boxes, M, frame.shape)
            
            # Filter các detection không hợp lệ
            boxes, scores, cids = filter_detections(
                boxes, scores, cids,
                frame_shape=frame.shape,
                min_conf=conf * 0.8,
                min_area=1,
                max_area_ratio=0.99,
                debug=False
            )
            all_boxes.append(boxes)
            all_scores.append(scores)
            all_class_ids.append(cids)
        
        # ====================================================================
        # AUGMENTATION 3: LẬT NGANG (Horizontal Flip)
        # ====================================================================
        # Lật ảnh theo chiều ngang để bắt defect có thể chỉ thấy rõ từ 1 phía
        # Dùng confidence thấp hơn một chút (conf * 0.9)
        flipped = cv2.flip(processed_frame, 1)  # 1 = horizontal flip
        results = model.predict(source=flipped, conf=conf * 0.9, verbose=False, stream=False)
        boxes, scores, cids = extract_predictions(results)
        
        # Chuyển đổi tọa độ box từ ảnh flip về ảnh gốc
        # x_new = image_width - x_old (đảo ngược trục x)
        boxes = flip_boxes(boxes, w, 'horizontal')
        
        # Filter các detection không hợp lệ
        boxes, scores, cids = filter_detections(
            boxes, scores, cids,
            frame_shape=frame.shape,
            min_conf=conf * 0.9,
            min_area=1,
            max_area_ratio=0.99,
            debug=False
        )
        all_boxes.append(boxes)
        all_scores.append(scores)
        all_class_ids.append(cids)
    
    # ========================================================================
    # ENSEMBLE - GỘP TẤT CẢ KẾT QUẢ
    # ========================================================================
    # Gộp kết quả từ tất cả augmentations (original + rotations + flip)
    # Loại bỏ detections trùng lặp và xử lý conflict OK vs DEFECT
    # iou_threshold=0.5: 2 box overlap >= 50% được coi là trùng nhau
    final_boxes, final_scores, final_class_ids = ensemble_detections(
        all_boxes, all_scores, all_class_ids, iou_threshold=0.5
    )
    
    return final_boxes, final_scores, final_class_ids

def extract_predictions(results):
    """Extract boxes, scores, class_ids from YOLO results"""
    if isinstance(results, list):
        res = results[0]
    else:
        res = results
    
    boxes = []
    scores = []
    class_ids = []
    
    try:
        for box in getattr(res, "boxes").xyxy.cpu().numpy():
            boxes.append(box.tolist())
        for score in getattr(res, "boxes").conf.cpu().numpy():
            scores.append(float(score))
        for cid in getattr(res, "boxes").cls.cpu().numpy():
            class_ids.append(int(cid))
    except Exception:
        boxes, scores, class_ids = [], [], []
    
    return boxes, scores, class_ids

# ============================================================================
# HÀM CHÍNH - PREDICT FRAME
# ============================================================================
def predict_frame(model, frame, conf=0.25, use_tta=True):
    """
    Hàm chính để predict và annotate ảnh.
    Đây là hàm được gọi từ app.py cho mỗi frame webcam/upload.
    
    LUỒNG XỬ LÝ:
    1. Gọi predict_with_tta() để lấy detections
    2. Vẽ bounding boxes lên ảnh với màu sắc tùy theo class:
       - Màu xanh lá: OK (class 0)
       - Màu đỏ: Defect (class 1-5)
    3. Trả về ảnh đã annotate + thông tin detections
    
    Args:
        model: YOLO model object
        frame: Ảnh đầu vào (từ webcam hoặc upload)
        conf: Ngưỡng confidence (mặc định 0.25)
        use_tta: Sử dụng Test-Time Augmentation hay không
                 - True: Chậm hơn nhưng chính xác hơn (khuyến nghị)
                 - False: Nhanh hơn, phù hợp real-time không cần độ chính xác cao
    
    Returns:
        annotated: Ảnh đã vẽ bounding boxes
        boxes: List các bounding boxes [x1, y1, x2, y2]
        scores: List các confidence scores
        class_ids: List các class IDs (0=OK, 1-5=defect types)
    """
    # Bước 1: Predict với TTA (hoặc không TTA)
    boxes, scores, class_ids = predict_with_tta(model, frame, conf, use_tta)
    
    # Bước 2: Vẽ bounding boxes lên ảnh gốc
    annotated = frame.copy()  # Copy để không modify ảnh gốc
    annotated = draw_boxes(
        annotated, boxes, scores, class_ids, 
        class_names=_class_names,  # ["OK", "Manipulated Front", ...]
        conf_threshold=conf
    )
    
    return annotated, boxes, scores, class_ids
