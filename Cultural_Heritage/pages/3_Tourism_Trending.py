import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import data_loaders
from sklearn.linear_model import LinearRegression
import numpy as np
import base64
from utils.common_css import add_logo

# Global Color Constants
BACKGROUND = "#000000"  # Fully black background
LEGEND_BG = "#6e8bc4"  # Light blue legend background
FONT_COLOR = "white"
TABLE_HEADER = "#222831"
TABLE_ROW_ODD = "#393E46"
TABLE_ROW_EVEN = "#222831"

# Streamlit Config
st.set_page_config(page_title="Tourism Trends Dashboard", layout="wide")

add_logo("data/BGs/logo_app.png")

def local_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = "data/BGs/trend.jpg"
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

st.markdown("<h1 style='color:#FF9933; text-align:center;'>🇮🇳 Indian Tourism Trends</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#FF9933; text-align:center;'>provided DTV - Domestic Tourist Visitor & FTV - Foreign Tourist Visitor</p>", unsafe_allow_html=True)

# Load Data
df_melted = data_loaders.load_tourist_stats()

# Sidebar Navigation
view_mode = st.sidebar.radio("View Mode", ["Indian Tourism Glory", "Tourism Trends", "Tourism Race", "India Tour stat"])

# Clean Table Function
def show_clean_table(df):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color=TABLE_HEADER,
                    font=dict(color=FONT_COLOR, size=16, family="Arial"),
                    align='center', line_color="#393E46"),
        cells=dict(values=[df[col].tolist() for col in df.columns],
                   fill_color=[[TABLE_ROW_ODD if i % 2 == 0 else TABLE_ROW_EVEN for i in range(len(df))]],
                   font=dict(color=FONT_COLOR, size=14, family="Arial"),
                   align='center', height=35, line_color="#393E46"))
    ])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=min(60 + 35 * len(df), 750), paper_bgcolor=BACKGROUND)
    st.plotly_chart(fig, use_container_width=True)

# =================== SUMMARY DASHBOARD ===================
if view_mode == "Indian Tourism Glory":
    st.sidebar.subheader("Indian Tourism Data")
    selected_year = st.sidebar.selectbox("📅 Select Year", sorted(df_melted["Year"].unique()))
    selected_type = st.sidebar.selectbox("🌐 Select Type", sorted(df_melted["Type"].unique()))
    top_n_states = st.sidebar.slider("📊 Top N States", 5, 36, 10, step=1)

    filtered = df_melted[(df_melted['Year'] == selected_year) & (df_melted['Type'] == selected_type)]
    st.subheader("📊 National Summary")

    total_tourists = filtered["Tourist_Count"].sum()
    top_state = filtered.loc[filtered["Tourist_Count"].idxmax()]
    low_state = filtered.loc[filtered["Tourist_Count"].idxmin()]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tourists", f"{total_tourists:,}")
    col2.markdown(f"<b>Top State:</b><br><span style='color:#2E8B57;font-size:28px;'>{top_state['State']}</span><br><span style='font-size:22px;'>{top_state['Tourist_Count']:,}</span>", unsafe_allow_html=True)
    col3.markdown(f"<b>Lowest State:</b><br><span style='color:#DC143C;font-size:28px;'>{low_state['State']}</span><br><span style='font-size:22px;'>{low_state['Tourist_Count']:,}</span>", unsafe_allow_html=True)

    col_chart, col_graph = st.columns([1, 4])
    with col_chart:
        display_mode = st.selectbox("🔄 Select Visualization Mode:", ["Pie Chart", "Bar Chart", "Table View"])

    top_states = filtered.sort_values(by='Tourist_Count', ascending=False).head(top_n_states)

    with col_graph:
        if display_mode == "Pie Chart":
            pie_fig = px.pie(top_states, names="State", values="Tourist_Count", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Bold)
            pie_fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16, pull=[0.05]*len(top_states))
            pie_fig.update_layout(height=700,
                                   paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
                                   legend=dict(bgcolor=LEGEND_BG, font=dict(color=FONT_COLOR)))
            st.plotly_chart(pie_fig, use_container_width=True)

        elif display_mode == "Bar Chart":
            bar_fig = px.bar(top_states, x="State", y="Tourist_Count", color="Tourist_Count",
                             color_continuous_scale=px.colors.sequential.Viridis_r)
            bar_fig.update_layout(height=600, xaxis_tickangle=-45,
                                   paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
                                   font=dict(color=FONT_COLOR),
                                   legend=dict(bgcolor=LEGEND_BG, font=dict(color=FONT_COLOR)))
            st.plotly_chart(bar_fig, use_container_width=True)

        elif display_mode == "Table View":
            df_display = df_melted.reset_index(drop=True)
            df_display.index = df_display.index + 1
            st.dataframe(df_display, use_container_width=True)

