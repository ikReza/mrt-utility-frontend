"""
Thin client for the FastAPI meetings backend (see /FastAPI in this project).

Change API_BASE_URL below once the backend is deployed somewhere other
than localhost (e.g. a Render/Railway URL, or an internal server address).
"""

import os
import requests
import pandas as pd
import streamlit as st

def _get_config(key: str, default: str) -> str:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)

# --------------------------------------------------------------------------
# Point this at wherever `uvicorn main:app` is running.
# Local dev default is http://localhost:8000
API_BASE_URL = _get_config("API_BASE_URL", "http://localhost:8000")
# --------------------------------------------------------------------------

TIMEOUT = 8


@st.cache_data(ttl=15, show_spinner=False)
def fetch_meetings() -> pd.DataFrame:
    """GET /api/meetings -> DataFrame (empty DataFrame on any failure)."""
    try:
        resp = requests.get(f"{API_BASE_URL}/api/meetings", timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return pd.DataFrame(columns=["id", "date", "day", "time",
                                          "meeting_location", "objective",
                                          "remarks", "attendee"])
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except requests.exceptions.RequestException:
        return pd.DataFrame()


def verify_admin_password(password: str):
    """POST /api/admin/verify -> (ok: bool, message: str)"""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/admin/verify",
            json={"password": password},
            timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            return True, "Verified"
        return False, "Incorrect password"
    except requests.exceptions.RequestException as e:
        return False, f"Could not reach the API server ({e})"


def _auth_headers():
    return {"X-Admin-Password": st.session_state.get("admin_password", "")}


def create_meeting(payload: dict):
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/meetings", json=payload,
            headers=_auth_headers(), timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            fetch_meetings.clear()
            return True, "Meeting added."
        return False, resp.json().get("detail", "Failed to add meeting.")
    except requests.exceptions.RequestException as e:
        return False, f"Could not reach the API server ({e})"


def update_meeting(meeting_id: int, payload: dict):
    try:
        resp = requests.put(
            f"{API_BASE_URL}/api/meetings/{meeting_id}", json=payload,
            headers=_auth_headers(), timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            fetch_meetings.clear()
            return True, "Meeting updated."
        return False, resp.json().get("detail", "Failed to update meeting.")
    except requests.exceptions.RequestException as e:
        return False, f"Could not reach the API server ({e})"


def delete_meeting(meeting_id: int):
    try:
        resp = requests.delete(
            f"{API_BASE_URL}/api/meetings/{meeting_id}",
            headers=_auth_headers(), timeout=TIMEOUT,
        )
        if resp.status_code == 200:
            fetch_meetings.clear()
            return True, "Meeting deleted."
        return False, resp.json().get("detail", "Failed to delete meeting.")
    except requests.exceptions.RequestException as e:
        return False, f"Could not reach the API server ({e})"