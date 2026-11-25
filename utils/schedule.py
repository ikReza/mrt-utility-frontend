"""Station schedule & progress dashboard — shared logic for the multipage app.

Reads:
    Google Sheet         schedule + lengths (total_len, done_len in metres) via utils/sheet_source.py
                         (falls back to data/tasks.csv if Google is unreachable)
    (from project root):
    data/stations.json   station registry: image + corridor boundary boxes
    images/...           wide corridor drawings (paths from stations.json)

Progress % = done_len ÷ total_len × 100 for a single work item.
The web table shows the REAL total_len / done_len (lm); weight is only used inside the % roll-ups.
Roll-ups (section / station) are WEIGHTED: Σ(done_len × weight) ÷ Σ(total_len × weight).
  total_len = actual length (lm)      weight = effort factor (default 1; BTCL / private cables 0.5)
  e.g. 255 lm BTCL at weight 0.5 counts as 127.5 lm in the section total.
done_len is entered in actual lm and can never exceed total_len.
Planned % (black tick on bars) comes from schedule dates + the "Status as of" date.
stations.json extras (all optional):
    "views":  [{"crop":[x,y,w,h]}, {"crop":[...], "title":"..."}]   crop windows (% of the image); first = main strip,
              the others are miniature insets with true aspect (e.g. one long vertical strip)
    box "dir":"v"                          progress shade runs top->bottom instead of left->right
    box "curve":{"x","w","y","sag","shape"} bent corridor; shape = beam | fixed | parabola; y = centre-line at the ends
    box "path":[[x,y],...]                  free-form centre-line (smoothed);  "thickness" = width in % of image height
    "map_h": "340px"                        taller schematic for this station (default clamp(220px,18vw,360px))
    box "chip_at": 0..1                     where along a curved corridor the % chip sits
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

from utils.sheet_source import read_tasks, tasks_asof

ROOT = Path(__file__).resolve().parents[1]          # project root (folder of Dashboard.py)
DATA_DIR = ROOT / "data"
TASKS_CSV = DATA_DIR / "tasks.csv"
STATIONS_JSON = DATA_DIR / "stations.json"
TEMPLATE = (Path(__file__).parent / "schedule_template.html").read_text(encoding="utf-8")

def csv_asof() -> dt.date:
    """'Plan reference' date = today (a Google Sheet has no file date)."""
    return tasks_asof().date()


AGENCY_COLOR = {
    "drain": "#2E7D46", "dwasa": "#0B6FA8", "titas": "#B8790A", "desco": "#B23A2E",
    "btcl": "#5B4B95", "priv": "#157A6E", "road": "#7A5C1E", "civil": "#3D4F63",
}
STATUS_COLOR = {"Completed": "#2E7D46", "In progress": "#B7791F",
                "Delayed": "#C0392B", "Not started": "#8C887C"}
GROUP_COLOR = {"west": "#1F6FEB", "east": "#E67E22", "road": "#C2185B"}   # corridor-group accent colours
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


def load_tasks() -> pd.DataFrame:
    """Tasks from the Google Sheet (cached ~60 s inside read_tasks)."""
    try:
        df = read_tasks().copy()
    except Exception as e:
        st.error(f"Could not load tasks: {e}")
        return pd.DataFrame()

    if "remarks" not in df.columns:
        df["remarks"] = ""
    df["remarks"] = df["remarks"].fillna("").astype(str)
    if "item" not in df.columns:                      # optional column: sub-parts of a work row
        df["item"] = ""
    df["item"] = df["item"].fillna("").astype(str).str.strip()

    # a mistyped date in the sheet would otherwise crash the page: skip those rows, but say so
    bad = df["start"].isna() | df["end"].isna()
    if bad.any():
        rows = ", ".join(str(i + 2) for i in df.index[bad][:10])      # +2 = sheet row number
        st.warning(f"{int(bad.sum())} sheet row(s) skipped: start/end is not a valid date "
                   f"(sheet row {rows}{' …' if bad.sum() > 10 else ''}). Expected format m/d/yyyy.")
        df = df[~bad].reset_index(drop=True)
    return df


def enrich(df: pd.DataFrame, today: pd.Timestamp) -> pd.DataFrame:
    df = df.copy()
    df["days"] = (df["end"] - df["start"]).dt.days + 1
    elapsed = (today - df["start"]).dt.days + 1
    df["planned_pct"] = (elapsed / df["days"]).clip(0, 1) * 100

    for c in ("total_len", "done_len"):
        if c not in df.columns:
            df[c] = 0
    df["total_len"] = pd.to_numeric(df["total_len"], errors="coerce").fillna(0)
    df["done_len"] = pd.to_numeric(df["done_len"], errors="coerce").fillna(0).clip(lower=0)
    # done can never exceed the total
    df["done_len"] = df["done_len"].where(df["total_len"] <= 0, df["done_len"].clip(upper=df["total_len"]))

    # weight (missing column / blank cell = 1) -> weighted lengths used for roll-ups
    if "weight" not in df.columns:
        df["weight"] = 1.0
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(1.0).clip(lower=0)
    df["w_total"] = df["total_len"] * df["weight"]
    df["w_done"] = df["done_len"] * df["weight"]

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
    """Weighted completed ÷ weighted total metres for a group (None if lengths missing)."""
    t, d = g["w_total"].sum(), g["w_done"].sum()
    if t > 0 and bool((g["total_len"] > 0).all()):
        return float(d / t * 100)
    return None


def status(actual: float, planned: float) -> str:
    if actual >= 99.9:
        return "Completed"
    if planned - actual > DELAY_TOLERANCE:
        return "Delayed"
    return "In progress" if actual > 0 else "Not started"


TIP_NAME = {"priv": "Pvt Cables", "drain": "DNCC Drainage"}


def tip_groups(g: pd.DataFrame) -> list:
    """Hover summary: one row per utility (all DESCO voltages / DWASA sizes / TITAS sizes combined).
    DESWSP stays separate from DWASA because the agency differs. % = weighted done ÷ weighted total."""
    out = []
    for (cls, org), gg in g.sort_values("start").groupby(["cls", "agency"], sort=False):
        if cls in ("civil", "road"):                      # Radiance: excavation vs backfilling
            label = f"{org} – {gg['description'].iloc[0].split(' + ')[0]}"
        else:
            label = TIP_NAME.get(cls, org)
        t, d = gg["w_total"].sum(), gg["w_done"].sum()
        a = float(d / t * 100) if t > 0 else float(gg["actual_pct"].mean())
        pl = wavg(gg, "planned_pct")
        out.append(dict(name=label, color=AGENCY_COLOR.get(cls, "#57534A"),
                        actual=round(a), planned=round(pl), status=status(a, pl),
                        start=gg["start"].min()))
    out.sort(key=lambda x: x.pop("start"))
    return out


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
            tip=tip_groups(g),
            tasks=[dict(agency=r.agency, desc=r.description,
                        start=r.start.strftime("%d %b"), end=r.end.strftime("%d %b"),
                        item=r.item,
                        total=round(float(r.total_len), 1), done=round(float(r.done_len), 1),   # real lm (no weight)
                        days=int(r.days), actual=round(r.actual_pct), planned=round(r.planned_pct),
                        color=AGENCY_COLOR.get(r.cls, "#57534A"), remarks=r.remarks.strip(),
                        status=status(r.actual_pct, r.planned_pct))
                   for r in g.sort_values("start").itertuples()])
    return out


def group_payload(df: pd.DataFrame, station: dict) -> list:
    """West / East / Road-crossing roll-ups. Membership comes from each box's "group" in stations.json
    (e.g. Section-1,2 -> West corridor; Section-3,4,5 -> East corridor; Section-6,7 -> Road crossing).
    % = weighted done / weighted total over every task of the member sections."""
    members = {}
    for k, b in station["boxes"].items():
        members.setdefault(b.get("group") or "Other", []).append(k)
    out = []
    for i, (name, keys) in enumerate(members.items()):
        gdf = df[df["section"].isin(keys)]
        color = next((c for w, c in GROUP_COLOR.items() if w in name.lower()), SEC_PALETTE[i % len(SEC_PALETTE)])
        if gdf.empty:
            out.append(dict(name=name, color=color, sections=keys, actual=0, planned=0, status="Not started",
                            start="—", end="—", tip=[]))
            continue
        a = length_pct(gdf)
        if a is None:
            a = wavg(gdf, "actual_pct")
        pl = wavg(gdf, "planned_pct")
        out.append(dict(name=name, color=color, sections=keys, actual=round(a, 1), planned=round(pl, 1),
                        status=status(a, pl), start=gdf["start"].min().strftime("%d %b"),
                        end=gdf["end"].max().strftime("%d %b %Y"), tip=tip_groups(gdf)))
    return out


def prelim_payload(df: pd.DataFrame) -> list:
    """Rows whose section has no box on the drawing (Preliminary works etc.), one table row each."""
    out = []
    for sec_name, g in df.groupby("section", sort=False):
        a = length_pct(g)
        if a is None:
            a = wavg(g, "actual_pct")
        p = wavg(g, "planned_pct")
        out.append(dict(name=sec_name, actual=round(a, 1), planned=round(p, 1), status=status(a, p),
                        tasks=[dict(agency=r.agency, desc=r.description, item=r.item,
                                    total=round(float(r.total_len), 1), done=round(float(r.done_len), 1),
                                    start=r.start.strftime("%d %b"), end=r.end.strftime("%d %b"),
                                    days=int(r.days), actual=round(r.actual_pct), planned=round(r.planned_pct),
                                    color=AGENCY_COLOR.get(r.cls, "#57534A"), remarks=r.remarks.strip(),
                                    status=status(r.actual_pct, r.planned_pct))
                               for r in g.sort_values("start").itertuples()]))
    return out


def _beam(t: float, shape: str) -> float:
    """Normalised deflection 0..1..0 along a span (t = 0..1)."""
    if shape == "parabola":
        return 4 * t * (1 - t)
    t = min(t, 1 - t)
    if shape == "fixed":                       # both ends clamped, point load at mid-span
        return 12 * t * t - 16 * t ** 3
    return 3 * t - 4 * t ** 3                  # "beam": simply supported, point load at mid-span


def _smooth(pts: list, per: int = 10) -> list:
    """Catmull-Rom smoothing of a hand-drawn point list -> dense polyline."""
    if len(pts) < 3:
        return pts
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            u = k / per
            out.append([round(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u
                                     + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u ** 2
                                     + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3), 3) for j in (0, 1)])
    out.append(list(pts[-1]))
    return out


def box_path(b: dict):
    """Curved corridor: either "path": [[x,y],...] (smoothed) or "curve": {x, w, y, sag, shape}."""
    c = b.get("curve")
    if c:
        n = int(c.get("n", 28))
        return [[round(c["x"] + c["w"] * i / n, 3),
                 round(c["y"] + c.get("sag", 0) * _beam(i / n, c.get("shape", "beam")), 3)] for i in range(n + 1)]
    if b.get("path"):
        return _smooth([list(map(float, q)) for q in b["path"]])
    return None


def build_payload(df: pd.DataFrame, station_id: str, station: dict) -> dict:
    box_keys = set(station["boxes"])
    prelim_df = df[~df["section"].isin(box_keys)]       # e.g. "Preliminary" - no box on the drawing
    df = df[df["section"].isin(box_keys)]               # roll-ups use corridors that have a box
    secs = section_payload(df)
    boxes = {}
    for i, (k, b) in enumerate(station["boxes"].items()):
        path = box_path(b)
        if path:                                           # bounding box of the curve (used for sizing only)
            xs, ys = [q[0] for q in path], [q[1] for q in path]
            b = {**b, "x": min(xs), "y": min(ys), "w": max(xs) - min(xs), "h": max(ys) - min(ys)}
        boxes[k] = dict(x=b["x"], y=b["y"], w=b["w"], h=b["h"],
                        path=path, thick=b.get("thickness", 8), chip_t=b.get("chip_at", 0.5),
                        dir=b.get("dir", "h"),
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
        groups=group_payload(df, station),
        views=station.get("views") or [{"crop": [0, 0, 100, 100]}],
        map_h=station.get("map_h"),
        prelim=prelim_payload(prelim_df),
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


# Injected into the embedded copy only (so it works whatever Streamlit version / CSS selectors are in use):
#  - small side padding so content never touches the rounded frame edge
#  - html background = the page's own paper colour (no stray strip at the edges)
#  - the iframe element itself is framed from inside: full width, cyan border, rounded, glow
PAD_X = 12   # px of horizontal breathing room (raise to 16-20 for more)

_FRAME_CSS = (
    "<style>html,body{margin:0!important}"
    f"body{{padding-left:{PAD_X}px!important;padding-right:{PAD_X}px!important;box-sizing:border-box!important}}"
    "</style>"
)
_FRAME_JS = (
    "<script>(function(){try{"
    "var c=getComputedStyle(document.body).backgroundColor;"
    "if(c&&c!=='rgba(0, 0, 0, 0)'&&c!=='transparent'){document.documentElement.style.background=c;}"
    "var fe=window.frameElement;"
    "if(fe){var s=fe.style;"
    "s.setProperty('display','block');s.setProperty('width','100%');s.setProperty('max-width','none');"
    "s.setProperty('border','1px solid rgba(0,240,255,.45)');s.setProperty('border-radius','16px');"
    "s.setProperty('box-shadow','0 0 0 4px rgba(0,240,255,.06),0 0 38px rgba(0,240,255,.18),0 22px 44px rgba(0,0,0,.5)');"
    "s.setProperty('background',c&&c!=='rgba(0, 0, 0, 0)'?c:'#f4f2ea');}"
    "}catch(e){}})();</script>"
)


def render_dashboard(payload: dict):
    data = json.dumps(payload).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATA__", data)
    html = html.replace("</head>", _FRAME_CSS + "</head>", 1) if "</head>" in html else _FRAME_CSS + html
    html = html.replace("</body>", _FRAME_JS + "</body>", 1) if "</body>" in html else html + _FRAME_JS
    # height=900 is also the CSS hook for iframe[height="900"] in utils/ui.py (the framed light panel)
    components.html(html, height=900, scrolling=False)


def admin_editor(df: pd.DataFrame, station_id: str):
    """LEGACY (not used by the pages): edits the LOCAL data/tasks.csv only.
    Progress is now entered in the Google Sheet, so saving here no longer changes what the app shows."""
    st.divider()
    with st.expander("✏️ Update completed length", expanded=True):
        st.caption("Enter **Done m** (actual lm, max = Total) per task — the item % is done ÷ total; "
                   "section totals apply each item's **Weight**. "
                   "Add **Remarks** only if there is an issue. Everything else is locked.")
        edit_cols = ["section", "agency", "description", "start", "end",
                     "total_len", "weight", "done_len", "actual_pct", "remarks"]
        edited = st.data_editor(
            df[edit_cols], hide_index=True, use_container_width=True, key=f"ed_{station_id}",
            disabled=[c for c in edit_cols if c not in ("done_len", "remarks")],
            column_config={
                "total_len": st.column_config.NumberColumn("Total m", disabled=True, format="%.1f"),
                "weight": st.column_config.NumberColumn("Weight", disabled=True, format="%.2f"),
                "done_len": st.column_config.NumberColumn("Done m", min_value=0, step=0.5, format="%.1f"),
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
            dne = pd.to_numeric(raw["done_len"], errors="coerce").fillna(0).clip(lower=0)
            dne = dne.where(tot <= 0, dne.clip(upper=tot))      # done ≤ total
            raw["done_len"] = dne
            legacy = pd.to_numeric(raw.get("actual_pct", 0), errors="coerce").fillna(0)
            raw["actual_pct"] = (dne / tot * 100).where(tot > 0, legacy).round(1)
            raw.to_csv(TASKS_CSV, index=False)
            st.cache_data.clear()
            st.success("Saved ✓")
            st.rerun()