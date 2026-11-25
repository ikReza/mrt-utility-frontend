"""S08 Natun Bazar - utility relocation monitor (read-only).

Place: pages/1_Natun_Bazar_S08.py (run the app with: streamlit run Dashboard.py)
Data: mock data below until data/natun_bazar_status.xlsx exists (project root / data).
      Excel sheets: Progress, Sections, Issues, Contractors (same columns as the mock tables).
      Nobody can edit anything in the browser; you update the Excel file, the page refreshes.
"""
import html
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

XLSX = Path(__file__).resolve().parent.parent / "data" / "natun_bazar_status.xlsx"

# ----------------------------------------------------------------------------
# Mock data (replace by Excel later)
# ----------------------------------------------------------------------------
_P = [  # section, item, factor, qty, actual
    ("S1", "Excavation", 1, 254, 254), ("S1", "DESWSP", 1, 254, 254), ("S1", "Drainage", 1, 254, 254),
    ("S1", "TITAS", 1, 254, 0), ("S1", "DWASA", 1, 254, 0), ("S1", "BTCL+pvt cables", .5, 254, 0),
    ("S1", "DESCO 11kV", 1, 254, 0), ("S1", "Road Restoration", 1, 254, 0),
    ("S2", "Excavation", 1, 456, 456), ("S2", "Drainage", 1, 456, 456), ("S2", "DESCO 132kV", 1, 456, 456),
    ("S2", "DESCO 33kV", 1, 456, 455), ("S2", "DESCO 11kV", 1, 456, 0), ("S2", "DWASA", 1, 456, 456),
    ("S2", "TITAS", 1, 456, 0), ("S2", "Road Restoration", 1, 456, 0),
    ("S3", "Excavation", 1, 140, 140), ("S3", "DESWSP DWASA", 1, 140, 140), ("S3", "TITAS 400", 1, 140, 140),
    ("S3", "TITAS 200", 1, 140, 140), ("S3", "DWASA 450", 1, 140, 0), ("S3", "DWASA 315", 1, 140, 0),
    ("S3", "BTCL+pvt cables", .5, 140, 0), ("S3", "DESCO 11kV", 1, 140, 0), ("S3", "DESCO 33kV", 1, 140, 0),
    ("S3", "Road Restoration", 1, 140, 0),
    ("S4", "Excavation", 1, 120, 70), ("S4", "DNCC Drainage", 1, 120, 0), ("S4", "TITAS 400", 1, 120, 0),
    ("S4", "TITAS 200", 1, 120, 0), ("S4", "DWASA 450", 1, 120, 0), ("S4", "Pvt cables", .5, 120, 0),
    ("S4", "Road Restoration", 1, 120, 0),
    ("S5", "Excavation", 1, 450, 450), ("S5", "DNCC Drainage", 1, 450, 224), ("S5", "TITAS 400", 1, 450, 0),
    ("S5", "TITAS 200", 1, 450, 0), ("S5", "DWASA 450", 1, 450, 0), ("S5", "DWASA 250", 1, 450, 0),
    ("S5", "DWASA 75", 1, 450, 0), ("S5", "BTCL+pvt cables", .5, 450, 50), ("S5", "DESCO 11kV", 1, 450, 0),
    ("S5", "DESCO 33kV", 1, 450, 0), ("S5", "Road Restoration", 1, 450, 0),
    ("S6", "Excavation", 1, 30, 15), ("S6", "TITAS 400", 1, 30, 0), ("S6", "TITAS 200", 1, 30, 0),
    ("S6", "DWASA 450", 1, 30, 0), ("S6", "DWASA 315", 1, 30, 0), ("S6", "BTCL+pvt cables", .5, 30, 0),
    ("S6", "DESCO 11kV", 1, 30, 0), ("S6", "DESCO 33kV", 1, 30, 0), ("S6", "Road Restoration", 1, 30, 0),
    ("S7", "Excavation", 1, 30, 0), ("S7", "DESCO 11kV", 1, 30, 0), ("S7", "DESCO 33kV", 1, 30, 0),
    ("S7", "Road Restoration", 1, 30, 0),
]
MOCK_PROGRESS = pd.DataFrame(_P, columns=["section", "item", "factor", "qty", "actual"])

MOCK_SECTIONS = pd.DataFrame([
    ("S1", "Section-1", "West", "CH 0-254", "On hold", "Waiting for US Embassy telecom line relocation and handover"),
    ("S2", "Section-2", "West", "CH 254-720", "On hold", "TITAS issue"),
    ("S3", "Section-3", "East", "CH 600-730", "On hold", "TITAS connection detail unclear after pipe laying"),
    ("S4", "Section-4", "East", "CH 450-600", "Blocked", "No sheet pile supply; excavated stretch is at risk"),
    ("S5", "Section-5", "East", "CH 0-450", "Blocked", "No sheet pile supply; drainage bypass to be redone in CH 0-90"),
    ("S6", "Section-6", "Crossing", "Mid crossing, near CH 254", "In progress", "Many connections to the east and west"),
    ("S7", "Section-7", "Crossing", "North road crossing", "Not started", "Not started"),
], columns=["section", "name", "corridor", "chainage", "status", "note"])

