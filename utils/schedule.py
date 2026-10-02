"""Station schedule & progress dashboard — shared logic for the multipage app.

Reads (from project root):
    data/tasks.csv       schedule + lengths (total_len, done_len in metres)
    data/stations.json   station registry: image + corridor boundary boxes
    images/...           wide corridor drawings (paths from stations.json)

Progress % = done_len ÷ total_len × 100 (lengths are never displayed).
Planned % (black tick on bars) comes from schedule dates + the "Status as of" date.
HTML template: utils/schedule_template.html  (__DATA__ placeholder gets the payload).
"""
import base64
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]          # project root (folder of Dashboard.py)
DATA_DIR = ROOT / "data"
TASKS_CSV = DATA_DIR / "tasks.csv"
STATIONS_JSON = DATA_DIR / "stations.json"
TEMPLATE = (Path(__file__).parent / "schedule_template.html").read_text(encoding="utf-8")

def csv_asof() -> dt.date:
    """'Plan reference' date = the day tasks.csv was last saved."""
    return dt.date.fromtimestamp(TASKS_CSV.stat().st_mtime)

AGENCY_COLOR = {
    "drain": "#2E7D46", "dwasa": "#0B6FA8", "titas": "#B8790A", "desco": "#B23A2E",
    "btcl": "#5B4B95", "priv": "#157A6E", "road": "#7A5C1E", "civil": "#3D4F63",
}
STATUS_COLOR = {"Completed": "#2E7D46", "In progress": "#B7791F",
                "Delayed": "#C0392B", "Not started": "#8C887C"}
SEC_PALETTE = ["#1F6FEB", "#8E44AD", "#E67E22", "#8C564B", "#16A085", "#C2185B", "#566573"]
DELAY_TOLERANCE = 10


def load_stations() -> dict:
    try:
        return json.loads(STATIONS_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError:
        st.error("data/stations.json is missing (expected at project root, next to Dashboard.py).")
    except json.JSONDecodeError as e:
        st.error(f"data/stations.json is not valid JSON — {e}")
    return {}


@st.cache_data
def _read_csv(mtime: float) -> pd.DataFrame:        # mtime busts the cache when the CSV changes
    df = pd.read_csv(TASKS_CSV, parse_dates=["start", "end"])
    if "remarks" not in df.columns:
        df["remarks"] = ""
    df["remarks"] = df["remarks"].fillna("").astype(str)
    return df


def load_tasks() -> pd.DataFrame:
    if not TASKS_CSV.exists():
        st.error("data/tasks.csv is missing (expected at project root).")
        return pd.DataFrame()
    return _read_csv(TASKS_CSV.stat().st_mtime)


def enrich(df: pd.DataFrame, today: pd.Timestamp) -> pd.DataFrame:
    df = df.copy()
    df["days"] = (df["end"] - df["start"]).dt.days + 1
    elapsed = (today - df["start"]).dt.days + 1
    df["planned_pct"] = (elapsed / df["days"]).clip(0, 1) * 100

    for c in ("total_len", "done_len"):
        if c not in df.columns:
            df[c] = 0
    df["total_len"] = pd.to_numeric(df["total_len"], errors="coerce").fillna(0)
    df["done_len"] = pd.to_numeric(df["done_len"], errors="coerce").fillna(0)

    if "actual_pct" not in df.columns:
        df["actual_pct"] = 0.0
    df["actual_pct"] = pd.to_numeric(df["actual_pct"], errors="coerce").fillna(0)
    from_len = (df["done_len"] / df["total_len"] * 100).where(df["total_len"] > 0)
    df["actual_pct"] = from_len.fillna(df["actual_pct"]).clip(0, 100)
    return df


def wavg(g: pd.DataFrame, col: str) -> float:
    """Duration-weighted average (used for planned %)."""
    return float((g[col] * g["days"]).sum() / g["days"].sum()) if len(g) else 0.0


def length_pct(g: pd.DataFrame):
    """Completed ÷ total metres for a group of tasks (None if lengths missing)."""
    t, d = g["total_len"].sum(), g["done_len"].sum()
    if t > 0 and bool((g["total_len"] > 0).all()):
        return float(d / t * 100)
    return None


def status(actual: float, planned: float) -> str:
    if actual >= 99.9:
        return "Completed"
    if planned - actual > DELAY_TOLERANCE:
        return "Delayed"
    return "In progress" if actual > 0 else "Not started"


def section_payload(df: pd.DataFrame) -> dict:
    out = {}
    for sec_name, g in df.groupby("section", sort=True):
        a = length_pct(g)
        if a is None:
            a = wavg(g, "actual_pct")
        p = wavg(g, "planned_pct")
        out[sec_name] = dict(
            actual=round(a, 1), planned=round(p, 1), status=status(a, p),
            start=g["start"].min().strftime("%d %b"), end=g["end"].max().strftime("%d %b %Y"),
            tasks=[dict(agency=r.agency, desc=r.description,
                        start=r.start.strftime("%d %b"), end=r.end.strftime("%d %b"),
                        days=int(r.days), actual=round(r.actual_pct), planned=round(r.planned_pct),
                        color=AGENCY_COLOR.get(r.cls, "#57534A"), remarks=r.remarks.strip(),
                        status=status(r.actual_pct, r.planned_pct))
                   for r in g.sort_values("start").itertuples()])
    return out


def build_payload(df: pd.DataFrame, station_id: str, station: dict) -> dict:
    secs = section_payload(df)
    boxes = {}
    for i, (k, b) in enumerate(station["boxes"].items()):
        boxes[k] = dict(x=b["x"], y=b["y"], w=b["w"], h=b["h"],
                        group=b.get("group", ""),
                        color=b.get("color", SEC_PALETTE[i % len(SEC_PALETTE)]),
                        critical=bool(b.get("critical", False)),
                        chip=b.get("chip", "tl"),
                        short=("C" if k.lower().startswith("corr") else "S")
                              + (re.sub(r"\D", "", k) or str(i + 1)),
                        label=f"{k} · {b.get('group', '').title()}")

    title = re.split(r"\s*[–—-]\s*", station["name"], maxsplit=1)[-1].strip() + " Station"
    ov = length_pct(df)
    if ov is None:
        ov = wavg(df, "actual_pct")
    return dict(
        code=station_id, title=title,
        overall=round(ov, 1),
        status=STATUS_COLOR, sections=secs, boxes=boxes,
        defaultSection=next(iter(boxes)),           # first corridor open on load
        image=image_uri(ROOT / station["image"]),
    )


def image_uri(path: Path) -> str:
    if path.exists():
        return _b64(str(path), path.stat().st_mtime)
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='2400' height='380'>"
           "<rect width='100%' height='100%' fill='#f4f2ea'/>"
           f"<text x='50%' y='52%' text-anchor='middle' font-family='monospace' font-size='22' fill='#8a8575'>"
           f"put station image at {path.name}</text></svg>")
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@st.cache_data
def _b64(path: str, mtime: float) -> str:
    p = Path(path)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def render_dashboard(payload: dict):
    data = json.dumps(payload).replace("</", "<\\/")
    components.html(TEMPLATE.replace("__DATA__", data), height=900, scrolling=False)


