import streamlit as st
import cv2
import time
import os
import numpy as np
from detect import load_model, predict_frame  # đảm bảo detect.py có 2 hàm này
from database import init_db, save_detection, get_detection_stats

st.set_page_config(page_title="Phát hiện khuyết tật ốc - Webcam", layout="wide", initial_sidebar_state="expanded")

# Custom CSS - Dark Mode Theme
st.markdown("""
<style>
    :root {
        --primary-color: #00D4FF;
        --success-color: #00FF88;
        --danger-color: #FF1744;
        --warning-color: #FFB300;
        --bg-dark: #0a0e27;
        --card-dark: #151933;
        --text-light: #e8eef5;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(180deg, #87CEEB 0%, #e0f6ff 30%, #90EE90 70%, #2d8659 100%);
        background-attachment: fixed;
    }
    
    /* Headers */
    h1 {
        color: #0d47a1 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        font-weight: 700 !important;
        margin-bottom: 5px !important;
        margin-top: 0 !important;
    }
    
    h2 {
        color: #1565c0 !important;
        border-bottom: 3px solid #2ecc71;
        padding-bottom: 5px;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    h3 {
        color: #2d8659 !important;
        font-weight: 600 !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    
    /* Text */
    body {
        color: #1a1a1a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3) !important;
        font-size: 14px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.5) !important;
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%) !important;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(240, 248, 255, 0.8) 100%);
        border-left: 4px solid #2ecc71;
        padding: 12px;
        border-radius: 6px;
        margin: 6px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Slider */
    .stSlider {
        padding: 10px 0;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 248, 255, 0.9) 100%);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid #2ecc71 !important;
        background-color: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* Divider */
    hr {
        border: 1px solid rgba(46, 204, 113, 0.3) !important;
        margin: 30px 0 !important;
    }
    
    /* Cards effect */
    .metric {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.08) 0%, rgba(39, 174, 96, 0.08) 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(46, 204, 113, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Phát hiện ốc — Live")
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.15) 0%, rgba(52, 152, 219, 0.1) 100%);
            padding: 12px; border-radius: 6px; border-left: 3px solid #2ecc71; margin-bottom: 15px;">
    <p style="color: #1a1a1a; margin: 0; font-size: 14px;">
    📹 Webcam thời thực • 🎯 Phát hiện khuyết tật • 💾 Tự động lưu
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

    # Image uploader in sidebar
    st.markdown("### 📁 Upload ảnh để nhận diện")
    uploaded_file = st.file_uploader("Kéo/thả ảnh ở đây hoặc chọn tệp", type=["png", "jpg", "jpeg"], accept_multiple_files=False)
    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file
    elif "uploaded_file" not in st.session_state:
        st.session_state["uploaded_file"] = None

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

# --- Process uploaded image when webcam not running ---

# --- Block xử lý ảnh upload (dễ copy/sửa) ---

uploaded = st.session_state.get("uploaded_file", None)
if uploaded and not st.session_state["running"]:
    # Đọc file bytes chỉ 1 lần, lưu vào session_state để dùng lại
    if "uploaded_bytes" not in st.session_state or st.session_state["uploaded_bytes"] is None:
        st.session_state["uploaded_bytes"] = uploaded.read()
    file_bytes = st.session_state["uploaded_bytes"]
    if not file_bytes:
        st.error("❌ File upload bị rỗng hoặc lỗi. Vui lòng chọn lại ảnh.")
    else:
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            st.error("❌ Không thể đọc ảnh đã tải lên.")
        else:
            # Nhận diện ảnh upload
            annotated, boxes, scores, cids = predict_frame(model, img, conf=CONF_THRESHOLD)
            frame_placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
            defect_detected = any(cid != 0 for cid in cids)
            if defect_detected:
                result_placeholder.error("❌ Phát hiện khuyết tật ốc!")
            else:
                result_placeholder.success("✅ Vít OK — Không phát hiện khuyết tật.")

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