# =================== TRENDS OVER YEARS ===================
elif view_mode == "Tourism Trends":
    st.subheader("📈 Tourism Trends")

    selected_type = st.sidebar.selectbox("Select Type (DTV/FTV)", sorted(df_melted["Type"].unique()))
    state_selection = st.multiselect("Select States", options=df_melted["State"].unique(), default=["Tamil Nadu", "Uttar Pradesh"])
    forecast_enable = st.checkbox("Enable Forecast", value=False)

    trend_df = df_melted[(df_melted["State"].isin(state_selection)) & (df_melted["Type"] == selected_type)]
    trend_df["Year_int"] = trend_df["Year"].astype(int)
    trend_df["Year_str"] = trend_df["Year"].astype(str)
    bright_colors = px.colors.qualitative.Vivid

    fig = go.Figure()
    for idx, state in enumerate(state_selection):
        state_df = trend_df[trend_df["State"] == state].sort_values("Year_int")
        fig.add_trace(go.Scatter(
            x=state_df["Year_str"], y=state_df["Tourist_Count"],
            mode="lines+markers", name=f"{state} Actual",
            marker=dict(size=8, color=bright_colors[idx % len(bright_colors)]),
            line=dict(width=3, color=bright_colors[idx % len(bright_colors)])
        ))

        if forecast_enable and len(state_df) >= 2:
            X = state_df["Year_int"].values.reshape(-1, 1)
            y = state_df["Tourist_Count"].values
            model = LinearRegression().fit(X, y)
            future_years = np.array([state_df["Year_int"].max() + i for i in range(1, 4)]).reshape(-1, 1)
            future_preds = model.predict(future_years)
            min_floor = max(0.5 * min(y), 0)
            forecast_values = [max(min_floor, int(val)) for val in future_preds]
            forecast_years = [str(int(y)) for y in future_years.flatten()]

            fig.add_trace(go.Scatter(
                x=forecast_years, y=forecast_values,
                mode="lines+markers", name=f"{state} Forecast",
                marker=dict(size=8, symbol="circle-open", color=bright_colors[idx % len(bright_colors)]),
                line=dict(width=2, color=bright_colors[idx % len(bright_colors)], dash="dash")
            ))

    fig.update_layout(
        title="Yearly Trends with Forecast",
        xaxis=dict(title="Year", type="category"),
        yaxis_title="Tourist Count",
        plot_bgcolor=BACKGROUND, paper_bgcolor=BACKGROUND, font=dict(color=FONT_COLOR, size=16),
        height=700,
        legend=dict(bgcolor=LEGEND_BG, bordercolor='white', borderwidth=1, font=dict(color=FONT_COLOR))
    )
    st.plotly_chart(fig, use_container_width=True)

# =================== BAR RACE ===================
elif view_mode == "Tourism Race":
    st.subheader("🎯 Interactive Tourism Race Chart (with Year Slider)")

    selected_type = st.sidebar.selectbox("Select Type (DTV/FTV)", sorted(df_melted["Type"].unique()))
    race_df = df_melted[df_melted["Type"] == selected_type]

    available_years = sorted(race_df["Year"].unique())
    selected_year = st.slider("Select Year:", min_value=min(available_years), max_value=max(available_years), value=min(available_years), step=1)

    filtered_df = race_df[race_df["Year"] == selected_year].sort_values(by="Tourist_Count", ascending=False)

    dynamic_height = 700

    bar_fig = px.bar(
        filtered_df,
        x="State",
        y="Tourist_Count",
        color="Tourist_Count",
        color_continuous_scale=px.colors.sequential.Plasma
    )

    bar_fig.update_layout(
        height=dynamic_height,
        plot_bgcolor=BACKGROUND,
        paper_bgcolor=BACKGROUND,
        font=dict(color=FONT_COLOR, size=16),
        margin=dict(l=50, r=50, t=50, b=200),
        legend=dict(bgcolor=LEGEND_BG, font=dict(color=FONT_COLOR)),
        xaxis=dict(tickangle=-45, tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14)),
        title=f"Tourism Data for {selected_year}"
    )

    st.plotly_chart(bar_fig, use_container_width=True)


