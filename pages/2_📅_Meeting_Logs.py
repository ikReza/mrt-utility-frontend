import streamlit as st
import pandas as pd

from utils.ui import apply_custom_css, hero, section_header, badge
from utils.meetings_api import (
    fetch_meetings, verify_admin_password,
    create_meeting, update_meeting, delete_meeting,
)

st.set_page_config(page_title="Meeting Logs", page_icon="📅", layout="wide")
apply_custom_css()

# extra CSS just for this page: round the native bordered containers so
# each meeting reads as a card consistent with the rest of the app.
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 16px !important;
        border-color: var(--border) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Session state defaults
# --------------------------------------------------------------------------
st.session_state.setdefault("admin_authenticated", False)
st.session_state.setdefault("admin_password", "")

# --------------------------------------------------------------------------
# Header row: hero + small gear icon for admin login
# --------------------------------------------------------------------------
col_hero, col_gear = st.columns([9, 1])
with col_hero:
    hero(
        eyebrow="Coordination",
        title="Meeting Logs",
        subtitle="A running record of site and coordination meetings, "
                 "grouped by month.",
    )
with col_gear:
    st.write("")
    st.write("")
    with st.popover("⚙️", use_container_width=True):
        if st.session_state.admin_authenticated:
            st.success("Admin mode is active.")
            if st.button("Log out", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.session_state.admin_password = ""
                st.rerun()
        else:
            st.markdown("**Admin Login**")
            pwd = st.text_input("Password", type="password", key="admin_pwd_input")
            if st.button("Unlock", use_container_width=True):
                ok, msg = verify_admin_password(pwd)
                if ok:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_password = pwd
                    st.rerun()
                else:
                    st.error(msg)

is_admin = st.session_state.admin_authenticated

# --------------------------------------------------------------------------
# Dialogs (add / edit / delete) — only reachable by an authenticated admin
# --------------------------------------------------------------------------
@st.dialog("Add Meeting")
def add_meeting_dialog():
    m_date = st.date_input("Date")
    m_time = st.text_input("Time", placeholder="e.g. 10:30 AM")
    m_loc = st.text_input("Location")
    m_obj = st.text_input("Objective")
    m_att = st.text_input("Attendees", placeholder="Comma separated names")
    m_rem = st.text_area("Remarks", height=100)
    if st.button("Save Meeting", type="primary", use_container_width=True):
        if not (m_time and m_loc and m_obj and m_att):
            st.error("Please fill in time, location, objective and attendees.")
        else:
            payload = {
                "date": str(m_date), "time": m_time, "meeting_location": m_loc,
                "objective": m_obj, "remarks": m_rem, "attendee": m_att,
            }
            ok, msg = create_meeting(payload)
            (st.success if ok else st.error)(msg)
            if ok:
                st.rerun()


@st.dialog("Edit Meeting")
def edit_meeting_dialog(row):
    m_date = st.date_input("Date", value=row["date"].date())
    m_time = st.text_input("Time", value=row["time"])
    m_loc = st.text_input("Location", value=row["meeting_location"])
    m_obj = st.text_input("Objective", value=row["objective"])
    m_att = st.text_input("Attendees", value=row["attendee"])
    m_rem = st.text_area("Remarks", value=row.get("remarks") or "", height=100)
    if st.button("Save Changes", type="primary", use_container_width=True):
        payload = {
            "date": str(m_date), "time": m_time, "meeting_location": m_loc,
            "objective": m_obj, "remarks": m_rem, "attendee": m_att,
        }
        ok, msg = update_meeting(int(row["id"]), payload)
        (st.success if ok else st.error)(msg)
        if ok:
            st.rerun()


@st.dialog("Delete Meeting?")
def delete_meeting_dialog(row):
    st.warning(f"This will permanently delete the meeting on "
               f"**{row['date'].strftime('%d %b %Y')}** ({row['objective']}).")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("Delete", type="primary", use_container_width=True):
            ok, msg = delete_meeting(int(row["id"]))
            (st.success if ok else st.error)(msg)
            if ok:
                st.rerun()


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
df = fetch_meetings()

top_l, top_r = st.columns([4, 1])
with top_l:
    section_header("Browse by Month", "Latest month is shown by default")
with top_r:
    if is_admin:
        if st.button("➕ Add Meeting", use_container_width=True):
            add_meeting_dialog()
    else:
        if st.button("🔄", help="Refresh", use_container_width=True):
            fetch_meetings.clear()
            st.rerun()

if df.empty:
    st.info(
        "No meetings yet. Click **➕ Add Meeting** above to create the first one."
        if is_admin else
        "No meetings found, or the API server is unreachable. "
        "Make sure the FastAPI backend is running (`uvicorn main:app`)."
    )
else:
    df = df.sort_values(["date", "time"], ascending=[False, False]).reset_index(drop=True)
    df["month_year"] = df["date"].dt.strftime("%B %Y")
    df["sort_key"] = df["date"].dt.strftime("%Y-%m")

    month_order = (
        df[["month_year", "sort_key"]].drop_duplicates()
        .sort_values("sort_key", ascending=False)["month_year"].tolist()
    )

    selected_month = st.selectbox("Month", month_order, index=0, label_visibility="collapsed")
    month_df = df[df["month_year"] == selected_month]

    st.markdown(
        f"""<div style="margin:4px 0 18px 0;">
                {badge(f"{len(month_df)} meeting{'s' if len(month_df) != 1 else ''} in {selected_month}", "primary")}
            </div>""",
        unsafe_allow_html=True,
    )

    for _, row in month_df.iterrows():
        with st.container(border=True):
            if is_admin:
                col_info, col_edit, col_del = st.columns([10, 1, 1])
            else:
                col_info = st.container()
                col_edit = col_del = None

            with col_info:
                st.markdown(
                    f"""
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
                        {badge(row['date'].strftime('%A · %d %b %Y'), 'primary')}
                        {badge(row['time'], 'accent')}
                        {badge(row['meeting_location'], 'warn')}
                    </div>
                    <div style="font-weight:700;font-size:1.05rem;color:var(--ink);
                                font-family:'Space Grotesk',sans-serif;margin-bottom:4px;">
                        {row['objective']}
                    </div>
                    <div style="color:var(--ink-muted);font-size:0.9rem;margin-bottom:4px;">
                        👥 {row['attendee']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if row.get("remarks"):
                    st.caption(row["remarks"])

            if is_admin:
                with col_edit:
                    if st.button("✏️", key=f"edit_{row['id']}"):
                        edit_meeting_dialog(row)
                with col_del:
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        delete_meeting_dialog(row)