MOCK_ISSUES = pd.DataFrame([
    ("I-01", "US Embassy telecom relocation holding Section-1", "S1", "US Embassy telecom contractor", "24 ECB", "2026-11-04", "2026-11-04", "Open", "High", "Get a firm handover date in writing"),
    ("I-02", "Sheet pile supply stopped (supplier changed to Anisha Corporation)", "S4, S5", "Anisha Corporation", "24 ECB", "2026-11-04", "2026-11-04", "Open", "High", "Confirm delivery schedule"),
    ("I-03", "TITAS issue holding Section-2", "S2", "TITAS contractor", "24 ECB", "2026-11-10", "", "Open", "High", "Confirm resolution date"),
    ("I-04", "TITAS connection method unclear, CH 600-730", "S3", "TITAS contractor", "24 ECB", "2026-11-12", "", "Open", "Medium", "Freeze connection detail and manhole locations"),
    ("I-05", "Drainage bypass CH 0-90 laid on proposed alignment, redo needed", "S5", "Radiance International", "24 ECB", "2026-11-15", "", "Open", "Medium", "Agree redo method and date"),
    ("I-06", "About 50 m excavated with steel shutter in soft soil", "S4", "Radiance International", "24 ECB", "2026-11-18", "", "Open", "High", "Safety inspection; no more excavation until sheet piles arrive"),
    ("I-07", "CH 90-200 RCC drainage relocation not required", "S5", "Drainage contractor", "24 ECB", "2026-11-18", "", "Monitoring", "Low", "Record the scope reduction"),
    ("I-08", "CH 450-470 connections deferred to mid crossing", "S4, S5", "Radiance International", "24 ECB", "2026-11-20", "", "Monitoring", "Low", "Plan connection sequence"),
    ("I-09", "South crossing complete, side connections remain", "Crossing", "Radiance International", "24 ECB", "2026-11-20", "", "Monitoring", "Low", "List remaining connections"),
], columns=["id", "issue", "section", "owner", "reported_via", "raised", "due", "status", "priority", "next_action"])

MOCK_CONTRACTORS = pd.DataFrame([
    ("Sheet piling", "Anisha Corporation", "Active", "Current supplier, no supply for 3+ weeks"),
    ("Sheet piling (previous)", "Dream Infrastructure Limited", "Replaced", "Installed 130 lm in Section-1"),
    ("Civil works", "Radiance International", "Active", "Excavation and civil works"),
    ("Drainage (DNCC)", "", "", "HDPE and RCC drainage"),
    ("DWASA water", "", "", "450 / 315 / 250 / 75 mm"),
    ("TITAS gas", "", "", "400 mm and 200 mm"),
    ("DESCO power", "", "", "132 kV, 33 kV, 11 kV"),
    ("BTCL and private cables", "", "", "Telecom and private cables"),
    ("Road restoration", "", "", "After utilities are complete"),
], columns=["package", "contractor", "status", "note"])
# All packages are appointed through 24 ECB, the delegated agency.


def _stamp():
    return XLSX.stat().st_mtime if XLSX.exists() else 0


@st.cache_data
def load(stamp):
    """Reads the Excel file if present (re-read whenever the file is saved), else mock data."""
    mock = not XLSX.exists()
    if mock:
        prog, sec, iss, con = MOCK_PROGRESS, MOCK_SECTIONS, MOCK_ISSUES, MOCK_CONTRACTORS
    else:
        x = pd.read_excel(XLSX, sheet_name=None)
        prog, sec, iss, con = x["Progress"], x["Sections"], x["Issues"], x["Contractors"]
    prog = prog[["section", "item", "factor", "qty", "actual"]].dropna(subset=["section", "item"]).copy()
    prog["section"] = prog["section"].astype(str).str.strip()
    sec, iss, con = sec.copy(), iss.copy(), con.copy()
    canon = {k.lower(): k for k in COL}
    sec["status"] = sec["status"].astype(str).str.strip().map(lambda v: canon.get(v.lower(), v))
    for c in ("raised", "due"):
        iss[c] = pd.to_datetime(iss[c], errors="coerce").dt.date
    iss = iss.dropna(subset=["id"]).fillna({"priority": "Medium", "owner": "", "reported_via": "", "next_action": ""})
    iss["status"] = iss["status"].astype(str).str.strip().str.capitalize()
    return prog, sec, iss, con.fillna(""), mock