# =================== FULL DATASET EXPLORER ===================
elif view_mode == "India Tour stat":
    st.subheader("📑 India Tour stat")
    explorer_option = st.sidebar.radio("Select Explorer Mode", ["Table View", "Total Bar Chart (DTV/FTV per State)", "State-wise Yearly Drilldown"])

    if explorer_option == "Table View":
        df_display = df_melted.reset_index(drop=True)
        styler = df_display.style.background_gradient(cmap="Blues", subset=["Tourist_Count"]).format({"Tourist_Count": "{:,}"})
        st.dataframe(styler, use_container_width=True, hide_index=True)

    elif explorer_option == "Total Bar Chart (DTV/FTV per State)":
        selected_type = st.sidebar.selectbox("Select Tourist Type:", sorted(df_melted["Type"].unique()))
        total_agg = df_melted.groupby(["Type", "State"]).sum().reset_index()
        type_df = total_agg[total_agg["Type"] == selected_type].sort_values(by="Tourist_Count", ascending=False)

        fig = px.bar(type_df, x="State", y="Tourist_Count", color="Tourist_Count", color_continuous_scale=px.colors.sequential.Plasma)
        fig.update_layout(xaxis_tickangle=-45, height=600,
                          plot_bgcolor=BACKGROUND, paper_bgcolor=BACKGROUND,
                          font=dict(color=FONT_COLOR),
                          legend=dict(bgcolor=LEGEND_BG, font=dict(color=FONT_COLOR)))
        st.plotly_chart(fig, use_container_width=True)

    elif explorer_option == "State-wise Yearly Drilldown":
        drilldown_state = st.sidebar.selectbox("Select State", sorted(df_melted["State"].unique()))
        drilldown_type = st.sidebar.selectbox("Select Type (DTV/FTV)", sorted(df_melted["Type"].unique()))
        drill_df = df_melted[(df_melted["State"] == drilldown_state) & (df_melted["Type"] == drilldown_type)].sort_values("Year")
        drill_df["Year_int"] = drill_df["Year"].astype(int)
        drill_df["Year"] = drill_df["Year_int"].astype(str)

        col1, col2 = st.columns([3, 1])
        forecast_enable = col2.checkbox("Enable Forecast", value=False)

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=drill_df["Year"], y=drill_df["Tourist_Count"], mode="lines+markers", name="Actual",
                                      line=dict(color="#FF7F0E", width=3), marker=dict(size=8)))

            if forecast_enable and len(drill_df) >= 2:
                X = drill_df["Year_int"].values.reshape(-1, 1)
                y = drill_df["Tourist_Count"].values
                model = LinearRegression().fit(X, y)
                future_years = np.array([drill_df["Year_int"].max() + i for i in range(1, 4)]).reshape(-1, 1)
                future_preds = model.predict(future_years)
                min_floor = max(0, min(y) * 0.5)
                forecast_values = [max(min_floor, int(val)) for val in future_preds]
                forecast_years = [str(int(y)) for y in future_years.flatten()]

                fig.add_trace(go.Scatter(
                    x=forecast_years, y=forecast_values,
                    mode="lines+markers", name="Forecast",
                    line=dict(color="cyan", dash="dash"), marker=dict(size=8)))

            fig.update_layout(
                title=f"{drilldown_state} Yearly Trend ({drilldown_type})",
                xaxis=dict(title="Year", type="category"), yaxis_title="Tourist_Count",
                plot_bgcolor=BACKGROUND, paper_bgcolor=BACKGROUND, font=dict(color=FONT_COLOR),
                height=600, legend=dict(bgcolor=LEGEND_BG, bordercolor='white', borderwidth=1, font=dict(color=FONT_COLOR))
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if forecast_enable and forecast_years:
                forecast_df = pd.DataFrame({"Forecast Year": forecast_years, "Forecast Count": [f"{val:,}" for val in forecast_values]})
                st.subheader("📈 Forecasted Values")
                st.table(forecast_df)
            elif forecast_enable:
                st.warning("Not enough data for forecasting!")
