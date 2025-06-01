import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components
import base64
from utils import data_loaders
from utils.common_css import add_logo

st.set_page_config(page_title="🇮🇳 India Tourism Recommender", layout="wide")


add_logo("data/BGs/logo_app.png")


# ---------- HELPERS ----------
def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------- DATA HANDLER ----------
class DataHandler:
    def __init__(self):
        self.places_df = data_loaders.load_places()
        self.login_df = data_loaders.load_login_data()

    def save_user(self, email, pwd):
        new_user = pd.DataFrame({"Email": [email], "Password": [pwd]})
        self.login_df = pd.concat([self.login_df, new_user], ignore_index=True)
        data_loaders.save_login_data(self.login_df)

    def validate_user(self, email, pwd):
        user = self.login_df[self.login_df["Email"] == email]
        return not user.empty and user.iloc[0]['Password'] == pwd


# ---------- SEARCH ----------
class SearchEngine:
    def __init__(self, df):
        self.df = df

    def search(self, query, state):
        filtered_df = self.df.copy()

        if not query.strip() and state != "All States":
            filtered_df = filtered_df[filtered_df['State'] == state]

        if query.strip():
            pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
            filtered_df = filtered_df[
                filtered_df['Name'].str.contains(pattern) |
                filtered_df['City'].str.contains(pattern) |
                filtered_df['State'].str.contains(pattern)
            ]

        return filtered_df

    def dynamic_filter(self, df, filters):
        for col, value in filters.items():
            if isinstance(value, list) and value:
                df = df[df[col].isin(value)]
            elif isinstance(value, tuple) and len(value) == 2:
                df = df[df[col].between(value[0], value[1])]
        return df


