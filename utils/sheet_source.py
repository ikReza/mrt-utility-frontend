"""
Google Sheet -> tasks DataFrame (replaces reading data/tasks.csv).

Edit the sheet online and the Station Schedule page picks it up within
CACHE_SECONDS. If Google can't be reached, the local CSV is used instead.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ----------------------------------------------------------------- settings
SHEET_ID = "1agOewCPe1ZXXNj0zuyJYR5Cjm69nfwaEiB_nd08FFLY"
SHEET_NAME = "Sheet1"                      # the tab name shown at the bottom of the sheet
CACHE_SECONDS = 60                         # how long to reuse the downloaded data
DATE_FORMAT = "%m/%d/%Y"                   # how dates appear in YOUR sheet (9/6/2026 = Sep 6, 2026)
LOCAL_FALLBACK = Path(__file__).resolve().parent.parent / "data" / "tasks.csv"
TIMEZONE = "Asia/Dhaka"

REQUIRED = ["station", "section", "cls", "agency", "description",
            "start", "end", "total_len", "weight", "done_len"]
OPTIONAL = ["remarks", "actual_pct"]       # kept if you add these columns to the sheet

_URLS = [
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}",
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0",
]


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise headers, types and dates so the rest of the app sees clean data."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Sheet is missing column(s): {', '.join(missing)}")

    df = df[REQUIRED + [c for c in OPTIONAL if c in df.columns]].dropna(how="all")
    for c in ["station", "section", "cls", "agency", "description"]:
        df[c] = df[c].astype("string").str.strip()
    df = df[df["station"].notna() & (df["station"] != "")]

    for c in ["start", "end"]:
        s = df[c].astype("string").str.strip()
        parsed = pd.to_datetime(s, format=DATE_FORMAT, errors="coerce")
        # accept ISO dates too (2026-09-06), in case some cells are typed that way
        parsed = parsed.fillna(pd.to_datetime(s, format="%Y-%m-%d", errors="coerce"))
        df[c] = parsed
    for c in ["total_len", "weight", "done_len"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df.reset_index(drop=True)


@st.cache_data(ttl=CACHE_SECONDS, show_spinner=False)
def read_tasks() -> pd.DataFrame:
    """Tasks from the Google Sheet (cached); falls back to data/tasks.csv."""
    last_err = None
    for url in _URLS:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return _clean(pd.read_csv(io.StringIO(r.text), dtype=str))
        except Exception as e:                 # try the next URL
            last_err = e
    if LOCAL_FALLBACK.exists():
        st.warning(f"Google Sheet unavailable ({last_err}). Showing local data/tasks.csv instead.")
        return _clean(pd.read_csv(LOCAL_FALLBACK, dtype=str))
    raise RuntimeError(f"Could not load tasks from Google Sheet: {last_err}")


def tasks_asof() -> pd.Timestamp:
    """'Today' used for progress ticks. A sheet has no file date, so use today's date."""
    return pd.Timestamp.now(tz=TIMEZONE).normalize().tz_localize(None)
