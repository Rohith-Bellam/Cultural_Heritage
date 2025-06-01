import streamlit as st
import base64
import os
from PIL import Image
from io import BytesIO
from utils.common_css import add_logo

# -------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Akhand Bharat - Intelligent Cultural Tourism 🇮🇳",
    page_icon="🌏",
    layout="wide"
)
add_logo("data/BGs/logo_app.png")

# Helper to encode local image (optimized version)
@st.cache_data(show_spinner=False)
def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Main background
bg_path = "data/BGs/bg.png"
bg_base64 = local_image_to_base64(bg_path)

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                    url("data:image/png;base64,{bg_base64}");
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-size: cover;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("data:image/png;base64,{bg_base64}");
        background-position: center center;
        background-repeat: no-repeat;
        background-size: cover;
    }}
    </style>
""", unsafe_allow_html=True)

# -------------- LOAD IMAGES (Optimized) -------------------

@st.cache_data(show_spinner=False)
def load_and_optimize_images(folder, target_size=(320, 200)):
    images_base64 = []
    for file in sorted(os.listdir(folder)):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(folder, file)
            img = Image.open(path).convert("RGB")
            img.thumbnail(target_size, Image.LANCZOS)  # Resize to reduce memory
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=60)  # Compress
            encoded = base64.b64encode(buffered.getvalue()).decode()
            images_base64.append(encoded)
    return images_base64

image_folder = "./data/indian_tourist_images"
images_base64 = load_and_optimize_images(image_folder)

# -------------- BUILD MARQUEE HTML -------------------

def build_images_html(images):
    return "".join([
        f'<img src="data:image/jpeg;base64,{img}" loading="eager" />' for img in images
    ])

top_row_html = build_images_html(images_base64)

common_css = """
<style>
.marquee-container {
    overflow: hidden;
    width: 100%;
    background-color: rgba(255, 255, 255, 0.0);
    padding: 20px 0;
}
.marquee {
    display: flex;
    width: max-content;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}
.marquee img {
    height: 180px;
    margin-right: 20px;
    border-radius: 10px;
    object-fit: cover;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
@keyframes scrollLeft {
    0% { transform: translateX(0%); }
    100% { transform: translateX(-50%); }
}
</style>
"""
st.markdown(common_css, unsafe_allow_html=True)

# Single repetition instead of double
st.markdown(f"""
<div class="marquee-container">
    <div class="marquee" style="animation-name: scrollLeft; animation-duration: 30s;">
        {top_row_html}{top_row_html}
    </div>
</div>
""", unsafe_allow_html=True)

# -------------- CSS for Advanced Text Styling -------------------
st.markdown("""
    <style>
    h2 {
        font-family: 'Segoe UI', sans-serif;
        font-size: 50px !important;
        text-align: center;
        color: #FFD700;
        text-shadow: 3px 3px 10px #000;
        letter-spacing: 1px;
    }
    p.subtitle {
        font-size: 22px;
        text-align: center;
        color: #EEEEEE;
        text-shadow: 2px 2px 5px #000;
        padding: 0 15%;
    }
    .feature-box {
        border-radius: 20px;
        background: rgba(0, 0, 0, 0.65);
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: 0.3s;
    }
    .feature-box:hover {
        transform: translateY(-10px);
    }
    .feature-box h3 {
        color: #FFD700;
        font-weight: 700;
        font-size: 26px;
        margin-bottom: 15px;
    }
    .feature-box ul {
        list-style: none;
        color: #FFFFFF;
        font-size: 18px;
        padding-left: 0;
    }
    .cta-button button {
        background-color: #FF6F00;
        color: white;
        font-size: 22px;
        padding: 15px 40px;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        transition: 0.3s;
    }
    .cta-button button:hover {
        background-color: #FF8C00;
        transform: scale(1.08);
    }
    </style>
""", unsafe_allow_html=True)

# -------------- HEADER -------------------
st.markdown("<h2>🌏 Akhand Bharat - Indian Culture 🇮🇳</h2>", unsafe_allow_html=True)
st.markdown("""
    <p class="subtitle">
        AI-powered Tourism • Heritage Discovery • Dance Classifier • 3D Visualizations
    </p>
""", unsafe_allow_html=True)

# -------------- 3 FEATURE BOXES -------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-box">
            <h3>🔎 Search & Discover</h3>
            <ul>
                <li>AI-based intelligent search</li>
                <li>Multi-state cultural data</li>
                <li>Dynamic recommendations</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-box">
            <h3>🎯 Personalize Trip</h3>
            <ul>
                <li>Interactive trip builder</li>
                <li>Auto-suggested attractions</li>
                <li>State-wise cultural hotspots</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-box">
            <h3>🚀 Contribute Data</h3>
            <ul>
                <li>Upload monuments</li>
                <li>Expand cultural datasets</li>
                <li>Community-powered growth</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
