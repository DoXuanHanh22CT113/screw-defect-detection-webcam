
import cv2
import numpy as np
from ultralytics import YOLO
from utils.visualize import draw_boxes
from validate import filter_detections

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

def predict_frame(model, frame, conf=0.25):
    # Cải thiện ảnh trước khi dự đoán
    processed_frame = preprocess_frame(frame)
    
    results = model.predict(source=processed_frame, conf=conf, verbose=False, stream=False)
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
    
    # Lọc detections để loại bỏ false positives
    # Sử dụng chính confidence score từ app (không giảm xuống)
    boxes, scores, class_ids = filter_detections(
        boxes, scores, class_ids, 
        frame_shape=frame.shape,
        min_conf=conf,  # Dùng confidence từ slider app
        min_area=1,             # Extreme: nhận diện screws rất nhỏ
        max_area_ratio=0.99,    # Cho phép quay gần camera
        debug=True              # Bật debug mode xem model detect gì
    )
    
    # If no boxes after preprocessing+filtering, try a quick fallback on the original frame
    if len(boxes) == 0:
        try:
            img_orig = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results2 = model.predict(source=img_orig, conf=conf, verbose=False, stream=False)
            res2 = results2[0] if isinstance(results2, list) else results2
            boxes2 = []
            scores2 = []
            class_ids2 = []
            for box in getattr(res2, "boxes").xyxy.cpu().numpy():
                boxes2.append(box.tolist())
            for score in getattr(res2, "boxes").conf.cpu().numpy():
                scores2.append(float(score))
            for cid in getattr(res2, "boxes").cls.cpu().numpy():
                class_ids2.append(int(cid))

            boxes2, scores2, class_ids2 = filter_detections(
                boxes2, scores2, class_ids2,
                frame_shape=frame.shape,
                min_conf=conf,
                min_area=1,
                max_area_ratio=0.99,
                debug=False
            )

            if len(boxes2) > 0:
                boxes, scores, class_ids = boxes2, scores2, class_ids2
        except Exception:
            # fallback failed silently; keep original (empty) lists
            pass

    annotated = frame.copy()
    annotated = draw_boxes(annotated, boxes, scores, class_ids, class_names=_class_names, conf_threshold=conf)
    return annotated, boxes, scores, class_ids