# ----------------------------------------------------------------------------
# Theme and helpers
# ----------------------------------------------------------------------------
TXT, MUT = "#E8EEFF", "#8A97B8"
CY, MINT, AMB, PINK, VIO, GREY = "#25E8FF", "#2BFFB0", "#FFB224", "#FF3D71", "#9B6BFF", "#6A7794"
RGB = {CY: "37,232,255", MINT: "43,255,176", AMB: "255,178,36", PINK: "255,61,113", VIO: "155,107,255", GREY: "106,119,148"}
COL = {"Complete": MINT, "In progress": CY, "On hold": AMB, "Blocked": PINK, "Not started": GREY}
STALLED = ("On hold", "Blocked")
PRIORITY = {"High": 0, "Medium": 1, "Low": 2}
GROUPS = ["Excavation", "Drainage", "TITAS gas", "DWASA water", "DESCO power", "Telecom and cables", "Road restoration"]
GEOM = {"S1": ("W", 0, 254), "S2": ("W", 254, 710), "S5": ("E", 0, 450), "S4": ("E", 450, 570), "S3": ("E", 570, 710)}
CROSS = {"S6": 254, "S7": 710}  # position along the plan, measured from the south end
e = html.escape


def pct(done, total):
    return round(100.0 * float(done) / float(total), 1) if total else 0.0


def group_of(item):
    n = item.strip().lower()
    if n.startswith("excavation"): return "Excavation"
    if "drainage" in n or n.startswith("deswsp"): return "Drainage"
    if n.startswith("titas"): return "TITAS gas"
    if n.startswith("dwasa"): return "DWASA water"
    if n.startswith("desco"): return "DESCO power"
    if "cable" in n: return "Telecom and cables"
    if n.startswith("road"): return "Road restoration"
    return item


def prepare(prog):
    df = prog.copy()
    df["f_qty"] = df["factor"] * df["qty"]
    df["f_actual"] = df["factor"] * df["actual"]
    df["group"] = df["item"].map(group_of)
    return df


def section_status(row, p):
    """Complete follows the numbers; hold / blocked / in progress come from the Sections sheet."""
    return "Complete" if p >= 99.5 else row["status"]


def plan_svg(sections, sec_pct, open_n):
    st_of = {r.section: section_status(r._asdict(), sec_pct[r.section]) for r in sections.itertuples()}
    info = sections.set_index("section")
    X = lambda ch: 60 + ch * 1.25  # distance from the south end -> x
    o = ["""<svg viewBox="0 0 1000 385" width="100%" role="img" aria-label="Station corridor plan, south to north">
<defs>
<filter id="glow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="hOnhold" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3.5" height="9" fill="rgba(255,178,36,.22)"/></pattern>
<pattern id="hBlocked" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3.5" height="9" fill="rgba(255,61,113,.26)"/></pattern>
</defs>
<text x="60" y="14" class="mut">South</text><text x="940" y="14" class="mut" text-anchor="end">North</text>
<text x="60" y="40" class="cor">West corridor</text>
<text x="940" y="40" class="mut" text-anchor="end">Chainage 0 at the south end, rising north</text>
<text x="60" y="372" class="cor">East corridor</text>
<text x="940" y="372" class="mut" text-anchor="end">Chainage 0 at the north end, rising south</text>"""]
    Y = {"W": (92, 62, 66, 82), "E": (236, 62, 331, 316)}  # band y, height, chainage-text y, status-text y

    def pin(x, y, sid):
        n = open_n.get(sid, 0)
        if n:
            o.append(f'<g><title>{n} open issue(s)</title><circle cx="{x}" cy="{y}" r="10" fill="#060913" stroke="{TXT}" stroke-width="1.5"/>'
                     f'<text x="{x}" y="{y + 4}" text-anchor="middle" class="pin">{n}</text></g>')

    for sid, ch in CROSS.items():  # crossings first so band ends sit on top of them
        x, status, p = X(ch), st_of[sid], sec_pct[sid]
        col, h = COL[status], 82
        o.append(f'<rect x="{x - 11}" y="154" width="22" height="{h}" fill="#111B30"/>')
        if status in STALLED: o.append(f'<rect x="{x - 11}" y="154" width="22" height="{h}" fill="url(#h{status.replace(" ", "")})"/>')
        o.append(f'<rect x="{x - 11}" y="{154 + h - h * p / 100}" width="22" height="{h * p / 100}" fill="{col}" filter="url(#glow)"/>'
                 f'<rect x="{x - 11}" y="154" width="22" height="{h}" fill="none" stroke="{col}" stroke-width="1.6"/>')
        sx, anc = (x + 18, "start") if ch < 500 else (x - 18, "end")
        o.append(f'<text x="{sx}" y="188" text-anchor="{anc}" class="lab">{sid} {e(str(info.loc[sid, "name"]))}</text>'
                 f'<text x="{sx}" y="210" text-anchor="{anc}" class="big" fill="{col}">{p:.0f}%</text>'
                 f'<text x="{sx}" y="226" text-anchor="{anc}" class="cap" fill="{col}">{e(status.lower())}</text>')
        pin(x + (11 if ch < 500 else -11), 162, sid)
    o.append(f'<rect x="49" y="154" width="22" height="82" fill="{MINT}" opacity=".9" filter="url(#glow)"/>'
             f'<text x="78" y="188" class="lab">South crossing</text><text x="78" y="206" class="cap" fill="{MINT}">complete, side connections remain</text>')

    for sid, (side, a, b) in GEOM.items():
        y, h, cy, sy = Y[side]
        lo, hi = (X(a), X(b)) if side == "W" else (X(710 - b), X(710 - a))  # east runs north to south
        x0, x1 = lo + 1.5, hi - 1.5
        w, p, status = x1 - x0, sec_pct[sid], st_of[sid]
        col = COL[status]
        o.append(f'<rect x="{x0}" y="{y}" width="{w}" height="{h}" rx="7" fill="#111B30"/>')
        if status in STALLED: o.append(f'<rect x="{x0}" y="{y}" width="{w}" height="{h}" rx="7" fill="url(#h{status.replace(" ", "")})"/>')
        o.append(f'<rect x="{x0}" y="{y}" width="{w * p / 100}" height="{h}" rx="7" fill="{col}" opacity=".9" filter="url(#glow)"/>'
                 f'<rect x="{x0}" y="{y}" width="{w}" height="{h}" rx="7" fill="none" stroke="{col}" stroke-width="1.6"/>'
                 f'<rect x="{x0 + 7}" y="{y + 8}" width="62" height="{h - 16}" rx="5" fill="#060913" opacity=".86"/>'
                 f'<text x="{x0 + 14}" y="{y + 25}" class="lab">{sid}</text>'
                 f'<text x="{x0 + 14}" y="{y + h - 14}" class="big" fill="{col}">{p:.0f}%</text>'
                 f'<text x="{x0 + 2}" y="{cy}" class="mut">{e(str(info.loc[sid, "chainage"]))}</text>'
                 f'<text x="{x0 + 2}" y="{sy}" class="cap" fill="{col}">{e(str(info.loc[sid, "name"]))}: {e(status.lower())}</text>')
        pin(x1 - 14, y + 14, sid)
    o.append("</svg>")
    return "".join(o)


