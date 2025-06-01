import streamlit as st
import pandas as pd
import os
import base64
from utils import data_loaders
from utils.common_css import add_logo

st.markdown("<h1 style='text-align:center;color:#FFD700;'>📝 Submit New Cultural Data</h1>", unsafe_allow_html=True)
add_logo("data/BGs/logo_app.png")
def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = "data/BGs/feedback.jpg"
bg_base64 = local_image_to_base64(bg_path)

# Main app background
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                    url("data:image/jpg;base64,{bg_base64}");
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
                    url("data:image/jpg;base64,{bg_base64}");
        background-position: center center;
        background-repeat: no-repeat;
        background-size: cover;
    }}
    </style>
""", unsafe_allow_html=True)


category = st.selectbox("Select Dataset to Add To",
    ["Monument/Place Information", "Tourist Stats", "Unified Feedback"])

# ----- Helpers -----
def load_dropdown_options(series):
    """Prepare a clean sorted list for dropdown."""
    return sorted(series.dropna().astype(str).unique())

def smart_input(label, options):
    """Show selectbox first; if empty, show text input."""
    choice = st.selectbox(label, ["Select Existing"] + options)
    if choice == "Select Existing":
        return st.text_input(f"Enter New {label}")
    else:
        return choice

# ----- Monument / Place Information -----
if category == "Monument/Place Information":
    st.header("🕌 Add or Update Monument Entry")

    places_df = data_loaders.load_places()

    monument_list = load_dropdown_options(places_df["Name"])
    state_list = load_dropdown_options(places_df["State"])
    city_list = load_dropdown_options(places_df["City"])
    type_list = load_dropdown_options(places_df["Type"])
    significance_list = load_dropdown_options(places_df["Significance"])
    weekly_off_list = load_dropdown_options(places_df["Weekly_Off"])
    best_time_list = load_dropdown_options(places_df["Best_Time_To_Visit"])
    dslr_list = load_dropdown_options(places_df["Dslr_Allowed"])

    # Smart Inputs
    monument = smart_input("Monument Name", monument_list)
    state = smart_input("State", state_list)
    city = smart_input("City", city_list)
    category_type = smart_input("Type", type_list)
    significance = smart_input("Significance", significance_list)
    weekly_off = smart_input("Weekly Off", weekly_off_list)
    best_time = smart_input("Best Time to Visit", best_time_list)
    dslr = smart_input("DSLR Allowed", dslr_list)

    # Numeric and other fields
    est_year = st.text_input("Establishment Year")
    duration = st.number_input("Time Needed To Visit (in Hours)", 0.0, 10.0, step=0.5)
    rating = st.number_input("Google Review Rating", 0.0, 5.0, step=0.1)
    review_count = st.number_input("Google Reviews (in Lakh)", 0.0, 100.0, step=0.01)
    fee = st.number_input("Entrance Fee (INR)", 0, 10000, step=10)
    airport = st.selectbox("Airport within 50km Radius", ["No", "Yes"])
    image_name = st.text_input("Image File Name")

    # Submit Entry
    if st.button("Submit Monument Entry"):
        new_entry = {
            "Zone": "",  # Future logic for auto-assign if needed
            "State": state,
            "City": city,
            "Name": monument,
            "Type": category_type,
            "Establishment Year": est_year,
            "time needed to visit in hrs": duration,
            "Google review rating": rating,
            "Entrance Fee in INR": fee,
            "Airport with 50km Radius": airport,
            "Weekly Off": weekly_off,
            "Significance": significance,
            "DSLR Allowed": dslr,
            "Number of google review in lakhs": review_count,
            "Best Time to visit": best_time,
            "Image": image_name
        }

        # Duplicate check based on Name + State
        duplicate_check = places_df[
            (places_df["Name"].str.lower() == monument.lower()) &
            (places_df["State"].str.lower() == state.lower())
        ]

        if not duplicate_check.empty:
            idx = duplicate_check.index[0]
            for col, val in new_entry.items():
                places_df.at[idx, col] = val
            st.success("✅ Existing monument updated successfully!")
        else:
            places_df = pd.concat([places_df, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("✅ New monument added successfully!")

        # Save updated data
        file_path = "data/Top_Indian_Places_to_Visit.csv"
        places_df.to_csv(file_path, index=False)
        st.balloons()

# ----- Tourist Stats -----
elif category == "Tourist Stats":
    st.header("➕ Add Tourist Statistics")

    tourist_stats_path = "data/tourist_stats.csv"
    tourist_df = pd.read_csv(tourist_stats_path)

    state_list = list(tourist_df.columns)
    state_list.remove("Year")
    state_list.remove("Type")

    year = st.number_input("Year", min_value=2000, max_value=2100, value=2024, step=1)
    visitor_type = st.selectbox("Visitor Type", ["DTV", "FTV"])
    state = st.selectbox("State", state_list)
    tourists = st.number_input("Tourist Count", min_value=0, step=1)

    if st.button("Submit Tourist Stats"):
        mask = (tourist_df["Year"] == year) & (tourist_df["Type"] == visitor_type)

        if mask.any():
            idx = tourist_df[mask].index[0]
            tourist_df.loc[idx, state] += tourists
        else:
            new_row = {"Year": year, "Type": visitor_type}
            for s in state_list:
                new_row[s] = tourists if s == state else 0
            new_row["Total"] = tourists
            tourist_df = pd.concat([tourist_df, pd.DataFrame([new_row])], ignore_index=True)

        tourist_df["Total"] = tourist_df[state_list].sum(axis=1)
        tourist_df.to_csv(tourist_stats_path, index=False)
        st.success("✅ Tourist statistics updated successfully!")

# ----- Unified Feedback -----
elif category == "Unified Feedback":
    st.header("📋 Submit Unified Feedback")

    feedback_path = "data/user_feedback.csv"

    if not os.path.exists(feedback_path):
        pd.DataFrame(columns=["Rating", "Location", "Title", "Reviews"]).to_csv(feedback_path, index=False)

    rating = st.slider("Rating (1-100)", 1, 100)
    location = st.text_input("Location / Place / Attraction Name")
    title = st.text_input("Describe Place in One Word")
    review = st.text_area("Detailed Review")

    if st.button("Submit Feedback"):
        new_feedback = {
            "Rating": rating,
            "Location": location.strip(),
            "Title": title.strip(),
            "Reviews": review.strip()
        }

        feedback_df = pd.read_csv(feedback_path)
        feedback_df = pd.concat([feedback_df, pd.DataFrame([new_feedback])], ignore_index=True)
        feedback_df.to_csv(feedback_path, index=False)

        st.success(f"✅ Feedback for {location} submitted successfully!")
