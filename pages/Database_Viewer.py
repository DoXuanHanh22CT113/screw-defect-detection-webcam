import streamlit as st
import pandas as pd
import sqlite3
import json
from database import get_all_detections, delete_old_detections
import os
from datetime import datetime

st.set_page_config(page_title="Trình xem cơ sở dữ liệu", layout="wide")

# Custom CSS - Premium Dark Mode Theme  
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main, .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%) !important;
    }
    
    h1, h2 {
        background: linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    
    h3 { color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
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
    
    [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #00D4FF 0%, #8B5CF6 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
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
    
    .stDataFrame {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px !important;
    }
    
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Trình xem cơ sở dữ liệu phát hiện")

# Tạo thư mục pages nếu chưa có
os.makedirs("pages", exist_ok=True)

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
            
            # Hiển thị ảnh dưới dạng grid
            cols = st.columns(3)
            for idx, row in defect_df.iterrows():
                col = cols[idx % 3]
                with col:
                    image_path = row['Đường dẫn ảnh']
                    if os.path.exists(image_path):
                        st.image(image_path, use_container_width=True)
                        st.markdown(f"**🕐 {row['Giờ']}**")
                        st.markdown(f"Khuyết tật: **{row['Số khuyết tật']}**")
                        scores_str = ", ".join([f"{s:.2f}" for s in json.loads(row['Điểm tin cậy'])])
                        st.caption(f"Độ tin cậy: {scores_str}")
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