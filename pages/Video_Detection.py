import streamlit as st
import cv2
import tempfile
import os
import time
import numpy as np
from detect import load_model, predict_frame
from database import init_db, save_detection

st.set_page_config(page_title="Phát hiện khiếm khuyết ốc - Video", layout="wide", initial_sidebar_state="expanded")

# Custom CSS - Premium Dark Mode Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-cyan: #00D4FF;
        --primary-purple: #8B5CF6;
        --success-color: #10B981;
        --danger-color: #EF4444;
    }
    
    .main, .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
        background-attachment: fixed !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    
    h2, h3 { color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
    body, p, span, div { color: #e2e8f0; font-family: 'Inter', sans-serif; }
    
    .stButton > button {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 50%, #00D4FF 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6) !important;
    }
    
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(139, 92, 246, 0.2) !important;
    }
    
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 700 !important;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #8B5CF6 0%, #00D4FF 100%) !important;
    }
    
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        background: rgba(30, 41, 59, 0.8) !important;
    }
    
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 12px !important;
        padding: 5px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        border-radius: 8px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎥 Phân tích video — Batch")
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(0, 212, 255, 0.1) 100%);
            padding: 15px 20px; border-radius: 12px; border-left: 4px solid #8B5CF6; margin-bottom: 20px;
            backdrop-filter: blur(10px);">
    <p style="color: #e2e8f0; margin: 0; font-size: 15px; font-weight: 500;">
    📹 Upload • 🎬 Frame-by-frame • 🎯 Auto phát hiện • 💾 Lưu
    </p>