def tone(p):
    return MINT if p >= 99.5 else CY if p > 0 else PINK


def cell(p, cls="c", c=None):
    if p is None:
        return "<td class='na'>-</td>"
    c = c or tone(p)
    rgb = RGB[c]
    fill = f"linear-gradient(90deg,rgba({rgb},.45) {p}%,rgba({rgb},{.16 if p == 0 else .08}) {p}%)"
    glow = ",0 0 14px rgba(%s,.30)" % rgb if "tot" in cls else ",0 0 9px rgba(%s,.18)" % rgb if "ft" in cls else ""
    return f"<td class='{cls}' style='background:{fill};color:{c};box-shadow:inset 0 0 0 1px rgba({rgb},.5){glow}'>{p:.0f}%</td>"


def matrix(df, sections, sec_pct, status):
    head = "".join(f"<th>{g}</th>" for g in GROUPS)
    rows = []
    for s in sections.itertuples():
        d, tds = df[df.section == s.section], []
        for g in GROUPS:
            x = d[d.group == g]
            tds.append(cell(None if x.empty else pct(x.f_actual.sum(), x.f_qty.sum())))
        dot = f"<i class='dot' style='background:{COL.get(status[s.section], GREY)}'></i>"
        rows.append(f"<tr><td class='rh'>{dot}{e(s.name)}<small>{e(str(s.corridor).lower())}</small></td>{''.join(tds)}{cell(sec_pct[s.section], 'c tot')}</tr>")
    foot = []
    for g in GROUPS:
        x = df[df.group == g]
        foot.append(cell(None if x.empty else pct(x.f_actual.sum(), x.f_qty.sum()), "c ft"))
    overall = pct(df.f_actual.sum(), df.f_qty.sum())
    corner = cell(overall, "c tot ft", VIO).replace(f"{overall:.0f}%</td>", f"{overall:.1f}%</td>")
    foot_row = f"<tr class='sep'><td class='rh'><i class='dot' style='background:{VIO}'></i>All sections<small>weighted</small></td>{''.join(foot)}{corner}</tr>"
    return (f"<div class='panel' style='overflow-x:auto'><table class='mx'><tr><th></th>{head}<th class='tt'>Section total</th></tr>"
            f"{''.join(rows)}{foot_row}</table></div>")


def bar(label, value):
    col = MINT if value >= 99.5 else CY if value > 0 else GREY
    return (f"<div class='ibar'><div>{e(label)}</div><div class='tr'><i style='width:{value}%;background:{col};box-shadow:0 0 10px {col}'></i></div>"
            f"<div class='pv' style='color:{col}'>{value:.0f}%</div></div>")


def tile(label, value, sub, col):
    return f"<div class='tile'><i class='acc' style='background:{col};box-shadow:0 0 14px {col}'></i><div class='tl'>{label}</div><div class='tv' style='color:{col}'>{value}</div><div class='ts'>{sub}</div></div>"


