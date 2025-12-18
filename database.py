import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
from datetime import datetime, timedelta
import os

# Khởi tạo Firebase
def init_firebase():
    """Khởi tạo kết nối Firebase"""
    try:
        # Kiểm tra xem Firebase đã được khởi tạo chưa
        firebase_admin.get_app()
    except ValueError:
        # Firebase chưa được khởi tạo
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(
            cred,
            {
                'databaseURL': 'https://phattriendungdung-default-rtdb.asia-southeast1.firebasedatabase.app'
            }
        )

# Alias để tương thích với mã cũ
def init_db():
    """Khởi tạo database với Firebase"""
    init_firebase()

def save_detection(image_path, defect_detected, num_defects, confidence_scores, class_ids, boxes):
    """Lưu dữ liệu nhận diện vào Firebase"""
    init_firebase()
    
    ref = db.reference('detections')
    
    detection_data = {
        'timestamp': datetime.now().isoformat(),
        'image_path': image_path,
        'defect_detected': defect_detected,
        'num_defects': num_defects,
        'confidence_scores': confidence_scores,
        'class_ids': class_ids,
        'boxes': boxes
    }
    
    # Thêm dữ liệu mới vào Firebase (tự động tạo ID)
    ref.push(detection_data)

def get_all_detections():
    """Lấy tất cả dữ liệu nhận diện từ Firebase"""
    init_firebase()
    
    try:
        ref = db.reference('detections')
        data = ref.get()
        
        if not data:
            return []
        
        # Chuyển đổi dữ liệu từ Firebase về dạng tuple tương thích
        rows = []
        if isinstance(data, dict):
            for key, value in sorted(data.items(), key=lambda x: x[1].get('timestamp', ''), reverse=True):
                rows.append((
                    key,  # ID
                    value.get('timestamp'),
                    value.get('image_path'),
                    1 if value.get('defect_detected') else 0,  # Chuyển boolean thành 0/1
                    value.get('num_defects'),
                    json.dumps(value.get('confidence_scores', [])),
                    json.dumps(value.get('class_ids', [])),
                    json.dumps(value.get('boxes', []))
                ))
        
        return rows
    except Exception as e:
        print(f"Error getting detections: {e}")
        return []

def get_detection_stats():
    """Lấy thống kê nhận diện từ Firebase"""
    init_firebase()
    
    try:
        ref = db.reference('detections')
        data = ref.get()
        
        if not data:
            return []
        
        # Tính toán thống kê
        defect_count = 0
        ok_count = 0
        
        if isinstance(data, dict):
            for value in data.values():
                if value.get('defect_detected'):
                    defect_count += 1
                else:
                    ok_count += 1
        
        stats = []
        if ok_count > 0:
            stats.append((0, ok_count))  # 0 = No defects
        if defect_count > 0:
            stats.append((1, defect_count))  # 1 = Defects detected
        
        return stats
    except Exception as e:
        print(f"Error getting stats: {e}")
        return []

def delete_old_detections(days=7):
    """Xóa dữ liệu cũ hơn N ngày từ Firebase"""
    init_firebase()
    
    ref = db.reference('detections')
    data = ref.get()
    
    if not data:
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    if isinstance(data, dict):
        for key, value in data.items():
            try:
                timestamp_str = value.get('timestamp', '')
                detection_date = datetime.fromisoformat(timestamp_str)
                
                if detection_date < cutoff_date:
                    ref.child(key).delete()
            except (ValueError, TypeError):
                # Bỏ qua các bản ghi có timestamp không hợp lệ
                pass

def delete_detection(detection_id):
    """Xóa một detection cụ thể theo ID"""
    init_firebase()
    
    ref = db.reference('detections')
    ref.child(detection_id).delete()
