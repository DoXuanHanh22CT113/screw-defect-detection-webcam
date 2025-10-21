# 🔧 Validation & False Detection Guide

## 📌 Vấn đề

Model có thể nhận diện sai - ví dụ: nhận diện người hay vật thể khác là ốc vít.

## ✅ Giải pháp đã áp dụng

### 1. **Tăng Confidence Threshold**
- Default: 0.35 → Thay đổi thành: 0.65
- Bạn vẫn có thể điều chỉnh trên UI (slider từ 0.1 đến 0.9)

### 2. **Thêm Validation Rules**
File `validate.py` kiểm tra:

| Quy tắc | Mục đích |
|--------|---------|
| **Min Area (100px²)** | Ốc vít phải đủ lớn để nhìn thấy |
| **Max Area Ratio (0.3)** | Ốc vít không được quá 30% frame (loại bỏ cảnh toàn cơ thể người) |
| **Aspect Ratio (0.3-3.0)** | Ốc vít thường gần hình tròn, không quá dài/cao |

### 3. **Filter Detections**
`detect.py` tự động lọc kết quả trước khi hiển thị

## ⚙️ Cách điều chỉnh tham số

### Nếu vẫn nhận diện sai quá nhiều:

**Tăng min_area** (trong `detect.py`):
```python
min_area=200,  # Thay từ 100 → 200 (ốc vít phải lớn hơn)
```

**Giảm max_area_ratio** (trong `detect.py`):
```python
max_area_ratio=0.2,  # Thay từ 0.3 → 0.2 (ốc vít phải nhỏ hơn)
```

**Tăng min_conf** (trực tiếp trên UI):
- Kéo slider "Confidence threshold" lên cao hơn 0.65

### Nếu bỏ sót ốc vít thực:

**Giảm min_area**:
```python
min_area=50,  # Thay từ 100 → 50 (chấp nhận ốc vít nhỏ hơn)
```

**Tăng max_area_ratio**:
```python
max_area_ratio=0.4,  # Thay từ 0.3 → 0.4 (chấp nhận ốc vít lớn hơn)
```

**Giảm min_conf** trên UI

## 📊 So sánh Before/After

| Scenario | Before | After |
|----------|--------|-------|
| **Nhận diện người** | ✅ Nhận diện | ❌ Bỏ qua |
| **Nhận diện ốc vít nhỏ** | ✅ Nhận diện | ⚠️ Tùy min_area |
| **Nhận diện ốc vít rõ ràng** | ✅ Nhận diện | ✅ Nhận diện |

## 🧪 Cách test

1. Chạy app: `streamlit run app.py`
2. Point camera vào người → Không nên nhận diện (nếu frame lớn)
3. Point camera vào ốc vít → Phải nhận diện
4. Điều chỉnh slider Confidence Threshold nếu cần

## 🔍 Debug Info

Để xem chi tiết detection (kích thước bbox, confidence, v.v):

```python
# Thêm vào app.py trong vòng lặp
for i, (box, score) in enumerate(zip(boxes, scores)):
    x1, y1, x2, y2 = box
    area = (x2-x1) * (y2-y1)
    print(f"Detection {i}: conf={score:.2f}, area={area:.0f}px²")
```

## 📝 Các file liên quan

- `validate.py` - Logic validation
- `detect.py` - Gọi filter_detections()
- `app.py` - UI settings

## 💡 Tips

1. **Nếu vẫn sai**: Train model mới với dataset cụ thể
2. **Nếu quá chặt**: Giảm confidence threshold
3. **Nếu quá lỏng**: Tăng min_area hoặc giảm max_area_ratio