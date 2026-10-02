import streamlit as st
from utils.ui import apply_custom_css, hero, section_header
from utils.data_fetcher import fetch_overview_data, fetch_station_details, fetch_sheet_names
from utils.plotly_charts import generate_station_corridor_plotly

st.set_page_config(page_title="Station Details", page_icon="📊", layout="wide")
apply_custom_css()

hero(
    eyebrow="Corridor Breakdown",
    title="📊 Station-wise Details",
    subtitle="Select a station to inspect West and East corridor progress"
)

detail_sheet_id = "1uWbBfQ25rBuLat9i9LzFwi3kUbC6bSLhA-5pkhiXMfE"
available_stations = fetch_sheet_names(detail_sheet_id)

if not available_stations:
    st.warning("Could not fetch station sheets. Please check the Google Sheet sharing permissions.")
else:
    col_select, _ = st.columns([2, 3])
    with col_select:
        selected_station = st.selectbox("Select Station", available_stations)
    
    st.markdown("---")
    st.markdown(f"### 🏗️ Detailed View: {selected_station}")
    
    detail_df = fetch_station_details(selected_station)
    
    if not detail_df.empty:
        # Generate and display the Plotly chart
        fig_station = generate_station_corridor_plotly(detail_df, selected_station)
        st.plotly_chart(fig_station, use_container_width=True)
    else:
        st.error(f"Failed to load data for {selected_station}.")