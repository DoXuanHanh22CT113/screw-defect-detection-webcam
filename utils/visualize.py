
import cv2
import numpy as np

def draw_boxes(frame, boxes, scores, class_ids, class_names=None, conf_threshold=0.25):
    h, w = frame.shape[:2]
    for box, score, cid in zip(boxes, scores, class_ids):
        x1, y1, x2, y2 = [int(v) for v in box]
        label = str(cid)
        if class_names and cid < len(class_names):
            label = class_names[cid]
        text = f"{label} {score:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw, y1), (0,255,0), -1)
        cv2.putText(frame, text, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
    return frame
