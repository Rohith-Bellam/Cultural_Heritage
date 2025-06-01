import streamlit as st
import pandas as pd
import os
import re
import time
import base64
from utils.common_css import add_logo

# ========== PATH SETUP ==========
feedback_path = "data/user_feedback.csv"
places_path = "data/Top_Indian_Places_to_Visit.csv"

# Initialize feedback file if not present
if not os.path.exists(feedback_path):
    pd.DataFrame(columns=["Rating", "Location", "Title", "Reviews"]).to_csv(feedback_path, index=False)

# Load datasets
places_df = pd.read_csv(places_path)
feedback_df = pd.read_csv(feedback_path)

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="CultureFlow - Tourist Reviews", layout="wide")
add_logo("data/BGs/logo_app.png")

# Load background
def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = "data/BGs/reviewes.jpg"
bg_base64 = local_image_to_base64(bg_path)

# Global background & sidebar
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.9)), url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.92);
    }}
    </style>
""", unsafe_allow_html=True)

# ======= CUSTOM STYLING =========
st.markdown("""
    <style>
    h1 { font-size: 60px !important; font-weight: 900; color: #FFD700; text-align: center; margin-top: -20px; }
    .searchbox input { font-size: 24px !important; padding: 15px; border-radius: 12px; border: 2px solid #FFD700;}
    .expander-header { font-size: 24px !important; font-weight: 600; color: #FFEE99; }
    </style>
""", unsafe_allow_html=True)

# ========== HEADER ===========
st.markdown("<h1>🇮🇳 CultureFlow - Tourist Reviews & Feedback</h1>", unsafe_allow_html=True)

# ========== SEARCH BAR ===========
with st.container():
    search_query = st.text_input("Search by Name, State, City, Type, Significance",
                                  key="search_input", label_visibility="collapsed",
                                  placeholder="🔍 Type anything to search...",
                                  help="Search across all fields").strip()

# Filter data based on query
filtered_df = places_df.copy()
if search_query:
    pattern = re.compile(search_query, re.IGNORECASE)
    filtered_df = filtered_df[
        filtered_df["Name"].str.contains(pattern) |
        filtered_df["State"].str.contains(pattern) |
        filtered_df["City"].str.contains(pattern) |
        filtered_df["Type"].str.contains(pattern) |
        filtered_df["Significance"].str.contains(pattern)
    ]

# ========== SIDEBAR FILTERS ===========
with st.sidebar:
    st.header("📊 Advanced Filters")

    type_options = sorted(filtered_df['Type'].dropna().unique())
    type_filter = st.selectbox("Filter by Type", ["All"] + type_options)
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['Type'] == type_filter]

    significance_options = sorted(filtered_df['Significance'].dropna().unique())
    significance_filter = st.selectbox("Filter by Significance", ["All"] + significance_options)
    if significance_filter != "All":
        filtered_df = filtered_df[filtered_df['Significance'] == significance_filter]

    min_rating = st.slider("Minimum Google Review Rating", 0.0, 5.0, 4.0, 0.1)
    filtered_df = filtered_df[filtered_df["Google review rating"] >= min_rating]

# ========== MAIN RESULTS ===========
st.markdown("## 🎯 Search Results")

if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.expander(f"📍 {row['Name']} — {row['City']}, {row['State']}", expanded=False):
            st.markdown(f"<span style='font-size:20px'><b>Type:</b> {row['Type']}  |  <b>Significance:</b> {row['Significance']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:20px'><b>Rating:</b> ⭐ {row['Google review rating']}  |  <b>Fee:</b> ₹ {row['Entrance Fee in INR']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:20px'><b>DSLR Allowed:</b> {row['DSLR Allowed']}  |  <b>Best Time:</b> {row['Best Time to visit']}</span>", unsafe_allow_html=True)
else:
    st.warning("❌ No matching results found. Try modifying your search or filters.")

# ========== FLOATING FEEDBACK BANNER ===========
if not feedback_df.empty:
    st.divider()
    placeholder = st.empty()

    for _ in range(len(feedback_df)):
        row = feedback_df.sample(1).iloc[0]
        feedback_html = f"""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: rgba(0,0,0,0.92);
            color: #FFD700;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.8);
            max-width: 450px;
            z-index: 9999;
            font-size: 17px;">
            <h5>📍 {row['Location']} — <small>{row['Title']}</small></h5>
            ⭐ Rating: {row['Rating']}/100
            <p>{row['Reviews']}</p>
        </div>
        """
        placeholder.markdown(feedback_html, unsafe_allow_html=True)
        time.sleep(3)
        placeholder.empty()
else:
    st.warning("No user feedback available yet.")
