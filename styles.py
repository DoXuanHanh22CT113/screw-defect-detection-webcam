"""
Shared CSS styles for all pages - Ultra Premium Futuristic Theme
Advanced glassmorphism, animations, and modern web design
"""

PREMIUM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {
        --primary-purple: #9D4EDD;
        --primary-blue: #7B68EE;
        --accent-cyan: #00D4FF;
        --accent-pink: #FF6B9D;
        --accent-green: #00F5A0;
        --bg-navy: #0a0e1a;
        --bg-dark: #0d1224;
        --bg-card: rgba(13, 18, 36, 0.8);
        --border-glow: rgba(157, 78, 221, 0.5);
        --text-primary: #E0E7FF;
        --text-secondary: #9CA3AF;
        --success: #00F5A0;
        --danger: #FF4757;
        --warning: #FFB347;
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
    }
    
    /* ===== ANIMATED BACKGROUND ===== */
    .main, .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1224 25%, #131833 50%, #0d1224 75%, #0a0e1a 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 15s ease infinite !important;
        background-attachment: fixed !important;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ===== FLOATING PARTICLES EFFECT ===== */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(2px 2px at 20% 30%, rgba(157, 78, 221, 0.3), transparent),
            radial-gradient(2px 2px at 40% 70%, rgba(0, 212, 255, 0.3), transparent),
            radial-gradient(1px 1px at 80% 20%, rgba(255, 107, 157, 0.2), transparent),
            radial-gradient(2px 2px at 60% 90%, rgba(0, 245, 160, 0.2), transparent);
        background-size: 200% 200%;
        animation: floatParticles 20s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes floatParticles {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }
    
    /* ===== PREMIUM SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(13, 18, 36, 0.98) 0%, rgba(10, 14, 26, 0.98) 100%) !important;
        border-right: 1px solid var(--border-glow) !important;
        box-shadow: 
            4px 0 30px rgba(157, 78, 221, 0.15),
            inset -1px 0 30px rgba(0, 212, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    section[data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(180deg, 
            rgba(157, 78, 221, 0.08) 0%, 
            transparent 30%,
            transparent 70%,
            rgba(0, 212, 255, 0.05) 100%);
        pointer-events: none;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    /* ===== NEON GLOW TITLE ===== */
    h1 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 3rem !important;
        text-align: center !important;
        background: linear-gradient(135deg, #9D4EDD 0%, #7B68EE 30%, #00D4FF 60%, #00F5A0 100%) !important;
        background-size: 200% 200% !important;
        animation: titleGradient 5s ease infinite !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        filter: drop-shadow(0 0 30px rgba(157, 78, 221, 0.5)) 
                drop-shadow(0 0 60px rgba(0, 212, 255, 0.3)) !important;
        letter-spacing: 3px !important;
        margin-bottom: 20px !important;
        margin-top: 10px !important;
        position: relative !important;
    }
    
    @keyframes titleGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ===== SUBTITLE HEADERS ===== */
    h2 {
        font-family: 'Orbitron', sans-serif !important;
        color: transparent !important;
        background: linear-gradient(90deg, #9D4EDD, #00D4FF) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
        border-bottom: 2px solid;
        border-image: linear-gradient(90deg, #9D4EDD, #00D4FF, transparent) 1;
        padding-bottom: 12px;
        margin-top: 30px !important;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    h3 {
        font-family: 'Inter', sans-serif !important;
        color: var(--accent-cyan) !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        margin-top: 20px !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    /* ===== BODY TEXT ===== */
    body, p, span, div, label {
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    /* ===== ULTRA PREMIUM BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B68EE 50%, #5852D6 100%) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 
            0 6px 25px rgba(157, 78, 221, 0.4),
            0 0 40px rgba(157, 78, 221, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
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
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255,255,255,0.4), 
            transparent) !important;
        transition: left 0.6s ease !important;
    }
    
    .stButton > button:hover::before {
        left: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: 
            0 15px 45px rgba(157, 78, 221, 0.5),
            0 0 60px rgba(157, 78, 221, 0.3),
            0 0 100px rgba(0, 212, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(0.98) !important;
    }
    
    /* ===== GLASSMORPHISM METRICS ===== */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.1) 0%, 
            rgba(0, 212, 255, 0.05) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        padding: 24px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            0 0 40px rgba(157, 78, 221, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        transition: all 0.4s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #9D4EDD, #00D4FF, transparent);
        animation: borderGlow 3s ease infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: rgba(157, 78, 221, 0.6) !important;
        box-shadow: 
            0 15px 50px rgba(0, 0, 0, 0.4),
            0 0 60px rgba(157, 78, 221, 0.2) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(135deg, #9D4EDD 0%, #00D4FF 50%, #00F5A0 100%) !important;
        background-size: 200% 200% !important;
        animation: valueGradient 4s ease infinite !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
        filter: drop-shadow(0 0 15px rgba(157, 78, 221, 0.5)) !important;
    }
    
    @keyframes valueGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 0.85rem !important;
    }
    
    /* ===== NEON SLIDER ===== */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #9D4EDD 0%, #00D4FF 50%, #00F5A0 100%) !important;
        box-shadow: 0 0 15px rgba(157, 78, 221, 0.5),
                    0 0 30px rgba(0, 212, 255, 0.3) !important;
    }
    
    .stSlider > div > div > div {
        background: rgba(157, 78, 221, 0.15) !important;
        border-radius: 10px !important;
    }
    
    /* ===== PREMIUM FILE UPLOADER ===== */
    .stFileUploader {
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.08) 0%, 
            rgba(0, 212, 255, 0.05) 100%) !important;
        border: 2px dashed rgba(157, 78, 221, 0.5) !important;
        border-radius: 20px !important;
        padding: 35px !important;
        transition: all 0.4s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stFileUploader:hover {
        border-color: #9D4EDD !important;
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.15) 0%, 
            rgba(0, 212, 255, 0.1) 100%) !important;
        box-shadow: 0 0 40px rgba(157, 78, 221, 0.3),
                    inset 0 0 40px rgba(157, 78, 221, 0.05) !important;
        transform: scale(1.01);
    }
    
    /* ===== PREMIUM ALERTS WITH ANIMATION ===== */
    .stAlert {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(15px) !important;
        animation: fadeIn 0.5s ease !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container:has(.stSuccess) {
        background: linear-gradient(135deg, 
            rgba(0, 245, 160, 0.15) 0%, 
            rgba(0, 245, 160, 0.05) 100%) !important;
        border-left: 4px solid var(--success) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: 0 0 30px rgba(0, 245, 160, 0.1) !important;
    }
    
    .element-container:has(.stError) {
        background: linear-gradient(135deg, 
            rgba(255, 71, 87, 0.15) 0%, 
            rgba(255, 71, 87, 0.05) 100%) !important;
        border-left: 4px solid var(--danger) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: 0 0 30px rgba(255, 71, 87, 0.1) !important;
        animation: shake 0.5s ease !important;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .element-container:has(.stInfo) {
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.15) 0%, 
            rgba(0, 212, 255, 0.08) 100%) !important;
        border-left: 4px solid #9D4EDD !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: 0 0 30px rgba(157, 78, 221, 0.1) !important;
    }
    
    .element-container:has(.stWarning) {
        background: linear-gradient(135deg, 
            rgba(255, 179, 71, 0.15) 0%, 
            rgba(255, 179, 71, 0.05) 100%) !important;
        border-left: 4px solid var(--warning) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        box-shadow: 0 0 30px rgba(255, 179, 71, 0.1) !important;
    }
    
    /* ===== ANIMATED DIVIDER ===== */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, 
            transparent 0%, 
            #9D4EDD 20%, 
            #7B68EE 40%, 
            #00D4FF 60%, 
            #00F5A0 80%, 
            transparent 100%) !important;
        margin: 45px 0 !important;
        animation: dividerPulse 3s ease infinite !important;
        border-radius: 2px !important;
    }
    
    @keyframes dividerPulse {
        0%, 100% { opacity: 0.6; transform: scaleX(0.95); }
        50% { opacity: 1; transform: scaleX(1); }
    }
    
    /* ===== FUTURISTIC TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, 
            rgba(13, 18, 36, 0.9) 0%, 
            rgba(19, 24, 51, 0.9) 100%) !important;
        border-radius: 20px !important;
        padding: 8px !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        gap: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.3s ease !important;
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(157, 78, 221, 0.1) !important;
        color: var(--text-primary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B68EE 100%) !important;
        color: white !important;
        box-shadow: 0 6px 25px rgba(157, 78, 221, 0.5),
                    0 0 40px rgba(157, 78, 221, 0.2) !important;
        border: none !important;
    }
    
    /* ===== PREMIUM IMAGE CONTAINER ===== */
    .stImage {
        border-radius: 20px !important;
        overflow: hidden !important;
        border: 2px solid rgba(157, 78, 221, 0.4) !important;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.5),
            0 0 60px rgba(157, 78, 221, 0.15),
            inset 0 0 80px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.4s ease !important;
    }
    
    .stImage:hover {
        transform: scale(1.02);
        border-color: rgba(157, 78, 221, 0.7) !important;
        box-shadow: 
            0 15px 50px rgba(0, 0, 0, 0.6),
            0 0 80px rgba(157, 78, 221, 0.25) !important;
    }
    
    /* ===== CHECKBOX STYLING ===== */
    .stCheckbox label {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox label:hover {
        color: var(--accent-cyan) !important;
    }
    
    /* ===== CUSTOM NEON SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #9D4EDD 0%, #7B68EE 50%, #00D4FF 100%);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #B35FFF 0%, #9D82FF 50%, #33E1FF 100%);
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.8);
    }
    
    /* ===== DATAFRAME TABLE ===== */
    .stDataFrame {
        background: var(--glass-bg) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        overflow: hidden !important;
    }
    
    /* ===== SELECTBOX ===== */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, 
            rgba(13, 18, 36, 0.95) 0%, 
            rgba(19, 24, 51, 0.95) 100%) !important;
        border: 1px solid rgba(157, 78, 221, 0.4) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #9D4EDD !important;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.3) !important;
    }
    
    /* ===== NUMBER INPUT ===== */
    .stNumberInput > div > div > input {
        background: linear-gradient(135deg, 
            rgba(13, 18, 36, 0.95) 0%, 
            rgba(19, 24, 51, 0.95) 100%) !important;
        border: 1px solid rgba(157, 78, 221, 0.4) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #9D4EDD !important;
        box-shadow: 0 0 25px rgba(157, 78, 221, 0.4) !important;
    }
    
    /* ===== ANIMATED FEATURE TAGS ===== */
    .feature-tag {
        display: inline-block;
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.2) 0%, 
            rgba(0, 212, 255, 0.15) 100%);
        border: 1px solid rgba(157, 78, 221, 0.4);
        border-radius: 25px;
        padding: 10px 20px;
        margin: 6px;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(157, 78, 221, 0.2);
    }
    
    .feature-tag:hover {
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.35) 0%, 
            rgba(0, 212, 255, 0.25) 100%);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(157, 78, 221, 0.4);
        border-color: rgba(157, 78, 221, 0.7);
    }
    
    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #9D4EDD 0%, #00D4FF 50%, #00F5A0 100%) !important;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.5),
                    0 0 40px rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
    }
    
    .stProgress > div > div {
        background: rgba(157, 78, 221, 0.15) !important;
        border-radius: 10px !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, 
            rgba(157, 78, 221, 0.1) 0%, 
            rgba(0, 212, 255, 0.05) 100%) !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #9D4EDD !important;
        box-shadow: 0 0 25px rgba(157, 78, 221, 0.3) !important;
    }
    
    /* ===== TOOLTIP ===== */
    .stTooltipIcon {
        color: var(--accent-cyan) !important;
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00D4FF 0%, #00F5A0 100%) !important;
        color: #0a0e1a !important;
        font-weight: 700 !important;
        border: none !important;
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.4) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.5),
                    0 0 60px rgba(0, 245, 160, 0.3) !important;
    }
    
    /* ===== COLUMN GAP ADJUSTMENT ===== */
    [data-testid="column"] {
        padding: 0 10px !important;
    }
    
    /* ===== GLASSMORPHISM CARDS ===== */
    .glass-card {
        background: linear-gradient(135deg, 
            rgba(255, 255, 255, 0.05) 0%, 
            rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    /* ===== STATUS INDICATOR ===== */
    .status-ok {
        color: var(--success) !important;
        text-shadow: 0 0 20px rgba(0, 245, 160, 0.5);
    }
    
    .status-error {
        color: var(--danger) !important;
        text-shadow: 0 0 20px rgba(255, 71, 87, 0.5);
        animation: pulse 1.5s ease infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* ===== LOADING SPINNER ===== */
    .stSpinner > div {
        border-top-color: #9D4EDD !important;
        border-right-color: #00D4FF !important;
        border-bottom-color: #00F5A0 !important;
        filter: drop-shadow(0 0 10px rgba(157, 78, 221, 0.5));
    }
    
    /* ===== CAPTION TEXT ===== */
    .stCaption {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* ===== HEADER ICON CONTAINER ===== */
    .header-icon {
        font-size: 5rem;
        text-align: center;
        margin-bottom: 10px;
        animation: iconFloat 3s ease-in-out infinite;
        filter: drop-shadow(0 0 30px rgba(157, 78, 221, 0.5));
    }
    
    @keyframes iconFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
</style>
"""

def apply_premium_theme():
    """Apply the ultra premium futuristic theme to Streamlit pages"""
    import streamlit as st
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
