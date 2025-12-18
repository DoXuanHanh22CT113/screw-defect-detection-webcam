
import cv2
import numpy as np

# Màu sắc tươi sáng (BGR format)
COLOR_OK = (0, 255, 0)         # Xanh lá (Green) cho OK
COLOR_DEFECT = (0, 0, 255)     # Đỏ (Red) cho Lỗi
COLOR_TEXT = (255, 255, 255)   # Trắng
COLOR_TEXT_DARK = (0, 0, 0)    # Đen

def draw_boxes(frame, boxes, scores, class_ids, class_names=None, conf_threshold=0.25):
    h, w = frame.shape[:2]
    for box, score, cid in zip(boxes, scores, class_ids):
        # CHỈ VẼ KHUYẾT TẬT - BỎ QUA CLASS OK (cid == 0)
        if cid == 0:
            continue
        
        x1, y1, x2, y2 = [int(v) for v in box]
        label = str(cid)
        if class_names and cid < len(class_names):
            label = class_names[cid]
        text = f"{label} {score:.2f}"
        
        # Màu đỏ cho khuyết tật
        box_color = COLOR_DEFECT
        text_color = COLOR_TEXT
        
        # VẼ KHUNG ĐẦY ĐỦ KÍCH THƯỚC - KHÔNG THU NHỎ
        # Để khung TO và RÕ RÀNG để dễ nhìn thấy defect
        draw_x1 = max(0, x1)
        draw_y1 = max(0, y1)
        draw_x2 = min(w, x2)
        draw_y2 = min(h, y2)
        
        center_x = (draw_x1 + draw_x2) // 2
        center_y = (draw_y1 + draw_y2) // 2
        
        # Vẽ bounding box với đường viền DÀY và RÕ RÀNG (4px thay vì 2px)
        cv2.rectangle(frame, (draw_x1, draw_y1), (draw_x2, draw_y2), box_color, 4)
        
        # Vẽ thêm outer glow effect để nổi bật hơn
        cv2.rectangle(frame, (draw_x1-2, draw_y1-2), (draw_x2+2, draw_y2+2), (128, 0, 128), 1)
        
        # Vẽ label background và text với font size LỚN HƠN
        font_scale = 0.8  # Tăng từ 0.6 lên 0.8
        font_thickness = 2  # Tăng từ 1 lên 2
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        
        # Label background
        label_y1 = draw_y1 - th - 10
        label_y2 = draw_y1
        if label_y1 < 0:  # Nếu không đủ chỗ ở trên, vẽ ở dưới
            label_y1 = draw_y2
            label_y2 = draw_y2 + th + 10
        
        cv2.rectangle(frame, (draw_x1, label_y1), (draw_x1 + tw + 10, label_y2), box_color, -1)
        cv2.putText(frame, text, (draw_x1 + 5, label_y2 - 5), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness)
        
        # Vẽ điểm đánh dấu tâm TO HƠN
        cv2.circle(frame, (center_x, center_y), 8, box_color, -1)
        cv2.circle(frame, (center_x, center_y), 10, box_color, 2)
    return frame
