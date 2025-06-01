import streamlit as st
import os
import random
import base64
import streamlit.components.v1 as components
from utils.common_css import add_logo

# ------------------ CONFIGURATION ------------------
BASE_PATH = "data/Places"
st.set_page_config(page_title="Indian Cultural Heritage", layout="wide")
add_logo("data/BGs/logo_app.png")
def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = "data/BGs/heritage.jpeg"
bg_base64 = local_image_to_base64(bg_path)
# Main app background
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                    url("data:image/jpeg;base64,{bg_base64}");
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-size: cover;
    }}
    </style>
""", unsafe_allow_html=True)

# Sidebar background
st.markdown(f"""
    <style>
    section[data-testid="stSidebar"] {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url("data:image/jpeg;base64,{bg_base64}");
        background-position: center center;
        background-repeat: no-repeat;
        background-size: cover;
    }}
    </style>
""", unsafe_allow_html=True)

# ------------------ UTILITY FUNCTIONS ------------------
def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def list_states():
    if not os.path.exists(BASE_PATH):
        return []
    return sorted([d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))])

def list_places(state):
    state_path = os.path.join(BASE_PATH, state)
    if not os.path.exists(state_path):
        return []
    return sorted([d for d in os.listdir(state_path) if os.path.isdir(os.path.join(state_path, d))])

def list_images(state, place=None):
    images = []
    if place:
        folder_path = os.path.join(BASE_PATH, state, place)
        if os.path.exists(folder_path):
            images = [os.path.join(folder_path, img) for img in os.listdir(folder_path) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
    else:
        state_path = os.path.join(BASE_PATH, state)
        for place_folder in os.listdir(state_path):
            place_path = os.path.join(state_path, place_folder)
            if os.path.isdir(place_path):
                imgs = [os.path.join(place_path, img) for img in os.listdir(place_path) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
                images.extend(imgs)
    return images

def ensure_state_and_place(state, place):
    state_path = ensure_folder(os.path.join(BASE_PATH, state))
    place_path = ensure_folder(os.path.join(state_path, place))
    return place_path

def encode_image(img_path):
    with open(img_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded}"
st.markdown("<h1 style='text-align:center;color:#FFD700;'>🇮🇳 Indian Cultural Heritage</h1>", unsafe_allow_html=True)


# ------------------ SIDEBAR ------------------
with st.sidebar:
    mode = st.radio("Choose Operation", ["📊 View Heritage Gallery", "🚀 Upload New Images"])

# ------------------ GALLERY VIEW ------------------
if mode == "📊 View Heritage Gallery":
    states = list_states()

    if not states:
        st.warning("⚠️ No States available. Please upload data first.")
    else:
        selected_state = st.selectbox("Select State", states)
        places = list_places(selected_state)
        place_selected = st.selectbox("Select Place (optional)", ["All Places"] + places)

        images = list_images(selected_state) if place_selected == "All Places" else list_images(selected_state, place_selected)

        if not images:
            st.warning("⚠️ No images found for this selection.")
        else:
            gallery_type = st.radio("Interactive Zoomable Gallery", ["Interactive Zoomable Gallery", "Smooth Horizontal Slider"], horizontal=True)
            sample_imgs = random.sample(images, min(20, len(images)))

            # -------- SMOOTH SLIDER GALLERY --------
            if gallery_type == "Smooth Horizontal Slider":
                slides = ""
                for img_path in sample_imgs:
                    img_data = encode_image(img_path)
                    slides += f"<div class='swiper-slide'><img src='{img_data}'></div>"

                html_code = f"""
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@9/swiper-bundle.min.css" />
                <script src="https://cdn.jsdelivr.net/npm/swiper@9/swiper-bundle.min.js"></script>

                <style>
                  .swiper {{
                    width: 80%;
                    height: 500px;
                    margin: auto;
                  }}
                  .swiper-slide {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                  }}
                  .swiper-slide img {{
                    max-width: 400px;
                    height: 400px;
                    object-fit: cover;
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                  }}
                </style>

                <div class="swiper mySwiper">
                  <div class="swiper-wrapper">{slides}</div>
                  <div class="swiper-button-next"></div>
                  <div class="swiper-button-prev"></div>
                </div>

                <script>
                  const swiper = new Swiper('.mySwiper', {{
                    loop: true,
                    autoplay: {{ delay: 1500, disableOnInteraction: false }},
                    speed: 1000,
                    navigation: {{ nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' }},
                    slidesPerView: 1,
                    centeredSlides: true,
                  }});
                </script>
                """

                components.html(html_code, height=600)

            # -------- INTERACTIVE FULLSCREEN ZOOM GALLERY --------
            else:
                html_code = """
                <style>
                    .gallery { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
                    .gallery img { height: 250px; width: 350px; object-fit: cover; border-radius: 15px; 
                                   box-shadow: 0 4px 15px rgba(0,0,0,0.5); transition: 0.3s; cursor: pointer; }
                    .gallery img:hover { transform: scale(1.1); }
                    .lightbox { display: none; position: fixed; z-index: 9999; top: 0; left: 0; width: 100%; 
                                height: 100%; background: rgba(0,0,0,0.95); justify-content: center; align-items: center; }
                    .lightbox-content { position: relative; max-width: 90%; max-height: 90%; }
                    .lightbox img { max-width: 100%; max-height: 100%; border-radius: 15px; transition: transform 0.3s; }
                    .close-btn { position: absolute; top: 40px; right: 60px; font-size: 60px; color: white; cursor: pointer; z-index: 99999; }
                </style>

                <div class="gallery">
                """

                for img_path in sample_imgs:
                    img_data = encode_image(img_path)
                    html_code += f"<img src='{img_data}' onclick='openLightbox(\"{img_data}\")'>"

                html_code += """
                </div>

                <div class="lightbox" id="lightbox">
                    <div class="close-btn" onclick="closeLightbox()">&times;</div>
                    <div class="lightbox-content">
                        <img id="lightbox-img" src="" />
                    </div>
                </div>

                <script>
                    let scale = 1;
                    function openLightbox(src) {
                        document.getElementById("lightbox-img").src = src;
                        document.getElementById("lightbox").style.display = "flex";
                        scale = 1;
                        document.getElementById("lightbox-img").style.transform = `scale(${scale})`;
                    }
                    function closeLightbox() {
                        document.getElementById("lightbox").style.display = "none";
                    }
                    document.getElementById("lightbox").addEventListener("wheel", function(e) {
                        e.preventDefault();
                        scale += e.deltaY * -0.001;
                        scale = Math.min(Math.max(.5, scale), 4);
                        document.getElementById("lightbox-img").style.transform = `scale(${scale})`;
                    });
                </script>
                """

                components.html(html_code, height=800)

# ------------------ UPLOAD SECTION ------------------
elif mode == "🚀 Upload New Images":
    st.header("Upload Heritage Images")
    states = list_states()
    state_mode = st.radio("State", ["Select Existing State", "Add New State"], horizontal=True)

    if state_mode == "Select Existing State" and states:
        selected_state = st.selectbox("Select State", states)
        places = list_places(selected_state)
        place_mode = st.radio("Place", ["Select Existing Place", "Add New Place"], horizontal=True)
        if place_mode == "Select Existing Place" and places:
            selected_place = st.selectbox("Select Place", places)
        else:
            selected_place = st.text_input("Enter New Place Name").strip()
    elif state_mode == "Add New State":
        selected_state = st.text_input("Enter New State Name").strip()
        if selected_state:
            selected_place = st.text_input("Enter New Place Name").strip()

    if selected_state and selected_place:
        uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=["jpg", "jpeg", "png"])
        if uploaded_files:
            place_path = ensure_state_and_place(selected_state, selected_place)
            for file in uploaded_files:
                file_path = os.path.join(place_path, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.read())
            st.success(f"{len(uploaded_files)} images uploaded to {selected_state}/{selected_place} successfully!")
