import streamlit as st
import cv2
import time
import os
import numpy as np
from detect import load_model, predict_frame
from database import init_db, save_detection, get_detection_stats
from styles import apply_premium_theme

st.set_page_config(page_title="Phát hiện khuyết tật ốc - Webcam", layout="wide", initial_sidebar_state="expanded")

# Apply premium theme
apply_premium_theme()

# Enhanced Header with Icon
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <div style="font-size: 4rem; margin-bottom: 10px;">🔧</div>
</div>
""", unsafe_allow_html=True)

st.title("🔍 SCREW DEFECT DETECTOR")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(157, 78, 221, 0.15) 0%, rgba(0, 212, 255, 0.1) 100%);
            padding: 20px 30px; border-radius: 16px; border: 1px solid rgba(157, 78, 221, 0.4); 
            margin-bottom: 30px; backdrop-filter: blur(10px); text-align: center;">
    <p style="color: #E0E7FF; margin: 0; font-size: 16px; font-weight: 500; line-height: 1.8;">
    <span class="feature-tag">📹 Real-time Detection</span>
    <span class="feature-tag">🎯 AI-Powered</span>
    <span class="feature-tag">💾 Auto Save</span>
    <span class="feature-tag">🔬 High Accuracy</span>
    </p>
</div>
""", unsafe_allow_html=True)


# Khởi tạo database
init_db()

model_path = "best.pt"

# Class names mapping (6 classes từ model mới)
# 0=ok, 1=manipulated_front, 2=scratch_head, 3=scratch_neck, 4=thread_side, 5=thread_top
CLASS_NAMES = ["OK", "Manipulated Front", "Scratch Head", "Scratch Neck", "Thread Side", "Thread Top"]
DEFECT_CLASSES = {1, 2, 3, 4, 5}

# Sidebar settings
with st.sidebar:
    st.markdown("### ⚙️ Cài đặt")
    
    CONF_THRESHOLD = st.slider(
        "Độ tin cậy",
        min_value=0.15, max_value=0.95, value=0.30, step=0.01,
        help="Ngưỡng phát hiện (thấp = nhạy hơn, cao = chặt hơn)"
    )
    
    USE_TTA = st.checkbox(
        "🔄 Test-Time Augmentation",
        value=True,
        help="Xoay ảnh nhiều góc độ để phát hiện chính xác hơn (chậm hơn nhưng tốt hơn)"
    )
    
    AUTO_CAPTURE = st.checkbox(
        "Tự động lưu khuyết tật",
        value=True,
        help="Lưu frame khi phát hiện"
    )
    
    # Camera selection
    st.markdown("### 📷 Chọn Camera")
    CAMERA_OPTIONS = {
        "Laptop Webcam (0)": 0,
        "USB Camera (1)": 1,
        "USB Camera (2)": 2,
    }
    selected_camera = st.selectbox(
        "Camera",
        options=list(CAMERA_OPTIONS.keys()),
        index=0,
        help="Chọn camera để sử dụng"
    )
    CAMERA_INDEX = CAMERA_OPTIONS[selected_camera]
    
    st.markdown("---")

    # Image uploader in sidebar - Multiple files
    st.markdown("### 📁 Upload ảnh để nhận diện")
    uploaded_files = st.file_uploader(
        "Kéo/thả ảnh ở đây hoặc chọn tệp", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True,
        help="Có thể chọn nhiều ảnh cùng lúc"
    )
    if uploaded_files:
        st.session_state["uploaded_files"] = uploaded_files
    elif "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []

save_dir = "outputs"
os.makedirs(save_dir, exist_ok=True)

@st.cache_resource
def get_model(path):
    return load_model(path, class_names=CLASS_NAMES)

model = get_model(model_path)

# Control buttons
st.markdown("### ▶️ Điều khiển")
col1, col2, col3 = st.columns(3, gap="small")
with col1:
    start = st.button("▶", use_container_width=True, help="Bắt đầu")
