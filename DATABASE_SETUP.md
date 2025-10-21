# Database Setup Guide

## 📋 Tính năng

Các file mới đã được thêm để lưu trữ dữ liệu nhận diện:

### 1. **database.py** - Module database
- Quản lý SQLite database
- Lưu trữ: ảnh, số lượng defect, confidence scores, bbox

### 2. **app.py** - Cập nhật
- Tự động khởi tạo database khi mở ứng dụng
- Lưu dữ liệu khi bấm "Capture"
- Hiển thị thống kê trên sidebar

### 3. **pages/Database_Viewer.py** - Trang xem dữ liệu
- Hiển thị bảng tất cả records
- Thống kê số lượng defect
- Export CSV
- Xóa dữ liệu cũ

## ✅ Yêu cầu

SQLite3 đã được cài sẵn trong Python, không cần setup thêm!

## 🚀 Cách dùng

### 1. Chạy ứng dụng bình thường
```bash
streamlit run app.py
```

### 2. Xem dữ liệu database
- Click vào tab **Database_Viewer** ở sidebar (nếu có)
- Hoặc chạy: `streamlit run pages/Database_Viewer.py`

### 3. Xem thống kê
- Thống kê hiện lên tự động ở sidebar của ứng dụng chính

## 📊 Cấu trúc Database

```
screw_detection.db
├── id (Primary Key)
├── timestamp (Datetime - tự động tạo)
├── image_path (Đường dẫn ảnh)
├── defect_detected (0/1 - có defect hay không)
├── num_defects (số lượng defect tìm thấy)
├── confidence_scores (JSON - độ tin cậy)
├── class_ids (JSON - loại defect)
└── boxes (JSON - tọa độ bbox)
```

## 🔧 Các hàm có sẵn

```python
from database import *

# Khởi tạo database
init_db()

# Lưu dữ liệu
save_detection(image_path, defect_detected, num_defects, confidence_scores, class_ids, boxes)

# Lấy tất cả dữ liệu
get_all_detections()

# Lấy thống kê
get_detection_stats()

# Xóa dữ liệu cũ
delete_old_detections(days=7)
```

## 💾 Dữ liệu sẽ được lưu ở

- **Database**: `screw_detection.db` (trong thư mục project)
- **Ảnh**: `outputs/capture_*.jpg`

## 🐛 Troubleshooting

**Q: Database không được tạo?**
- A: SQLite3 phải được cài sẵn. Kiểm tra bằng: `python -c "import sqlite3; print(sqlite3.version)"`

**Q: Không thấy dữ liệu trong Database_Viewer?**
- A: Hãy chắc chắn rằng bạn đã bấm "Capture" ít nhất 1 lần

**Q: Muốn xóa database hoàn toàn?**
- A: Xóa file `screw_detection.db` và restart ứng dụng

## 📈 Tiếp theo

Bạn có thể:
- Thêm tính năng xuất báo cáo PDF
- Kết nối với server database (PostgreSQL, MySQL)
- Tạo dashboard thống kê chi tiết
- Tích hợp export cloud (Google Drive, AWS S3)