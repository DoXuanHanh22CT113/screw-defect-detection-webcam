#!/usr/bin/env python3
"""
Simple webcam test - just try to capture 1 frame
"""
import cv2

print("🎥 Testing webcam access...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ KHÔNG THỂ MỞ WEBCAM!")
    print("   Kiểm tra:")
    print("   1. Webcam có kết nối không?")
    print("   2. Có app nào khác dùng webcam không?")
    print("   3. Driver camera có lỗi không?")
    exit(1)

print("✅ Webcam opened successfully!")

ret, frame = cap.read()
if not ret:
    print("❌ Không thể đọc frame từ webcam")
    cap.release()
    exit(1)

print(f"✅ Đã capture frame: {frame.shape}")

# Test detection
from detect import load_model, predict_frame

print("\n📦 Loading model...")
model = load_model("best.pt")

print("🔍 Testing detection...")
annotated, boxes, scores, class_ids = predict_frame(model, frame, conf=0.25)

print(f"\n✅ KẾT QUẢ:")
print(f"   - Detections: {len(boxes)} boxes")
if len(boxes) > 0:
    print(f"   - Classes: {class_ids}")
    print(f"   - Scores: {[f'{s:.2f}' for s in scores]}")
else:
    print("   - KHÔNG CÓ DETECTION!")

cap.release()
print("\n✅ Test hoàn thành!")