with col2:
    stop = st.button("⏹", use_container_width=True, help="Dừng")
with col3:
    capture = st.button("📸", use_container_width=True, help="Chụp")

st.markdown("---")

frame_placeholder = st.empty()
info_placeholder = st.empty()
result_placeholder = st.empty()  # nơi hiển thị kết quả OK/LỖI

# Session state
if "running" not in st.session_state:
    st.session_state["running"] = False
if "capture" not in st.session_state:
    st.session_state["capture"] = False
if "last_defect_time" not in st.session_state:
    st.session_state["last_defect_time"] = 0
if "auto_capture_count" not in st.session_state:
    st.session_state["auto_capture_count"] = 0

# Start/stop logic
if start:
    st.session_state["running"] = True
if stop:
    st.session_state["running"] = False
if capture:
    st.session_state["capture"] = True

# Webcam loop
if st.session_state["running"]:
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        info_placeholder.error("🚫 Không thể mở webcam. Kiểm tra quyền truy cập và chỉ số camera.")
        st.session_state["running"] = False
    else:
        info_placeholder.info("✅ Webcam đang chạy. Nhấp vào '📸 Chụp khung hình hiện tại' để lưu và phân tích hình ảnh.")
        while st.session_state["running"]:
            ret, frame = cap.read()
            if not ret:
                info_placeholder.error("⚠️ Không thể đọc khung hình từ webcam.")
                break

            annotated, boxes, scores, cids = predict_frame(model, frame, conf=CONF_THRESHOLD, use_tta=USE_TTA)
            frame_placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                                    channels="RGB", use_container_width=True)

            # Hiển thị kết quả nhận diện real-time
            # Class 0 = OK, Classes 1-5 = defect types
            defect_detected = any(cid in DEFECT_CLASSES for cid in cids)
            if defect_detected:
                result_placeholder.error("❌ Phát hiện khuyết tật ốc!")
            else:
                result_placeholder.success("✅ Vít OK — Không phát hiện khuyết tật.")

            # ========== AUTO-CAPTURE Logic ==========
            current_time = time.time()
            should_auto_capture = False
            
            if defect_detected and AUTO_CAPTURE:
                # Auto-capture nếu đã cách defect cuối cùng >= 2 giây (tránh spam)
                if current_time - st.session_state["last_defect_time"] >= 2:
                    should_auto_capture = True
                    st.session_state["last_defect_time"] = current_time

            # Nếu bấm chụp thủ công hoặc auto-capture
            if st.session_state["capture"] or should_auto_capture:
                timestamp = int(time.time() * 1000)  # Sử dụng milliseconds để tránh trùng lặp
                fname = os.path.join(save_dir, f"capture_{timestamp}.jpg")
                cv2.imwrite(fname, annotated)
                
                # Lưu vào database
                num_defects = sum(1 for cid in cids if cid in DEFECT_CLASSES)  # Count only defects
                save_detection(
                    image_path=fname,
                    defect_detected=defect_detected,
                    num_defects=num_defects,
                    confidence_scores=scores,
                    class_ids=cids,
                    boxes=boxes
                )
                
                if should_auto_capture:
                    st.session_state["auto_capture_count"] += 1
                    info_placeholder.warning(
                        f"🔴 Tự động chụp! Khuyết tật #{st.session_state['auto_capture_count']} | 💾 {fname}"
                    )
                else:
                    info_placeholder.success(f"💾 Đã lưu: {fname} | ✅ Cơ sở dữ liệu đã cập nhật")
                
                st.session_state["capture"] = False

            time.sleep(0.05)  # giảm tốc độ refresh → tránh lỗi removeChild

        cap.release()
        info_placeholder.info("🟡 Webcam đã dừng.")
else:
    frame_placeholder.info("🛑 Webcam đã dừng. Nhấp vào '▶ Bắt đầu webcam' để bắt đầu.")

# --- Process uploaded images when webcam not running ---

# --- Block xử lý nhiều ảnh upload ---

