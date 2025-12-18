import streamlit as st
import cv2
import tempfile
import os
import time
import numpy as np
from detect import load_model, predict_frame
from database import init_db, save_detection
from styles import apply_premium_theme

st.set_page_config(page_title="Phát hiện khiếm khuyết ốc - Video", layout="wide", initial_sidebar_state="expanded")

# Apply premium theme
apply_premium_theme()

# Enhanced Header
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <div style="font-size: 4rem; margin-bottom: 10px;">🎥</div>
</div>
""", unsafe_allow_html=True)

st.title("🎥 VIDEO ANALYSIS")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(157, 78, 221, 0.15) 0%, rgba(0, 212, 255, 0.1) 100%);
            padding: 20px 30px; border-radius: 16px; border: 1px solid rgba(157, 78, 221, 0.4); 
            margin-bottom: 30px; backdrop-filter: blur(10px); text-align: center;">
    <p style="color: #E0E7FF; margin: 0; font-size: 16px; font-weight: 500; line-height: 1.8;">
    <span class="feature-tag">📹 Upload Video</span>
    <span class="feature-tag">🎬 Frame Analysis</span>
    <span class="feature-tag">🎯 Auto Detection</span>
    <span class="feature-tag">💾 Batch Save</span>
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
        min_value=0.15, max_value=0.95, value=0.30, step=0.01,
        help="Ngưỡng phát hiện (thấp = nhạy hơn, cao = chặt hơn)"
    )
    
    USE_TTA = st.checkbox(
        "🔄 Test-Time Augmentation",
        value=True,
        help="Xoay ảnh nhiều góc độ để phát hiện chính xác hơn (chậm hơn nhưng tốt hơn)"
    )
    
    SAVE_DEFECTS = st.checkbox(
        "Tự động lưu khiếm khuyết",
        value=True,
        help="Lưu frames lỗi vào database"
    )
    
    st.markdown("---")

@st.cache_resource
def get_model(path):
    return load_model(path)

model = get_model(model_path)

# Class names mapping (6 classes từ model mới)
# 0=ok, 1=manipulated_front, 2=scratch_head, 3=scratch_neck, 4=thread_side, 5=thread_top
CLASS_NAMES = {
    0: "OK",
    1: "Manipulated Front",
    2: "Scratch Head",
    3: "Scratch Neck",
    4: "Thread Side",
    5: "Thread Top"
}
DEFECT_CLASSES = {1, 2, 3, 4, 5}

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
            annotated, boxes, scores, cids = predict_frame(model, frame, conf=CONF_THRESHOLD, use_tta=USE_TTA)
            
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