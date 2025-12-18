import streamlit as st
import pandas as pd
import json
from database import get_all_detections, delete_old_detections, delete_detection
import os
import time
from datetime import datetime
from styles import apply_premium_theme

st.set_page_config(page_title="Trình xem cơ sở dữ liệu", layout="wide")

# Apply premium theme
apply_premium_theme()

# Enhanced Header
st.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <div style="font-size: 4rem; margin-bottom: 10px;">📊</div>
</div>
""", unsafe_allow_html=True)

st.title("📊 DATABASE VIEWER")

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(157, 78, 221, 0.15) 0%, rgba(0, 212, 255, 0.1) 100%);
            padding: 20px 30px; border-radius: 16px; border: 1px solid rgba(157, 78, 221, 0.4); 
            margin-bottom: 30px; backdrop-filter: blur(10px); text-align: center;">
    <p style="color: #E0E7FF; margin: 0; font-size: 16px; font-weight: 500; line-height: 1.8;">
    <span class="feature-tag">🖼️ Gallery View</span>
    <span class="feature-tag">📋 Table View</span>
    <span class="feature-tag">📊 Statistics</span>
    <span class="feature-tag">🗑️ Delete Records</span>
    </p>
</div>
""", unsafe_allow_html=True)



# Lấy tất cả dữ liệu
detections = get_all_detections()

if not detections:
    st.info("📭 Cơ sở dữ liệu trống. Chụp một số khung hình trước!")
else:
    # Chuyển đổi sang DataFrame
    df = pd.DataFrame(detections, columns=[
        'ID', 'Timestamp', 'Đường dẫn ảnh', 'Phát hiện khuyết tật', 
        'Số khuyết tật', 'Điểm tin cậy', 'ID lớp', 'Hộp'
    ])
    
    # Định dạng lại
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Trạng thái'] = df['Phát hiện khuyết tật'].map({1: '❌ Khuyết tật', 0: '✅ OK'})
    df['Giờ'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # ========== FILTER TABS ==========
    tab1, tab2, tab3 = st.tabs(["🖼️ Xem thư viện", "📋 Xem bảng", "📊 Thống kê"])
    
    with tab1:
        st.subheader("Thư viện ảnh khuyết tật")
        # Lọc chỉ ảnh có defect
        defect_df = df[df['Phát hiện khuyết tật'] == 1].sort_values('Timestamp', ascending=False)
        
        if len(defect_df) == 0:
            st.info("✅ Không tìm thấy khuyết tật trong cơ sở dữ liệu!")
        else:
            st.info(f"📸 Đang hiển thị {len(defect_df)} hình ảnh khuyết tật")
            
            # Session state để track deletions
            if 'deleted_ids' not in st.session_state:
                st.session_state.deleted_ids = set()
            
            # Hiển thị ảnh dưới dạng grid
            cols = st.columns(3)
            img_count = 0
            for idx, row in defect_df.iterrows():
                # Skip if deleted
                if row['ID'] in st.session_state.deleted_ids:
                    continue
                    
                col = cols[img_count % 3]
                img_count += 1
                
                with col:
                    image_path = row['Đường dẫn ảnh']
                    if os.path.exists(image_path):
                        # Container với border cho mỗi ảnh
                        st.markdown(f"""
                        <div style='background: rgba(30, 41, 59, 0.6); 
                                    border-radius: 12px; 
                                    padding: 10px; 
                                    border: 1px solid rgba(139, 92, 246, 0.3);
                                    margin-bottom: 15px;'>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.image(image_path, use_container_width=True)
                        st.markdown(f"**🕐 {row['Giờ']}**")
                        st.markdown(f"Khuyết tật: **{row['Số khuyết tật']}**")
                        scores_str = ", ".join([f"{s:.2f}" for s in json.loads(row['Điểm tin cậy'])])
                        st.caption(f"Độ tin cậy: {scores_str}")
                        
                        # Delete button
                        if st.button(f"🗑️ Xóa", key=f"delete_{row['ID']}", use_container_width=True):
                            # Delete from Firebase
                            delete_detection(row['ID'])
                            # Delete image file if exists
                            if os.path.exists(image_path):
                                try:
                                    os.remove(image_path)
                                except Exception as e:
                                    st.warning(f"Không thể xóa file: {e}")
                            # Track deletion
                            st.session_state.deleted_ids.add(row['ID'])
                            st.success("✅ Đã xóa!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        st.warning(f"⚠️ Không tìm thấy hình ảnh: {image_path}")
    
    with tab2:
        st.subheader("Bảng tất cả phát hiện")
        st.dataframe(df[['ID', 'Giờ', 'Số khuyết tật', 'Trạng thái', 'Đường dẫn ảnh']], 
                     use_container_width=True)
    
    with tab3:
        st.subheader("📊 Thống kê & Quản lý")
        
        # Thống kê
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = len(df)
            st.metric("📈 Tổng bản ghi", total)
        
        with col2:
            defects = (df['Phát hiện khuyết tật'] == 1).sum()
            st.metric("❌ Tìm thấy khuyết tật", defects)
        
        with col3:
            ok = (df['Phát hiện khuyết tật'] == 0).sum()
            st.metric("✅ Không có khuyết tật", ok)
        
        # Chart
        st.divider()
        st.subheader("Tóm tắt phát hiện")
        summary = df['Trạng thái'].value_counts()
        st.bar_chart(summary)
    
    # ========== BOTTOM SECTION ==========
    st.divider()
    st.subheader("🛠️ Quản lý dữ liệu")
    
    col1, col2, col3 = st.columns(3)
    
    # CSV Download
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Tải xuống dưới dạng CSV",
            data=csv,
            file_name="detection_data.csv",
            mime="text/csv"
        )
    
    # Defect-only CSV
    with col2:
        defect_csv = df[df['Phát hiện khuyết tật'] == 1].to_csv(index=False)
        st.download_button(
            label="❌ Chỉ tải khuyết tật",
            data=defect_csv,
            file_name="defects_only.csv",
            mime="text/csv"
        )
    
    # Delete Old Data
    with col3:
        st.write("Xóa bản ghi cũ hơn:")
        days = st.number_input("Ngày:", min_value=1, max_value=30, value=7)
        if st.button("🗑️ Xóa dữ liệu cũ", type="secondary"):
            delete_old_detections(days)
            st.success(f"✅ Đã xóa bản ghi cũ hơn {days} ngày")
            st.rerun()