def admin_editor(df: pd.DataFrame, station_id: str):
    """Field-engineer entry: edit Done m (and remarks); % is derived on save."""
    st.divider()
    with st.expander("✏️ Update completed length", expanded=True):
        st.caption("Enter **Done m** per task — the % is calculated as done ÷ total. "
                   "Add **Remarks** only if there is an issue. Everything else is locked.")
        edit_cols = ["section", "agency", "description", "start", "end",
                     "total_len", "done_len", "actual_pct", "remarks"]
        edited = st.data_editor(
            df[edit_cols], hide_index=True, use_container_width=True, key=f"ed_{station_id}",
            disabled=[c for c in edit_cols if c not in ("done_len", "remarks")],
            column_config={
                "total_len": st.column_config.NumberColumn("Total m", disabled=True),
                "done_len": st.column_config.NumberColumn("Done m", min_value=0, step=5),
                "actual_pct": st.column_config.NumberColumn("%", disabled=True, format="%.1f"),
                "remarks": st.column_config.TextColumn("Remarks / issue")})
        if st.button("💾 Save progress", type="primary"):
            raw = pd.read_csv(TASKS_CSV)
            for c in ("total_len", "done_len"):
                if c not in raw.columns:
                    raw[c] = 0
            if "remarks" not in raw.columns:
                raw["remarks"] = ""
            raw.loc[edited.index, "done_len"] = pd.to_numeric(edited["done_len"], errors="coerce").fillna(0).values
            raw.loc[edited.index, "remarks"] = edited["remarks"].fillna("").astype(str).values
            tot = pd.to_numeric(raw["total_len"], errors="coerce").fillna(0)
            dne = pd.to_numeric(raw["done_len"], errors="coerce").fillna(0)
            legacy = pd.to_numeric(raw.get("actual_pct", 0), errors="coerce").fillna(0)
            raw["actual_pct"] = (dne / tot * 100).where(tot > 0, legacy).round(1)
            raw.to_csv(TASKS_CSV, index=False)
            st.cache_data.clear()
            st.success("Saved ✓")
            st.rerun()