</div>
""")

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
    
    SAVE_DEFECTS = st.checkbox(
        "Tự động lưu khuyết tật",
        value=True,
        help="Lưu frames lỗi vào database"
    )
    
    st.markdown("---")

@st.cache_resource
def get_model(path):
    return load_model(path)

model = get_model(model_path)

# Class names mapping
CLASS_NAMES = {0: "OK", 1: "Manipulated", 2: "Scratch", 3: "Thread"}
DEFECT_CLASSES = {1, 2, 3}

# Video upload
uploaded_video = st.file_uploader("📤 Upload video", type=["mp4", "avi", "mov", "mkv", "flv"])

if uploaded_video is not None:
    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(uploaded_video.read())
        video_path = tmp_file.name
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("🚫 Không thể mở video. Vui lòng kiểm tra định dạng tệp.")
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        st.info(f"✅ {total_frames} frames @ {fps:.1f} FPS")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Extract frames and detect
        frames_data = []
        defect_frames = []
        ok_frames = []
        
        for frame_idx in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run detection
            annotated, boxes, scores, cids = predict_frame(model, frame, conf=CONF_THRESHOLD)
            
            # Check if defect detected
            has_defect = any(cid in DEFECT_CLASSES for cid in cids)
            
            # Store frame data
            frame_data = {
                "index": frame_idx,
                "original": frame,
                "annotated": annotated,
                "boxes": boxes,
                "scores": scores,
                "class_ids": cids,
                "has_defect": has_defect
            }
            frames_data.append(frame_data)
            
            if has_defect:
                defect_frames.append(frame_data)
            else:
                ok_frames.append(frame_data)
            
            # Update progress
            progress = (frame_idx + 1) / total_frames
            progress_bar.progress(progress)
            status_text.text(f"Frame {frame_idx + 1}/{total_frames}")
        
        cap.release()
        os.unlink(video_path)
        
        progress_bar.empty()
        status_text.empty()
        
        # Summary stats
        st.divider()
        st.markdown("### 📊 Tóm tắt")
        
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            st.metric("📹 Frames", total_frames)
        with col2:
            st.metric("✅ OK", len(ok_frames))
        with col3:
            st.metric("❌ Lỗi", len(defect_frames))
        with col4:
            defect_rate = (len(defect_frames) / total_frames * 100) if total_frames > 0 else 0
            st.metric("Tỉ lệ", f"{defect_rate:.1f}%")
        
        st.divider()
        
        # Tabs for browsing
        tab1, tab2, tab3 = st.tabs(["📹 Tất cả", "❌ Lỗi", "✅ OK"])
        
        # TAB 1: ALL FRAMES
        with tab1:
            if frames_data:
                frame_slider = st.slider("Select frame", 0, len(frames_data) - 1, 0, key="all_frames")
                frame_info = frames_data[frame_slider]
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(cv2.cvtColor(frame_info["annotated"], cv2.COLOR_BGR2RGB), 
                            use_container_width=True)
                
                with col2:
                    st.subheader(f"Frame #{frame_info['index']}")
                    
                    # Status
                    if frame_info["has_defect"]:
                        st.error("❌ DEFECT DETECTED")
                    else:
                        st.success("✅ OK - No Defects")
                    
                    # Detections
                    st.write(f"**Detections:** {len(frame_info['boxes'])}")
                    
                    if frame_info['boxes']:
                        st.write("**Details:**")
                        for i, (box, score, cid) in enumerate(zip(frame_info['boxes'], 
                                                                    frame_info['scores'], 
                                                                    frame_info['class_ids'])):
                            class_name = CLASS_NAMES.get(cid, f"Unknown({cid})")
                            color = "🔴" if cid in DEFECT_CLASSES else "🟢"
                            st.write(f"{i+1}. {color} **{class_name}** - Confidence: {score:.2f}")
                    
                    # Save button
                    if SAVE_DEFECTS and frame_info["has_defect"]:
                        if st.button("💾 Lưu", key=f"save_all_{frame_slider}", use_container_width=True):
                            output_dir = "outputs"
                            os.makedirs(output_dir, exist_ok=True)
                            timestamp = int(time.time() * 1000)
                            fname = os.path.join(output_dir, f"video_frame_{frame_info['index']}_{timestamp}.jpg")
                            cv2.imwrite(fname, frame_info["annotated"])
                            
                            num_defects = sum(1 for cid in frame_info['class_ids'] if cid in DEFECT_CLASSES)
                            save_detection(
                                image_path=fname,
                                defect_detected=True,
                                num_defects=num_defects,
                                confidence_scores=frame_info['scores'],
                                class_ids=frame_info['class_ids'],
                                boxes=frame_info['boxes']
                            )
                            st.success("✅ Đã lưu")
        
        # TAB 2: DEFECT FRAMES
        with tab2:
            if defect_frames:
                frame_slider = st.slider("Select defect frame", 0, len(defect_frames) - 1, 0, key="defect_frames")
                frame_info = defect_frames[frame_slider]
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(cv2.cvtColor(frame_info["annotated"], cv2.COLOR_BGR2RGB), 
                            use_container_width=True)
                
                with col2:
                    st.subheader(f"Defect Frame #{frame_info['index']}")
                    st.error("❌ DEFECT DETECTED")
                    st.write(f"**Detections:** {len(frame_info['boxes'])}")
                    
                    if frame_info['boxes']:
                        st.write("**Defect Details:**")
                        for i, (box, score, cid) in enumerate(zip(frame_info['boxes'], 
                                                                    frame_info['scores'], 
                                                                    frame_info['class_ids'])):
                            if cid in DEFECT_CLASSES:
                                class_name = CLASS_NAMES.get(cid, f"Unknown({cid})")
                                st.write(f"{i+1}. 🔴 **{class_name}** - Confidence: {score:.2f}")
                    
                    # Save button
                    if st.button("💾 Lưu", key=f"save_defect_{frame_slider}", use_container_width=True):
                        output_dir = "outputs"
                        os.makedirs(output_dir, exist_ok=True)
                        timestamp = int(time.time() * 1000)
                        fname = os.path.join(output_dir, f"video_defect_{frame_info['index']}_{timestamp}.jpg")
                        cv2.imwrite(fname, frame_info["annotated"])
                        
                        num_defects = sum(1 for cid in frame_info['class_ids'] if cid in DEFECT_CLASSES)
                        save_detection(
                            image_path=fname,
                            defect_detected=True,
                            num_defects=num_defects,
                            confidence_scores=frame_info['scores'],
                            class_ids=frame_info['class_ids'],
                            boxes=frame_info['boxes']
                        )
                        st.success("✅ Đã lưu")
            else:
                st.info("✅ Không có lỗi")
        
        # TAB 3: OK FRAMES
        with tab3:
            if ok_frames:
                frame_slider = st.slider("Select OK frame", 0, len(ok_frames) - 1, 0, key="ok_frames")
                frame_info = ok_frames[frame_slider]
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(cv2.cvtColor(frame_info["annotated"], cv2.COLOR_BGR2RGB), 
                            use_container_width=True)
                
                with col2:
                    st.subheader(f"OK Frame #{frame_info['index']}")
                    st.success("✅ OK - No Defects")
                    st.write(f"**Detections:** {len(frame_info['boxes'])}")
                    
                    if frame_info['boxes']:
                        st.write("**Details:**")
                        for i, (box, score, cid) in enumerate(zip(frame_info['boxes'], 
                                                                    frame_info['scores'], 
                                                                    frame_info['class_ids'])):
                            class_name = CLASS_NAMES.get(cid, f"Unknown({cid})")
                            st.write(f"{i+1}. 🟢 **{class_name}** - Confidence: {score:.2f}")
            else:
                st.info("❌ Không có OK frames")
        
        st.divider()
        
        # Batch export defects
        if defect_frames:
            st.markdown("### 💾 Lưu hàng loạt")
            if st.button("💾 Lưu tất cả lỗi", use_container_width=True):
                output_dir = "outputs"
                os.makedirs(output_dir, exist_ok=True)
                
                count = 0
                for frame_info in defect_frames:
                    timestamp = int(time.time() * 1000) + count
                    fname = os.path.join(output_dir, f"batch_defect_{frame_info['index']}_{timestamp}.jpg")
                    cv2.imwrite(fname, frame_info["annotated"])
                    
                    num_defects = sum(1 for cid in frame_info['class_ids'] if cid in DEFECT_CLASSES)
                    save_detection(
                        image_path=fname,
                        defect_detected=True,
                        num_defects=num_defects,
                        confidence_scores=frame_info['scores'],
                        class_ids=frame_info['class_ids'],
                        boxes=frame_info['boxes']
                    )
                    count += 1
                
                st.success(f"✅ Đã lưu {count} frame lỗi")
else:
    st.info("📹 Upload video để bắt đầu")