import pandas as pd
import streamlit as st

from utils.ui import apply_custom_css
from utils.schedule import (load_stations, load_tasks, enrich,
                            build_payload, render_dashboard, csv_asof)

st.set_page_config(page_title="Station Schedule", page_icon="🛤️", layout="wide")
apply_custom_css()

# this page only: full-width content + readable dropdown text on the dark sidebar
st.markdown("""
<style>
.block-container{max-width:100% !important;padding-left:1.2rem !important;padding-right:1.2rem !important;}
section[data-testid="stSidebar"] [data-baseweb="select"] > div{color:#fff !important;font-weight:600;}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:#cfd0e4 !important;}
</style>
""", unsafe_allow_html=True)

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
    st.divider()
    st.markdown("### Station")

stations = load_stations()
if not stations:
    st.stop()

with st.sidebar:
    station_id = st.selectbox("Station", list(stations),
                              format_func=lambda k: stations[k]["name"],
                              label_visibility="collapsed")

tasks = enrich(load_tasks(), pd.Timestamp(csv_asof()))   # tick date = CSV last edit
df = tasks[tasks["station"] == station_id]

if df.empty:
    st.warning(f"No tasks found for {station_id} in data/tasks.csv.")
    st.stop()

render_dashboard(build_payload(df, station_id, stations[station_id]))