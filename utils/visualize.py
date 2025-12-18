
import cv2
import numpy as np

# Màu sắc tươi sáng (BGR format)
COLOR_OK = (255, 255, 0)       # Cyan tươi sáng
COLOR_DEFECT = (0, 165, 255)   # Cam tươi (Orange)
COLOR_TEXT = (255, 255, 255)   # Trắng
COLOR_TEXT_DARK = (0, 0, 0)    # Đen

def draw_boxes(frame, boxes, scores, class_ids, class_names=None, conf_threshold=0.25):
    h, w = frame.shape[:2]
    for box, score, cid in zip(boxes, scores, class_ids):
        x1, y1, x2, y2 = [int(v) for v in box]
        label = str(cid)
        if class_names and cid < len(class_names):
            label = class_names[cid]
        text = f"{label} {score:.2f}"
        
        # Chọn màu dựa trên class (0 = OK, còn lại = defect)
        box_color = COLOR_OK if cid == 0 else COLOR_DEFECT
        text_color = COLOR_TEXT_DARK if cid == 0 else COLOR_TEXT
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw, y1), box_color, -1)
        cv2.putText(frame, text, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1)
        
        # Vẽ điểm đánh dấu cho defect
        if cid != 0:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(frame, (center_x, center_y), 5, box_color, -1)
    return frame
