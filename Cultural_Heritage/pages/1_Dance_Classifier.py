import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
import os
import shutil
import random
from PIL import Image
import base64
import streamlit.components.v1 as components
from utils.common_css import add_logo

# --- Constants ---
BASE_DIR = "data/Dance_Forms"
TRAIN_DIR = os.path.join(BASE_DIR, "Train")
UPLOAD_DIR = os.path.join(BASE_DIR, "New_Uploads")
MODEL_PATH = os.path.join(BASE_DIR, "dance_model.h5")
IMG_SIZE = (224, 224)


# --- Utility functions ---
def list_valid_dirs(path):
    return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')])


def list_valid_images(path):
    return sorted([f for f in os.listdir(path) if not f.startswith('.')])


def load_model():
    if os.path.exists(MODEL_PATH):
        return tf.keras.models.load_model(MODEL_PATH)
    return None


def train_model():
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        TRAIN_DIR,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=32
    )
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        TRAIN_DIR,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=32
    )
    class_names = train_ds.class_names
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    model = tf.keras.Sequential([
        tf.keras.layers.Rescaling(1. / 255, input_shape=(224, 224, 3)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(len(class_names), activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    model.fit(train_ds, validation_data=val_ds, epochs=10)
    model.save(MODEL_PATH)
    return class_names


def predict_dance(model, class_names, image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=IMG_SIZE)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions)]
    return predicted_class


def move_new_uploads_to_train():
    updated = False
    for cls in list_valid_dirs(UPLOAD_DIR):
        class_dir = os.path.join(UPLOAD_DIR, cls)
        target_dir = os.path.join(TRAIN_DIR, cls)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        for img in list_valid_images(class_dir):
            shutil.move(os.path.join(class_dir, img), target_dir)
            updated = True
    return updated


# --- Streamlit UI ---
st.set_page_config(page_title="Dance Form Classifier", layout="wide")
add_logo("data/BGs/logo_app.png")
def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = "data/BGs/dance.jpeg"
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


st.markdown("<h1 style='text-align:center;color:#FFD700;'> 💃 Indian Dance Forms</h1>", unsafe_allow_html=True)
menu = "💃 Dance Forms"
menu = st.selectbox("Choose Mode", ["💃 Dance Forms", "🖼 Know the Dance Form", "🚀 Contribute Dance Data"])

# ✅ NOTE: No set_page_config() here since you're calling inside a multi-page Streamlit app

# --- Constants ---
TRAIN_DIR = "data/Dance_Forms/Train"

# --- Utility functions ---
def list_valid_dirs(path):
    return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')])

def list_valid_images(path):
    return sorted([f for f in os.listdir(path) if not f.startswith('.') and f.lower().endswith(('.jpg', '.jpeg', '.png'))])

def encode_image(img_path):
    with open(img_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded}"

# --- Main Gallery Code ---

if menu == "💃 Dance Forms":
    class_list = list_valid_dirs(TRAIN_DIR)

    if not class_list:
        st.warning("⚠️ No dance forms available.")
    else:
        selected_class = st.selectbox("Select Dance Form", class_list)
        gallery_type = st.radio("Select Gallery Type", ["3D Carousel", "Flip Gallery"], horizontal=True)

        sample_path = os.path.join(TRAIN_DIR, selected_class)
        all_imgs = list_valid_images(sample_path)
        sample_imgs = random.sample(all_imgs, min(10, len(all_imgs)))  # max 10 for smoother animation

        st.markdown(f"### 🎯 **{selected_class}**")

        if gallery_type == "3D Carousel":
            slides = ""
            for img_file in sample_imgs:
                full_path = os.path.join(sample_path, img_file)
                img_data = encode_image(full_path)
                slides += f'<div class="item"><img src="{img_data}" alt="Dance Image"></div>'

            html_code = f"""
            <style>
                .carousel {{
                    width: 500px;
                    height: 500px;
                    position: relative;
                    margin: auto;
                    perspective: 1500px;
                    transform-style: preserve-3d;
                }}
                .item {{
                    width: 300px;
                    height: 400px;
                    position: absolute;
                    top: 50px;
                    transition: transform 1s;
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
                }}
                .item img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }}
                #carousel {{
                    animation: rotate 20s infinite linear;
                }}
                @keyframes rotate {{
                    from {{ transform: rotateY(0deg); }}
                    to {{ transform: rotateY(360deg); }}
                }}
            </style>

            <div class="carousel" id="carousel">
                {slides}
            </div>

            <script>
                const items = document.querySelectorAll('.item');
                const angle = 360 / items.length;
                items.forEach((item, i) => {{
                    item.style.transform = 'rotateY(' + (i * angle) + 'deg) translateZ(400px)';
                }});
            </script>
            """
            components.html(html_code, height=650)

        else:  # Flip Gallery
            slides = ""
            for img_file in sample_imgs:
                full_path = os.path.join(sample_path, img_file)
                img_data = encode_image(full_path)
                slides += f'<div class="swiper-slide"><img src="{img_data}" class="slide-img"></div>'

            html_code = f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@9/swiper-bundle.min.css" />
            <script src="https://cdn.jsdelivr.net/npm/swiper@9/swiper-bundle.min.js"></script>

            <div class="swiper mySwiper" style="width:80%; height:500px; margin: auto;">
              <div class="swiper-wrapper">
                {slides}
              </div>

              <div class="swiper-button-next"></div>
              <div class="swiper-button-prev"></div>
            </div>

            <style>
                .slide-img {{
                    height: 450px;
                    border-radius: 15px;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }}
            </style>

            <script>
            const swiper = new Swiper('.mySwiper', {{
              loop: true,
              autoplay: {{
                delay: 1200,
                disableOnInteraction: false
              }},
              effect: 'flip',
              navigation: {{
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
              }},
              slidesPerView: 1,
            }});
            </script>
            """
            components.html(html_code, height=650)


# Predict Dance Form
elif menu == "🖼 Know the Dance Form":
    if not os.path.exists(MODEL_PATH):
        st.warning("Model not trained yet. Please upload new images for training first.")
    else:
        uploaded_file = st.file_uploader("Upload an Image for Prediction", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            img_path = os.path.join("temp_uploaded_image.jpg")
            with open(img_path, "wb") as f:
                f.write(uploaded_file.read())
            model = load_model()
            train_ds = tf.keras.preprocessing.image_dataset_from_directory(
                TRAIN_DIR,
                image_size=IMG_SIZE,
                batch_size=32)
            class_names = train_ds.class_names
            prediction = predict_dance(model, class_names, img_path)
            st.success(f"Predicted Dance Form: {prediction}")
            st.image(img_path, caption="Uploaded Image", width=300)

# Contribute Images for Training
elif menu == "🚀 Contribute Dance Data":
    uploaded_class = st.text_input("Enter Dance Form Name")
    uploaded_files = st.file_uploader("Upload Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploaded_files and uploaded_class:
        class_folder = os.path.join(UPLOAD_DIR, uploaded_class)
        os.makedirs(class_folder, exist_ok=True)
        for file in uploaded_files:
            with open(os.path.join(class_folder, file.name), "wb") as f:
                f.write(file.read())

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        custom_button = st.markdown("""
            <style>
            div.stButton > button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 24px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("🔄 Uploading the data will take few seconds....!!"):
            updated = move_new_uploads_to_train()
            if updated:
                class_names = train_model()
                st.success("✅ Thanks for Contributing!")
            else:
                st.warning("⚠️ No new data found for training.")


