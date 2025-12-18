"""
Shared CSS styles for all pages - Premium Navy/Purple Theme
Based on modern screw defect detector design
"""

PREMIUM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-purple: #9D4EDD;
        --primary-blue: #7B68EE;
        --accent-cyan: #00D4FF;
        --bg-navy: #0a0e27;
        --bg-dark: #141B3D;
        --card-bg: rgba(20, 27, 61, 0.8);
        --border-glow: rgba(157, 78, 221, 0.4);
        --text-primary: #E0E7FF;
        --text-secondary: #9CA3AF;
        --success: #10B981;
        --danger: #EF4444;
    }
    
    /* Main Background - Deep Navy */
    .main, .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #141B3D 50%, #1a1f4a 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Sidebar - Navy with glow */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #141B3D 100%) !important;
        border-right: 2px solid var(--border-glow) !important;
        box-shadow: 0 0 30px rgba(157, 78, 221, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* Main Title - Large Gradient with Glow */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 3.5rem !important;
        text-align: center !important;
        background: linear-gradient(135deg, #9D4EDD 0%, #7B68EE 50%, #00D4FF 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: 0 0 40px rgba(157, 78, 221, 0.5) !important;
        letter-spacing: 4px !important;
        margin-bottom: 10px !important;
        margin-top: 20px !important;
    }
    
    /* Subtitle Headers */
    h2 {
        font-family: 'Orbitron', sans-serif !important;
        color: #9D4EDD !important;
        font-weight: 600 !important;
        font-size: 1.8rem !important;
        border-bottom: 2px solid rgba(157, 78, 221, 0.3);
        padding-bottom: 10px;
        margin-top: 30px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    h3 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
        margin-top: 20px !important;
    }
    
    /* Body Text */
    body, p, span, div, label {
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    /* Premium Gradient Buttons with Glow */
    .stButton > button {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B68EE 50%, #5E60CE 100%) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 32px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 32px rgba(157, 78, 221, 0.5) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
        transition: left 0.5s !important;
    }
    
    .stButton > button:hover::before {
        left: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 12px 48px rgba(157, 78, 221, 0.7) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(0.99) !important;
    }
    
    /* Metrics - Glowing Cards */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(135deg, #9D4EDD 0%, #00D4FF 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 900 !important;
        font-size: 2.5rem !important;
        text-shadow: 0 0 20px rgba(157, 78, 221, 0.5) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.9rem !important;
    }
    
    div[data-testid="stMetric"] {
        background: var(--card-bg) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        border: 1px solid var(--border-glow) !important;
        box-shadow: 0 4px 24px rgba(157, 78, 221, 0.2) !important;
    }
    
    /* Slider - Purple Gradient */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #9D4EDD 0%, #7B68EE 50%, #00D4FF 100%) !important;
    }
    
    .stSlider > div > div > div {
        background: rgba(157, 78, 221, 0.2) !important;
    }
    
    /* File Uploader - Dashed Border with Glow */
    .stFileUploader {
        background: var(--card-bg) !important;
        border: 3px dashed var(--border-glow) !important;
        border-radius: 16px !important;
        padding: 30px !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #9D4EDD !important;
        background: rgba(157, 78, 221, 0.1) !important;
        box-shadow: 0 0 30px rgba(157, 78, 221, 0.3) !important;
    }
    
    /* Alert Messages */
    .stAlert {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .element-container:has(.stSuccess) {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%) !important;
        border-left: 4px solid var(--success) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    
    .element-container:has(.stError) {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
        border-left: 4px solid var(--danger) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    
    .element-container:has(.stInfo) {
        background: linear-gradient(135deg, rgba(157, 78, 221, 0.15) 0%, rgba(0, 212, 255, 0.05) 100%) !important;
        border-left: 4px solid #9D4EDD !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    
    /* Divider - Animated Gradient */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #9D4EDD, #7B68EE, #00D4FF, transparent) !important;
        margin: 40px 0 !important;
        animation: shimmer 3s infinite !important;
    }
    
    @keyframes shimmer {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    /* Tabs - Modern Style */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg) !important;
        border-radius: 16px !important;
        padding: 8px !important;
        border: 1px solid var(--border-glow) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B68EE 100%) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(157, 78, 221, 0.5) !important;
    }
    
    /* Image - Glowing Border */
    .stImage {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 2px solid var(--border-glow) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #9D4EDD 0%, #7B68EE 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #B35FFF 0%, #9D82FF 100%);
    }
    
    /* Dataframe/Table */
    .stDataFrame {
        background: var(--card-bg) !important;
        border-radius: 16px !important;
        border: 1px solid var(--border-glow) !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    /* Number Input */
    .stNumberInput > div > div > input {
        background: var(--card-bg) !important;
        border: 1px solid var(--border-glow) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    /* Feature Tags */
    .feature-tag {
        display: inline-block;
        background: linear-gradient(135deg, rgba(157, 78, 221, 0.2), rgba(123, 104, 238, 0.2));
        border: 1px solid var(--border-glow);
        border-radius: 20px;
        padding: 6px 16px;
        margin: 5px;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
</style>
"""

def apply_premium_theme():
    """Apply the premium navy/purple theme to Streamlit pages"""
    import streamlit as st
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