uploaded_files = st.session_state.get("uploaded_files", [])
if uploaded_files and not st.session_state["running"]:
    st.markdown("### 🖼️ Kết quả nhận diện ảnh")
    
    # Nút xóa tất cả
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.info(f"📸 Đã upload {len(uploaded_files)} ảnh")
    with col_header2:
        if st.button("🗑️ Xóa tất cả", use_container_width=True):
            st.session_state["uploaded_files"] = []
            st.rerun()
    
    # Hiển thị ảnh dạng grid (3 cột)
    cols = st.columns(3)
    
    total_ok = 0
    total_defect = 0
    files_to_remove = []
    
    for idx, uploaded_file in enumerate(uploaded_files):
        col = cols[idx % 3]
        
        with col:
            # Đọc và xử lý từng ảnh
            file_bytes = uploaded_file.read()
            uploaded_file.seek(0)  # Reset để có thể đọc lại nếu cần
            
            if file_bytes:
                np_arr = np.frombuffer(file_bytes, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    # Nhận diện
                    annotated, boxes, scores, cids = predict_frame(model, img, conf=CONF_THRESHOLD, use_tta=USE_TTA)
                    
                    # Hiển thị ảnh đã annotate
                    st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), 
                             caption=uploaded_file.name, 
                             use_container_width=True)
                    
                    # Kết quả và nút xóa
                    result_col, delete_col = st.columns([2, 1])
                    
                    defect_detected = any(cid in DEFECT_CLASSES for cid in cids)
                    
                    # Lưu ảnh vào thư mục outputs
                    timestamp = int(time.time() * 1000)
                    safe_name = uploaded_file.name.replace(" ", "_")
                    fname = os.path.join(save_dir, f"upload_{timestamp}_{safe_name}")
                    cv2.imwrite(fname, annotated)
                    
                    # Lưu vào database
                    num_defects = sum(1 for cid in cids if cid in DEFECT_CLASSES)
                    save_detection(
                        image_path=fname,
                        defect_detected=defect_detected,
                        num_defects=num_defects,
                        confidence_scores=scores,
                        class_ids=cids,
                        boxes=boxes
                    )
                    
                    with result_col:
                        if defect_detected:
                            st.error("❌ Lỗi")
                            total_defect += 1
                        else:
                            st.success("✅ OK")
                            total_ok += 1
                    
                    with delete_col:
                        if st.button("🗑️", key=f"del_{idx}", help=f"Xóa {uploaded_file.name}"):
                            files_to_remove.append(idx)
                else:
                    st.error(f"❌ Không đọc được: {uploaded_file.name}")
    
    # Xử lý xóa file
    if files_to_remove:
        new_files = [f for i, f in enumerate(uploaded_files) if i not in files_to_remove]
        st.session_state["uploaded_files"] = new_files
        st.rerun()
    
    # Tổng kết
    st.markdown("---")
    st.markdown("### 📊 Tổng kết")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📸 Tổng ảnh", len(uploaded_files))
    with col2:
        st.metric("✅ OK", total_ok)
    with col3:
        st.metric("❌ Lỗi", total_defect)

# Hiển thị thống kê database
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Thống kê")
    
    stats = get_detection_stats()
    if stats:
        stat_dict = {status: count for status, count in stats}
        ok_count = stat_dict.get(0, 0)
        defect_count = stat_dict.get(1, 0)
        total = ok_count + defect_count
        
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.metric("✅ OK", ok_count)
        with col2:
            st.metric("❌ Lỗi", defect_count)
        
        if total > 0:
            defect_rate = (defect_count / total * 100)
            st.markdown(f"<div style='text-align: center; color: #1a1a1a; margin-top: 8px;'><b>Tỉ lệ:</b> <span style='color: #FF1744; font-size: 18px;'>{defect_rate:.1f}%</span></div>", unsafe_allow_html=True)
    else:
        st.info("💭 Chưa có dữ liệu")
