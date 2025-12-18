
import cv2
import numpy as np
from ultralytics import YOLO
from utils.visualize import draw_boxes
from validate import filter_detections
from typing import List, Tuple
from collections import defaultdict

_model = None
_class_names = None

def load_model(model_path="best.pt", class_names=None):
    global _model, _class_names
    _class_names = class_names
    if _model is None:
        _model = YOLO(model_path)
    return _model

def preprocess_frame(frame):
    """
    Tăng độ chính xác nhận diện bằng cách cải thiện chất lượng ảnh
    """
    # 1. Histogram equalization - cải thiện contrast
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    processed = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # 2. Slight noise reduction
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

def ensemble_detections(all_boxes, all_scores, all_class_ids, iou_threshold=0.5):
    """
    Gộp các detections từ multiple augmentations sử dụng weighted voting
    Ưu tiên các detections DEFECT hơn OK
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
    
    # NMS để loại bỏ duplicates
    indices = cv2.dnn.NMSBoxes(
        combined_boxes,
        combined_scores,
        score_threshold=0.1,  # Thấp để giữ nhiều candidates
        nms_threshold=iou_threshold
    )
    
    if len(indices) == 0:
        return [], [], []
    
    # Apply class-based priority: DEFECT > OK
    # Nếu cùng vùng có cả OK và DEFECT, ưu tiên DEFECT
    final_boxes = []
    final_scores = []
    final_class_ids = []
    
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
                # Ưu tiên DEFECT (class != 0) hơn OK (class == 0)
                if cid == 0 and other_cid != 0:
                    # Box hiện tại là OK, box kia là defect -> bỏ OK
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

def predict_with_tta(model, frame, conf=0.25, use_tta=True):
    """
    Predict với Test-Time Augmentation để tăng độ chính xác
    Thử nhiều góc xoay và flip để phát hiện defect tốt hơn
    """
    processed_frame = preprocess_frame(frame)
    h, w = processed_frame.shape[:2]
    
    all_boxes = []
    all_scores = []
    all_class_ids = []
    
    # Augmentation 1: Original image
    results = model.predict(source=processed_frame, conf=conf, verbose=False, stream=False)
    boxes, scores, cids = extract_predictions(results)
    boxes, scores, cids = filter_detections(
        boxes, scores, cids,
        frame_shape=frame.shape,
        min_conf=conf,
        min_area=1,
        max_area_ratio=0.99,
        debug=False
    )
    all_boxes.append(boxes)
    all_scores.append(scores)
    all_class_ids.append(cids)
    
    if use_tta:
        # Augmentation 2: Rotate 90 degrees
        for angle in [90, 180, 270]:
            rotated, M = rotate_image(processed_frame, angle)
            results = model.predict(source=rotated, conf=conf * 0.8, verbose=False, stream=False)
            boxes, scores, cids = extract_predictions(results)
            
            # Rotate boxes back to original orientation
            boxes = rotate_boxes_back(boxes, M, frame.shape)
            
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
        
        # Augmentation 3: Horizontal flip
        flipped = cv2.flip(processed_frame, 1)
        results = model.predict(source=flipped, conf=conf * 0.9, verbose=False, stream=False)
        boxes, scores, cids = extract_predictions(results)
        
        # Flip boxes back
        boxes = flip_boxes(boxes, w, 'horizontal')
        
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
    
    # Ensemble all predictions
    final_boxes, final_scores, final_class_ids = ensemble_detections(
        all_boxes, all_scores, all_class_ids, iou_threshold=0.4
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

def predict_frame(model, frame, conf=0.25, use_tta=True):
    """
    Main prediction function với TTA support
    use_tta: True = sử dụng Test-Time Augmentation (chậm hơn nhưng chính xác hơn)
            False = chỉ dùng ảnh gốc (nhanh hơn)
    """
    boxes, scores, class_ids = predict_with_tta(model, frame, conf, use_tta)
    
    annotated = frame.copy()
    annotated = draw_boxes(annotated, boxes, scores, class_ids, class_names=_class_names, conf_threshold=conf)
    return annotated, boxes, scores, class_ids