# ---------- AUTH ----------
class Auth:
    def __init__(self, data_handler):
        self.data_handler = data_handler

    def login_ui(self):
        self._add_login_background()
        st.markdown("<h1 style='text-align:center;color:#FFD700;'>🔐 India Tourism Login</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#FFEEAA;'>Register/Login required to access recommendations</p>", unsafe_allow_html=True)

        menu = st.radio("Choose", ["Login", "Register"], horizontal=True)
        st.write(f"**Mode:** {menu}")

        email = st.text_input("📧 Email")
        pwd = st.text_input("🔑 DOB (YYYY-MM-DD)", placeholder="This will act as your password")

        btn_label = "🚪 Login" if menu == "Login" else "📝 Register"
        center_btn = st.columns([2, 3, 2])[1]

        with center_btn:
            if st.button(btn_label, use_container_width=True):
                if menu == "Login":
                    st.session_state.logged_in = True
                    if self.data_handler.validate_user(email, pwd):
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.success("✅ Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Incorrect credentials.")
                else:
                    if email in self.data_handler.login_df["Email"].values:
                        st.warning("⚠️ Email already exists!")
                    else:
                        self.data_handler.save_user(email, pwd)
                        st.success("✅ Registration successful! You can now login.")

    def _add_login_background(self):
        image_path = "data/BGs/login_bg.jpg"
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                            url("data:image/jpg;base64,{encoded}");
                background-position: center;
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
                            url("data:image/jpg;base64,{encoded}");
                background-position: center center;
                background-repeat: no-repeat;
                background-size: cover;
            }}
            </style>
        """, unsafe_allow_html=True)


# ---------- UI ----------
class UI:
    def render(self, df, columns_to_display):
        if df.empty:
            st.warning("⚠️ No results found!")
            return

        view_mode = st.radio("View Mode", ["🃏 Card View", "📊 Table View"], horizontal=True)

        if view_mode == "📊 Table View":
            self._render_table(df, columns_to_display)
        else:
            self._render_cards(df, columns_to_display)

    def _render_cards(self, df, columns_to_display):
        card_html = """
        <style>
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; padding: 10px; }
        .card {
            background: linear-gradient(to bottom right, #1c1c1c, #333);
            color: #fff; border-radius: 15px; padding: 20px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.5);
            text-align: center; transition: 0.4s ease;
        }
        .card:hover { transform: scale(1.05); }
        .card h3 { font-family: 'Orbitron', sans-serif; font-size: 26px; margin: 10px; color: #FFD700; }
        .card p { font-size: 16px; }
        </style>
        <div class="card-grid">
        """
        for _, row in df.iterrows():
            card_html += "<div class='card'>"
            card_html += f"<h3>📍 {row['Name']}</h3><p>📌 {row['City']}, {row['State']}</p>"
            for col in columns_to_display:
                if col not in ['Name', 'City', 'State']:
                    card_html += f"<p><b>{col.replace('_',' ')}:</b> {row[col]}</p>"
            card_html += "</div>"
        card_html += "</div>"
        components.html(card_html, height=900, scrolling=True)

    def _render_table(self, df, columns_to_display):
        table_html = """
        <style>
        .table-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 15px; padding: 15px; }
        .box {
            background: #1b1b1b; color: #fff;
            border: 2px solid #444; padding: 15px;
            border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            transition: 0.3s ease;
        }
        .box:hover { transform: scale(1.03); }
        h4 { color: #FFD700; font-family: 'Orbitron'; font-size: 22px; }
        </style>
        <div class='table-grid'>
        """
        for _, row in df.iterrows():
            table_html += "<div class='box'>"
            table_html += f"<h4>📍 {row['Name']}</h4><p>📌 {row['City']}, {row['State']}</p>"
            for col in columns_to_display:
                if col not in ['Name', 'City', 'State']:
                    table_html += f"<p><b>{col.replace('_',' ')}:</b> {row[col]}</p>"
            table_html += "</div>"
        table_html += "</div>"

        components.html(table_html, height=900, scrolling=True)


# ---------- MAIN APP ----------
class TourismApp:
    def __init__(self):
        self.data_handler = DataHandler()
        self.search_engine = SearchEngine(self.data_handler.places_df)
        self.ui = UI()

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "search_query" not in st.session_state:
            st.session_state.search_query = ""
        if "selected_state" not in st.session_state:
            st.session_state.selected_state = "All States"

    def run(self):
        if not st.session_state.logged_in:
            Auth(self.data_handler).login_ui()
        else:
            self._add_dashboard_background()
            self.dashboard()

    def _add_dashboard_background(self):
        image_path = "data/BGs/logo.png"
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.7)), 
                            url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
            }}
            </style>
        """, unsafe_allow_html=True)

        # Sidebar background
        st.markdown(f"""
            <style>
            section[data-testid="stSidebar"] {{
                background: linear-gradient(to bottom, rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                            url("data:image/png;base64,{encoded}");
                background-position: center center;
                background-repeat: no-repeat;
                background-size: cover;
            }}
            </style>
        """, unsafe_allow_html=True)

    def dashboard(self):
        st.markdown("<h1 style='text-align:center;font-family:Orbitron;color:#FFD700;'>🌏 India Cultural & Tourism Explorer</h1>", unsafe_allow_html=True)

        query = st.text_input("🔎 Search", value=st.session_state.search_query)
        st.session_state.search_query = query

        if not query.strip():
            state_list = ["All States"] + sorted(self.data_handler.places_df["State"].unique())
            selected_state = st.selectbox("Select State", state_list, index=state_list.index(st.session_state.selected_state))
            st.session_state.selected_state = selected_state

        filtered_df = self.search_engine.search(st.session_state.search_query, st.session_state.selected_state)

        columns_available = [col for col in self.data_handler.places_df.columns if col not in ["Name", "City", "State"]]
        selected_cols = st.multiselect("Select additional fields to view:", columns_available, default=[])
        fields_to_display = ["Name", "City", "State"] + selected_cols

        with st.sidebar:
            filters = {}
            if selected_cols:
                st.header("⚙️ Advanced Filters")
            for field in selected_cols:
                if self.data_handler.places_df[field].dtype == "object":
                    options = sorted(self.data_handler.places_df[field].dropna().unique().tolist())
                    filters[field] = st.multiselect(f"{field}", options, default=[])
                elif self.data_handler.places_df[field].dtype in ['int64', 'float64']:
                    min_val = float(self.data_handler.places_df[field].min())
                    max_val = float(self.data_handler.places_df[field].max())
                    filters[field] = st.slider(f"{field}", min_val, max_val, (min_val, max_val))

            filtered_df = self.search_engine.dynamic_filter(filtered_df, filters)

            st.divider()
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.experimental_rerun()

        self.ui.render(filtered_df, fields_to_display)


# --------- RUN ------------
TourismApp().run()
