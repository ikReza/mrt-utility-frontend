import streamlit as st
import streamlit.components.v1 as components # Import this for HTML rendering
from datetime import datetime

from utils.ui import apply_custom_css, hero, section_header, kpi_row, badge
from utils.data_fetcher import fetch_overview_data
from utils.plotly_charts import generate_plotly_chart

# ---------------------------------------------------------------- Page setup
st.set_page_config(
    page_title="Utility Relocation Monitor",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;padding:6px 4px 18px 4px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,#5b5bf6,#12c2a9);
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;">🚆</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                            font-size:0.95rem;color:#fff;">Utility Relocation</div>
                <div style="font-size:0.72rem;color:#9598c9;">Monitor</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- Data
df = fetch_overview_data()

# ---------------------------------------------------------------- Hero
hero(
    eyebrow="Program Overview",
    title="🏠 Utility Relocation Dashboard",
    subtitle="Real-time progress of utility relocation works across all stations"
)

if not df.empty:
    col1, col2, col3 = st.columns(3)
    total_stations = len(df)
    completed = len(df[df["Work Progress"] >= 1.0])
    not_started = len(df[df["Work Progress"] == 0.0])
    
    with col1: st.metric(label="Total Stations", value=total_stations)
    with col2: st.metric(label="Completed", value=f"{completed} / {total_stations}")
    with col3: st.metric(label="Not Started", value=not_started)
        
    st.markdown("")
    st.markdown("### 📈 Station Progress Overview")
    fig = generate_plotly_chart(df)
    st.plotly_chart(fig, width="stretch")
    
    # --- Add the HTML Map Below ---
    st.markdown("---")
    st.markdown("### 🗺️ Route Map")
    
    try:
        # Read the HTML file
        with open("route_map.html", 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Render the HTML map in Streamlit
        st.iframe(html_content, height=1130) # You can adjust the height here
    except FileNotFoundError:
        st.warning("route_map.html not found. Please ensure it is in the same folder.")