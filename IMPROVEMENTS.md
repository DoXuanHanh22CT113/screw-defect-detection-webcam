# 🔧 Cải Tiến Phát Hiện Khuyết Tật Ốc

## Các vấn đề đã sửa

### ❌ Vấn đề cũ:
- Model nhận diện ốc lỗi thành OK bất kể góc xoay
- Không ổn định với các điều kiện ánh sáng khác nhau
- Khung bounding box quá nhỏ, khó nhìn thấy defect

### ✅ Giải pháp mới:

## 1. **Test-Time Augmentation (TTA)** 🔄

TTA là kỹ thuật phát hiện ảnh ở nhiều góc độ và orientation khác nhau để tăng độ chính xác:

- **Xoay 0°**: Ảnh gốc
- **Xoay 90°**: Phát hiện ốc nằm ngang
- **Xoay 180°**: Phát hiện ốc ngược
- **Xoay 270°**: Phát hiện ốc nằm ngang (hướng khác)
- **Flip ngang**: Phát hiện ốc bị lật

Sau đó **ensemble** tất cả kết quả với ưu tiên:
- **DEFECT > OK**: Nếu cùng vùng có cả OK và DEFECT, chọn DEFECT
- **Score cao hơn**: Trong cùng class, chọn detection có confidence cao hơn

### Cách sử dụng:
```python
# Bật TTA (chính xác hơn, chậm hơn)
annotated, boxes, scores, cids = predict_frame(model, frame, conf=0.30, use_tta=True)

# Tắt TTA (nhanh hơn, kém chính xác hơn)
annotated, boxes, scores, cids = predict_frame(model, frame, conf=0.30, use_tta=False)
```

## 2. **Điều Chỉnh Confidence Threshold** 📊

Đã cập nhật ngưỡng confidence để ưu tiên phát hiện defect:

| Class | Tên | Offset | Mục đích |
|-------|-----|--------|----------|
| 0 | OK | **+0.25** | Yêu cầu RẤT CAO để tránh nhận nhầm ốc lỗi thành OK |
| 1 | Manipulated Front | **-0.25** | Giảm threshold để dễ phát hiện |
| 2 | Scratch Head | **-0.25** | Giảm threshold (khó detect) |
| 3 | Scratch Neck | **-0.25** | Giảm threshold (khó detect) |
| 4 | Thread Side | **-0.25** | Giảm threshold (khó detect) |
| 5 | Thread Top | **-0.25** | Giảm threshold (khó detect) |

**CONFIDENCE_MIN** giảm xuống `0.02` để bắt được nhiều defect hơn.

## 3. **Cải Thiện Visualization** 🎨

### Trước:
- Bounding box **thu nhỏ 50%**
- Đường viền mỏng (2px)
- Font nhỏ, khó đọc

### Sau:
- **Khung FULL SIZE** - không thu nhỏ
- Đường viền DÀY **4px** thay vì 2px
- **Outer glow** effect màu tím để nổi bật
- Font size **0.8** (tăng từ 0.6)
- Font thickness **2** (tăng từ 1)
- Điểm tâm TO HƠN (8px thay vì 5px) + viền outer (10px)
- Label tự động đặt ở dưới nếu không đủ chỗ phía trên

## 4. **Cải Tiến Preprocessing** 🖼️

- **CLAHE** (Contrast Limited Adaptive Histogram Equalization) để cải thiện contrast
- **Bilateral Filter** để giảm noise nhưng giữ được edge

## Cách Chạy

### 1. Webcam Real-time:
```bash
streamlit run app.py
```

**Cài đặt trong sidebar:**
- 🎚️ **Độ tin cậy**: Điều chỉnh 0.15-0.95 (khuyến nghị: 0.30)
- 🔄 **Test-Time Augmentation**: BẬT để phát hiện tốt nhất
- 💾 **Tự động lưu khiếm khuyết**: BẬT để lưu tự động khi phát hiện lỗi

### 2. Video Analysis:
```bash
streamlit run pages/Video_Detection.py
```

## Performance

| Mode | TTA | FPS (ước tính) | Độ chính xác |
|------|-----|----------------|--------------|
| Fast | ❌ OFF | ~15-20 FPS | Trung bình |
| Accurate | ✅ ON | ~3-5 FPS | Cao nhất |

**Khuyến nghị:**
- **Webcam real-time**: Tắt TTA nếu cần FPS cao, bật TTA nếu ưu tiên độ chính xác
- **Video/Image upload**: Luôn bật TTA để có kết quả tốt nhất

## Kiểm Tra Kết Quả

1. Upload ảnh ốc với các góc quay khác nhau (0°, 90°, 180°, 270°)
2. Kiểm tra với các điều kiện ánh sáng khác nhau (sáng, tối, có bóng)
3. So sánh kết quả với TTA ON vs OFF

## Technical Details

### Ensemble Strategy:
```python
# Ưu tiên DEFECT hơn OK
if cid == 0 and other_cid != 0:  # Box hiện tại là OK, box kia là defect
    is_best = False  # Bỏ OK, giữ DEFECT
```

### Box Transformation:
- Rotation: Sử dụng `cv2.getRotationMatrix2D` và inverse transform để map boxes về ảnh gốc
- Flip: Mirror x-coordinates theo width

## Changelog

### Version 2.0 (2025-12-18)
- ✅ Thêm Test-Time Augmentation
- ✅ Điều chỉnh confidence thresholds
- ✅ Cải thiện visualization (khung to, rõ ràng hơn)
- ✅ Ensemble predictions với priority: DEFECT > OK
- ✅ Giảm ngưỡng confidence minimum xuống 0.02

---

**Lưu ý**: TTA làm tăng thời gian xử lý ~5x nhưng cải thiện đáng kể độ chính xác, đặc biệt với các góc xoay khác nhau và điều kiện ánh sáng thay đổi.