def issue_html(r, today):
    days = (today - r.raised).days if pd.notna(r.raised) else None
    due_txt, cls = "no date set", ""
    if pd.notna(r.due):
        late = (today - r.due).days
        due_txt, cls = (f"{late} d overdue", "od") if (late > 0 and r.status == "Open") else (r.due.strftime("%d %b"), "")
    stripe = {"High": PINK, "Medium": AMB, "Low": GREY}.get(r.priority, GREY)
    if r.status == "Resolved": stripe = MINT
    sub = f"open {days} d" if days is not None else ""
    return (f"<div class='isu'><div class='bar' style='background:{stripe};box-shadow:0 0 14px {stripe}'></div>"
            f"<div><div class='t'>{e(r.issue)}</div><div class='m'>Next: {e(r.next_action)}</div></div>"
            f"<div class='x'><div>{e(r.owner)}</div><div class='m'>via {e(r.reported_via)}</div></div>"
            f"<div class='x'><span class='chip'>{e(str(r.section))}</span></div>"
            f"<div class='n {cls}'>{due_txt}<div class='m'>{sub}</div></div></div>")


CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#060913;--surf:#0C1322;--surf2:#111B30;--line:rgba(130,170,255,.16);--txt:#E8EEFF;--mut:#8A97B8;--cy:#25E8FF;--vio:#9B6BFF;--pink:#FF3D71}
html,body,.stApp,[class*="css"]{font-family:'DM Sans',system-ui,sans-serif;color:var(--txt)}
.stApp{background:radial-gradient(1100px 500px at 85% -10%,rgba(155,107,255,.16),transparent 60%),radial-gradient(900px 500px at 0% 0%,rgba(37,232,255,.10),transparent 55%),var(--bg)}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1260px;padding:1.2rem 1.4rem 3rem}
h1,h2,h3,.tv,.big,.brand b,.pv{font-family:'Space Grotesk',sans-serif}
.topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;padding:.2rem 0 .9rem}
.brand{display:flex;align-items:center;gap:.8rem}
.logo{width:38px;height:38px;border-radius:11px;background:conic-gradient(from 210deg,#25E8FF,#9B6BFF,#FF3D71,#25E8FF);box-shadow:0 0 22px rgba(37,232,255,.45);position:relative}
.logo::after{content:'';position:absolute;inset:3px;border-radius:8px;background:#060913}
.logo::before{content:'';position:absolute;left:9px;right:9px;top:17px;height:4px;border-radius:2px;background:#25E8FF;box-shadow:0 0 8px #25E8FF;z-index:2}
.brand b{font-size:1.35rem;letter-spacing:-.01em;display:block;line-height:1.1}
.brand small{color:var(--mut);font-size:.82rem}
.tag{font-size:.78rem;font-weight:600;padding:5px 11px;border-radius:999px;border:1px solid rgba(255,178,36,.5);color:#FFB224;background:rgba(255,178,36,.08)}
div[data-testid="stRadio"]>div[role="radiogroup"]{gap:.3rem;background:rgba(12,19,34,.8);border:1px solid var(--line);border-radius:14px;padding:5px;display:inline-flex;flex-wrap:wrap}
div[data-testid="stRadio"] label{padding:.5rem 1.2rem;border-radius:10px;cursor:pointer;margin:0;transition:background .15s}
div[data-testid="stRadio"] label>div:first-child{display:none}
div[data-testid="stRadio"] label p{font-weight:600;color:var(--mut);font-size:.95rem;margin:0}
div[data-testid="stRadio"] label:hover p{color:var(--txt)}
div[data-testid="stRadio"] label:has(input:checked){background:linear-gradient(135deg,rgba(37,232,255,.22),rgba(155,107,255,.24));box-shadow:0 0 0 1px rgba(37,232,255,.55),0 0 18px rgba(37,232,255,.25)}
div[data-testid="stRadio"] label:has(input:checked) p{color:#fff}
.hero{display:grid;grid-template-columns:auto 1fr;gap:1rem;margin:1.1rem 0 .4rem}
.panel,.ringcard,.tile{background:linear-gradient(180deg,var(--surf2),var(--surf));border:1px solid var(--line);border-radius:16px}
.panel{padding:.7rem .8rem}
.ringcard{display:flex;align-items:center;gap:1.2rem;padding:1rem 1.4rem}
.ring{width:132px;height:132px;border-radius:50%;display:grid;place-items:center;box-shadow:0 0 34px rgba(37,232,255,.28)}
.ring i{width:104px;height:104px;border-radius:50%;background:#0A1120;display:grid;place-items:center;font-style:normal;font-family:'Space Grotesk';font-weight:700;font-size:1.75rem}
.ringcard .tl{font-weight:600;font-size:1.05rem}.ringcard .ts{color:var(--mut);font-size:.84rem;max-width:170px}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem}
.tile{padding:1rem 1.1rem;position:relative;overflow:hidden}
.tile .acc{position:absolute;left:0;top:14%;bottom:14%;width:3px;border-radius:3px}
.tl{color:var(--mut);font-size:.84rem;font-weight:500}.tv{font-size:2.3rem;font-weight:700;line-height:1.15;text-shadow:0 0 18px currentColor}.ts{color:var(--mut);font-size:.8rem}
h3.sec{font-family:'Space Grotesk';font-size:1.1rem;font-weight:600;margin:1.7rem 0 .7rem;display:flex;align-items:center;gap:.6rem}
h3.sec::before{content:'';width:22px;height:3px;border-radius:2px;background:linear-gradient(90deg,#25E8FF,#9B6BFF);box-shadow:0 0 10px #25E8FF}
.mx{width:100%;border-collapse:separate;border-spacing:4px;font-size:.88rem}
.mx th{font-weight:600;color:var(--mut);text-align:center;padding:6px 6px;font-size:.78rem}.mx th.tt{color:#C8B8FF}
.mx td.c{padding:11px 6px;border-radius:8px;text-align:center;font-weight:600;font-family:'Space Grotesk'}
.mx td.tot{font-size:1rem}
.mx td.na{text-align:center;color:#3A4663}
.mx td.rh{text-align:left;font-weight:600;white-space:nowrap;padding:0 10px 0 4px}.mx td.rh small{color:var(--mut);font-weight:400;margin-left:8px}
.mx tr.sep td{padding-top:12px}.mx tr.sep td.rh{padding-top:12px}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:9px;box-shadow:0 0 8px currentColor}
.isu{display:grid;grid-template-columns:4px 1fr 160px 80px 100px;gap:1rem;align-items:center;background:var(--surf);
 border:1px solid var(--line);border-radius:12px;padding:.75rem 1rem .75rem 0;margin-bottom:.5rem;overflow:hidden;font-size:.88rem}
.isu .bar{align-self:stretch}
.isu .t{font-weight:600}.isu .m{color:var(--mut);font-size:.8rem;font-weight:400}.isu .n{text-align:right;font-weight:600;font-family:'Space Grotesk'}
.od{color:#FF3D71}
div[data-testid="stWidgetLabel"] p{color:var(--mut);font-weight:600}
div[data-baseweb="select"]>div{background:#0C1322;border:1px solid rgba(37,232,255,.5);border-radius:12px;box-shadow:0 0 12px rgba(37,232,255,.25);transition:box-shadow .15s,border-color .15s}
div[data-baseweb="select"]>div:hover,div[data-baseweb="select"]>div:focus-within{border-color:#25E8FF;box-shadow:0 0 0 1px #25E8FF,0 0 24px rgba(37,232,255,.6)}
span[data-baseweb="tag"]{background:linear-gradient(135deg,rgba(155,107,255,.30),rgba(37,232,255,.16))!important;border:1px solid rgba(155,107,255,.75);border-radius:8px;box-shadow:0 0 10px rgba(155,107,255,.4)}
span[data-baseweb="tag"] span,span[data-baseweb="tag"] svg{color:#E8EEFF!important;fill:#E8EEFF!important}
div[data-baseweb="popover"]>div,div[data-baseweb="popover"] ul[role="listbox"]{background:#0C1322!important;border-radius:12px}
div[data-baseweb="popover"] ul[role="listbox"]{border:1px solid rgba(37,232,255,.45);box-shadow:0 0 24px rgba(37,232,255,.22)}
li[role="option"]{background:transparent!important;color:#E8EEFF!important}
li[role="option"]:hover,li[role="option"][aria-selected="true"]{background:rgba(37,232,255,.15)!important}
.crow{display:grid;grid-template-columns:190px 1fr 110px;gap:1rem;align-items:center;background:linear-gradient(180deg,var(--surf2),var(--surf));border:1px solid var(--line);border-radius:14px;padding:.85rem 1.1rem;margin-bottom:.6rem}
.crow .pk{font-family:'Space Grotesk';font-weight:600}.crow .st{text-align:right}
.cn2{display:inline-block;padding:.5rem .9rem;border-radius:12px;border:1px solid var(--line);background:var(--bg)}
.cn2 b{display:block;font-family:'Space Grotesk';font-size:1rem}.cn2 small{color:var(--mut);font-size:.78rem}
.cn2.dim b{color:var(--mut);font-weight:500}
.cn2.old{opacity:.6;border-style:dashed}.cn2.old b{text-decoration:line-through;text-decoration-color:rgba(255,61,113,.8)}
.cn2.new{border-color:rgba(43,255,176,.6);box-shadow:0 0 16px rgba(43,255,176,.28)}
.swap{display:flex;align-items:center;gap:1rem;flex-wrap:wrap}
.parr{display:inline-flex;align-items:center;gap:6px;color:#25E8FF}
.parr b{width:7px;height:7px;border-radius:50%;background:currentColor;box-shadow:0 0 8px currentColor;animation:hop 1.1s infinite ease-in-out}
.parr b:nth-child(2){animation-delay:.15s}.parr b:nth-child(3){animation-delay:.3s}
.parr i{font-style:normal;font-size:1.7rem;line-height:1;text-shadow:0 0 12px currentColor;animation:nudge 1.1s infinite ease-in-out;animation-delay:.45s}
@keyframes hop{0%,100%{transform:translateY(0);opacity:.45}40%{transform:translateY(-8px);opacity:1}}
@keyframes nudge{0%,100%{transform:translateX(0) rotate(0)}50%{transform:translateX(7px) rotate(-10deg)}}
@media (prefers-reduced-motion:reduce){.parr b,.parr i{animation:none}}
.chip{font-size:.74rem;font-weight:600;padding:3px 9px;border-radius:999px;background:rgba(155,107,255,.15);color:#C8B8FF;border:1px solid rgba(155,107,255,.35)}
.ibar{display:grid;grid-template-columns:190px 1fr 48px;gap:.8rem;align-items:center;font-size:.86rem;margin:7px 0}
.ibar .tr{height:8px;background:#16213B;border-radius:4px;overflow:hidden}.ibar .tr i{display:block;height:100%;border-radius:4px}.pv{text-align:right;font-weight:600}
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:.8rem}
.cc{background:linear-gradient(180deg,var(--surf2),var(--surf));border:1px solid var(--line);border-radius:14px;padding:1rem 1.1rem;border-top:2px solid var(--c)}
.cc .ch{color:var(--mut);font-size:.8rem}.cc .cn{font-family:'Space Grotesk';font-size:1.1rem;font-weight:600;margin:.25rem 0}.cc .cm{color:var(--mut);font-size:.82rem;margin-bottom:.6rem}
.flow{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin:.2rem 0 1rem}
.flow span.n{padding:.45rem .9rem;border-radius:999px;border:1px solid var(--line);background:var(--surf2);font-weight:600;font-size:.86rem}
.flow span.a{color:#25E8FF;text-shadow:0 0 10px #25E8FF}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:12px;background:var(--surf)}
@media (max-width:900px){.crow{grid-template-columns:1fr}.crow .st{text-align:left}.hero{grid-template-columns:1fr}.tiles{grid-template-columns:repeat(2,1fr)}.isu{grid-template-columns:4px 1fr}.isu .x{display:none}}
"""

PLAN_CSS = """@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&family=Space+Grotesk:wght@600;700&display=swap');
body{margin:0;font-family:'DM Sans',sans-serif;background:transparent}
.w{background:linear-gradient(180deg,#111B30,#0C1322);border:1px solid rgba(130,170,255,.16);border-radius:16px;padding:10px 14px 12px}
.mut{font-size:12px;fill:#8A97B8}.cor{font-size:14px;font-weight:700;fill:#E8EEFF;font-family:'Space Grotesk'}.lab{font-size:12px;font-weight:600;fill:#E8EEFF}
.big{font-size:20px;font-weight:700;font-family:'Space Grotesk'}.cap{font-size:12px;font-weight:600}.pin{font-size:11px;font-weight:700;fill:#fff}
.lg{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:#8A97B8;padding:6px 4px 0}.lg b{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:-1px}"""


def ring(p):
    return f"<div class='ring' style='background:conic-gradient(#25E8FF 0,#9B6BFF {p}%,#16213B {p}% 100%)'><i>{p:.1f}%</i></div>"


def contractor_rows(con):
    """One row per package. A row named '<package> (previous)' is shown as old -> new on the package's row."""
    pkg = lambda r: str(r.package).strip()
    prev = {pkg(r).replace(" (previous)", ""): r for r in con.itertuples() if pkg(r).endswith("(previous)")}
    sc = {"Active": MINT, "Replaced": GREY, "On hold": AMB}

    def box(name, note, cls=""):
        shown = e(name) if name else "To be confirmed"
        return f"<div class='cn2 {cls if name else 'dim'}'><b>{shown}</b><small>{e(note)}</small></div>"

    rows = []
    for r in con.itertuples():
        if pkg(r).endswith("(previous)"):
            continue
        old = prev.get(pkg(r))
        if old is not None:
            mid = (f"<div class='swap'>{box(old.contractor, old.note, 'old')}"
                   "<span class='parr' title='Replaced by'><b></b><b></b><b></b><i>➜</i></span>"
                   f"{box(r.contractor, r.note, 'new')}</div>")
        else:
            mid = box(r.contractor, r.note, "new" if r.status == "Active" else "")
        col = sc.get(r.status, "#3A4663")
        rows.append(f"<div class='crow' style='border-left:3px solid {col}'><div class='pk'>{e(pkg(r))}</div>{mid}"
                    f"<div class='st'><span class='chip'>{e(r.status) or 'Unassigned'}</span></div></div>")
    return "".join(rows)


# ----------------------------------------------------------------------------
# Page
# ----------------------------------------------------------------------------
def render():
    st.set_page_config(page_title="S08 Natun Bazar", page_icon="🚧", layout="wide", initial_sidebar_state="auto")
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    prog, sections, issues, contractors, mock = load(_stamp())
    today = date.today()
    df = prepare(prog)

    sec_pct = {s: pct(g.f_actual.sum(), g.f_qty.sum()) for s, g in df.groupby("section")}
    overall = pct(df.f_actual.sum(), df.f_qty.sum())
    exc = df[df.group == "Excavation"]
    status = {r.section: section_status(r._asdict(), sec_pct.get(r.section, 0.0)) for r in sections.itertuples()}
    stalled = sum(1 for v in status.values() if v in STALLED)
    live = issues[issues.status == "Open"]
    overdue = int(sum(1 for r in live.itertuples() if pd.notna(r.due) and r.due < today))
    open_n = {}
    for r in live.itertuples():
        for s in [x.strip() for x in str(r.section).split(",")]:
            open_n[s] = open_n.get(s, 0) + 1

    asof = "Sample data" if mock else "Data as of " + datetime.fromtimestamp(_stamp()).strftime("%d %b %I:%M %p")
    st.markdown(f"""<div class='topbar'><div class='brand'><span class='logo'></span><div><b>Natun Bazar</b>
<small>Dhaka MRT Line-1, Station 08 · utility relocation since December 2024</small></div></div>
<span class='tag'>{e(asof)}</span></div>""", unsafe_allow_html=True)
    page = st.radio("Page", ["Overview", "Utilities", "Issues", "Contractors"], horizontal=True, label_visibility="collapsed", key="nav")

    if page == "Overview":
        st.markdown(f"""<div class='hero'><div class='ringcard'>{ring(overall)}<div><div class='tl'>Overall progress</div>
<div class='ts'>Weighted by factored length across all {len(sections)} sections</div></div></div>
<div class='tiles'>{tile("Excavation", f"{pct(exc.f_actual.sum(), exc.f_qty.sum()):.0f}%", "of trench length open", CY)}
{tile("Stalled sections", f"{stalled} / {len(sections)}", "on hold or blocked", AMB)}
{tile("Open issues", len(live), f"of {len(issues)} logged", VIO)}
{tile("Past committed date", overdue, "open issues overdue", PINK if overdue else MINT)}</div></div>""", unsafe_allow_html=True)

        st.markdown("<h3 class='sec'>Corridor plan, south to north</h3>", unsafe_allow_html=True)
        legend = "".join(f"<span><b style='background:{c};box-shadow:0 0 8px {c}'></b>{n}</span>" for n, c in COL.items())
        components.html(f"<style>{PLAN_CSS}</style><div class='w'>{plan_svg(sections, sec_pct, open_n)}"
                        f"<div class='lg'>{legend}<span>Hatched = stalled</span><span>Circle = open issues</span></div></div>", height=545)

        st.markdown("<h3 class='sec'>Needs attention</h3>", unsafe_allow_html=True)
        top = sorted(live.itertuples(), key=lambda r: (PRIORITY.get(r.priority, 3), r.raised))[:4]
        st.markdown("".join(issue_html(r, today) for r in top) or "<div class='panel'>No open issues.</div>", unsafe_allow_html=True)

    elif page == "Utilities":
        st.markdown("<h3 class='sec'>Utility progress by section</h3>", unsafe_allow_html=True)
        st.markdown(matrix(df, sections, sec_pct, status), unsafe_allow_html=True)
        st.caption("Percent of factored length complete. Dash means the utility is not in that section's scope. Bottom row and right column are weighted totals.")
        st.markdown("<h3 class='sec'>Section detail</h3>", unsafe_allow_html=True)
        for s in sections.itertuples():
            with st.expander(f"{s.name}: {sec_pct.get(s.section, 0):.0f}% · {status[s.section].lower()} · {s.chainage}"):
                st.caption(s.note)
                d = df[df.section == s.section]
                st.markdown("".join(bar(r.item, pct(r.actual, r.qty)) for r in d.itertuples()), unsafe_allow_html=True)

    elif page == "Issues":
        c1, c2 = st.columns([1, 2])
        stat = c1.multiselect("Status", ["Open", "Monitoring", "Resolved"], default=["Open"])
        sect = c2.multiselect("Section", list(sections.section), default=list(sections.section))

        def hit(x):
            parts = [s.strip() for s in str(x).split(",")]
            return any(p in sect or (p == "Crossing" and ("S6" in sect or "S7" in sect)) for p in parts)

        v = issues[issues.status.isin(stat) & issues.section.apply(hit)]
        v = sorted(v.itertuples(), key=lambda r: (r.status != "Open", PRIORITY.get(r.priority, 3), r.raised))
        st.markdown(f"<h3 class='sec'>{len(v)} issue{'s' if len(v) != 1 else ''}</h3>", unsafe_allow_html=True)
        st.markdown("".join(issue_html(r, today) for r in v) or "<div class='panel'>No issues match these filters.</div>", unsafe_allow_html=True)
        st.caption("Stripe: pink high, amber medium, grey low. Owner is who must act; 'via' is who we chase them through.")

    else:
        st.markdown("<h3 class='sec'>Contractors by package</h3>", unsafe_allow_html=True)
        st.markdown(contractor_rows(contractors), unsafe_allow_html=True)


if __name__ == "__main__":
    render()