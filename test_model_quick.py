#!/usr/bin/env python3
"""
Test nhanh model - không cần interactive
"""

import cv2
import time
from detect import load_model, predict_frame

# Load model
print("📦 Loading model...")
model = load_model("best.pt")

# Test với webcam
print("🎥 Testing with webcam (10 frames)...")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Không thể mở webcam!")
    exit(1)

frame_count = 0
detection_count = 0

for i in range(10):
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Lỗi đọc frame {i}")
        break
    
    frame_count += 1
    
    # Test với confidence thấp
    conf = 0.25
    print(f"\n[Frame {i+1}] Predicting with confidence={conf}...", end="")
    annotated, boxes, scores, class_ids = predict_frame(model, frame, conf=conf)
    
    print(f" → {len(boxes)} detections", end="")
    if len(boxes) > 0:
        detection_count += 1
        print(f" (Classes: {class_ids}, Scores: {[f'{s:.2f}' for s in scores]})")
    else:
        print()
    
    time.sleep(0.5)  # Delay giữa frames

cap.release()

print(f"\n📊 Kết quả test:")
print(f"   Frames: {frame_count}")
print(f"   Frames có detection: {detection_count}")
if frame_count > 0:
    print(f"   Detection rate: {detection_count/frame_count*100:.1f}%")

if detection_count == 0:
    print("\n⚠️ MỢI: Model không detect được gì!")
    print("   Kiểm tra:")
    print("   1. Model file best.pt tồn tại và đúng?")
    print("   2. Ốc lỗi có trong frame không?")
    print("   3. Thử giảm confidence threshold hơn nữa?")