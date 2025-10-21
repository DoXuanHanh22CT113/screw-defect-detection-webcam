#!/usr/bin/env python3
"""
Script test nhanh - kiểm tra model có detect được không
"""

import cv2
import os
from detect import load_model, predict_frame

# Load model
print("📦 Loading model...")
model = load_model("best.pt")

# Test với webcam
print("🎥 Testing with webcam...")
print("Press 'q' to stop, 'c' to capture and analyze")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Không thể mở webcam!")
    exit(1)

capture_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Lỗi đọc frame")
        break
    
    # Test với confidence thấp
    conf = 0.25
    print(f"\n🔍 Predict frame với confidence={conf}")
    annotated, boxes, scores, class_ids = predict_frame(model, frame, conf=conf)
    
    print(f"✅ Kết quả: {len(boxes)} detections")
    if len(boxes) > 0:
        print(f"   Classes: {class_ids}")
        print(f"   Scores: {scores}")
    
    # Hiển thị frame
    cv2.imshow("Test - Phát hiện ốc", annotated)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        capture_count += 1
        fname = f"test_capture_{capture_count}.jpg"
        cv2.imwrite(fname, annotated)
        print(f"💾 Saved: {fname}")

cap.release()
cv2.destroyAllWindows()
print("\n✅ Test hoàn thành!")