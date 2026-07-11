import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
import re

@st.cache_data(ttl=10)
def fetch_overview_data():
    sheet_id = "1-kMxEESzFbja7Xsla6W6pxf5DFSq8ejFjeeKUEbF73U"
    gid = "0"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        df["Baseline Progress"] = pd.to_numeric(df["Baseline Progress"], errors='coerce')
        df["Work Progress"] = pd.to_numeric(df["Work Progress"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error fetching Overview Google Sheet: {e}")
        return pd.DataFrame()

STATION_NAMES = [
    "Nadda", "Natun Bazar"
]

def fetch_sheet_names(sheet_id=None):
    return STATION_NAMES

@st.cache_data(ttl=10)
def fetch_station_details(station_name):
    sheet_id = "1uWbBfQ25rBuLat9i9LzFwi3kUbC6bSLhA-5pkhiXMfE"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={station_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        return df
    except Exception:
        return pd.DataFrame()