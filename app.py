import streamlit as st
import cv2
import time
import os
import numpy as np
from detect import load_model, predict_frame  # đảm bảo detect.py có 2 hàm này
from database import init_db, save_detection, get_detection_stats

st.set_page_config(page_title="Phát hiện khuyết tật ốc - Webcam", layout="wide", initial_sidebar_state="expanded")

# Custom CSS - Premium Dark Mode Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-cyan: #00D4FF;
        --primary-purple: #8B5CF6;
        --success-color: #10B981;
        --danger-color: #EF4444;
        --warning-color: #F59E0B;
        --bg-dark: #0f172a;
        --bg-darker: #020617;
        --card-dark: rgba(30, 41, 59, 0.8);
        --border-color: rgba(148, 163, 184, 0.1);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Main container - Dark gradient */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
        background-attachment: fixed !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
    }
    
    /* Headers with gradient text effect */
    h1 {
        background: linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 10px !important;
        text-shadow: none !important;
    }
    
    h2 {
        color: #00D4FF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-bottom: 2px solid rgba(139, 92, 246, 0.5);
        padding-bottom: 8px;
        margin-top: 15px !important;
    }
    
    h3 {
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    /* General text */
    body, p, span, div {
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Glassmorphism Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 50%, #00D4FF 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    /* Sidebar - Glassmorphism */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Metrics with glow effect */
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Slider with gradient track */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #8B5CF6 0%, #00D4FF 100%) !important;
    }
    
    .stSlider > div > div > div {
        background: rgba(148, 163, 184, 0.2) !important;
    }
    
    /* Alert boxes with modern styling */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        background: rgba(30, 41, 59, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    div[data-testid="stNotification"] {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
    }
    
    /* Success message */
    .element-container:has(.stSuccess) {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border-left: 4px solid #10B981 !important;
        border-radius: 8px !important;
    }
    
    /* Error message */
    .element-container:has(.stError) {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border-left: 4px solid #EF4444 !important;
        border-radius: 8px !important;
    }
    
    /* Divider with gradient */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent) !important;
        margin: 25px 0 !important;
    }
    
    /* File uploader */
    .stFileUploader {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 2px dashed rgba(139, 92, 246, 0.4) !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    .stFileUploader:hover {
        border-color: rgba(0, 212, 255, 0.6) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        color: #e2e8f0 !important;
    }
    
    /* Image container with subtle border */
    .stImage {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #8B5CF6 0%, #6366F1 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #A78BFA 0%, #818CF8 100%);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Phát hiện khiếm khuyết ốc — Live")
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(0, 212, 255, 0.1) 100%);
            padding: 15px 20px; border-radius: 12px; border-left: 4px solid #8B5CF6; margin-bottom: 20px;
            backdrop-filter: blur(10px);">
    <p style="color: #e2e8f0; margin: 0; font-size: 15px; font-weight: 500;">
    📹 Webcam thời thực • 🎯 Phát hiện khiếm khuyết • 💾 Tự động lưu • 🔬 AI-Powered
    </p>
</div>
""", unsafe_allow_html=True)

# Khởi tạo database
init_db()

model_path = "best.pt"

# Sidebar settings
with st.sidebar:
    st.markdown("### ⚙️ Cài đặt")
    
    CONF_THRESHOLD = st.slider(
        "Độ tin cậy",
        min_value=0.3, max_value=0.95, value=0.65, step=0.01,
        help="Ngưỡng phát hiện (cao = chặt)"
    )
    
    AUTO_CAPTURE = st.checkbox(
        "Tự động lưu khuyết tật",
        value=True,
        help="Lưu frame khi phát hiện"
    )
    
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
    return load_model(path)

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
    cap = cv2.VideoCapture(0)
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

            annotated, boxes, scores, cids = predict_frame(model, frame, conf=CONF_THRESHOLD)
            frame_placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB),
                                    channels="RGB", use_container_width=True)

            # Hiển thị kết quả nhận diện real-time
            # Class 0 = OK, Classes 1-3 = defect (manipulated, scratch, thread)
            defect_detected = any(cid != 0 for cid in cids)
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
                num_defects = sum(1 for cid in cids if cid != 0)  # Count only defects (non-OK classes)
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
                    annotated, boxes, scores, cids = predict_frame(model, img, conf=CONF_THRESHOLD)
                    
                    # Hiển thị ảnh đã annotate
                    st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), 
                             caption=uploaded_file.name, 
                             use_container_width=True)
                    
                    # Kết quả và nút xóa
                    result_col, delete_col = st.columns([2, 1])
                    
                    defect_detected = any(cid != 0 for cid in cids)
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
