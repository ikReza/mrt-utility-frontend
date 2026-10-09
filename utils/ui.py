"""
Design system for the Utility Relocation Monitor — DARK SCI-FI theme.

Matched to the embedded route map: deep navy canvas, cyan/magenta neon,
blueprint grid, Orbitron headings, JetBrains Mono body.
"""

import streamlit as st


# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------

COLORS = {
    "bg": "#04060d",                       # app canvas (matches route map)
    "surface": "#0a1020",                  # panels / cards
    "surface_alt": "#0d1428",
    "border": "rgba(0,240,255,0.16)",
    "ink": "#e9f6ff",                      # primary text
    "ink_muted": "#7b86b8",
    "ink_faint": "#57608f",
    "primary": "#00f0ff",                  # neon cyan (route map line-a)
    "primary_dark": "#00b8cc",
    "primary_soft": "rgba(0,240,255,0.10)",
    "accent": "#2bff88",                   # completed green
    "accent_soft": "rgba(43,255,136,0.10)",
    "warn": "#ffcc33",                     # route map line-c
    "warn_soft": "rgba(255,204,51,0.10)",
    "danger": "#ff2e5f",
    "danger_soft": "rgba(255,46,95,0.10)",
    "pending": "#ff2e9a",                  # route map pending pink
    "gradient": "linear-gradient(90deg, #00f0ff 0%, #ff2e9a 55%, #ffcc33 100%)",
}


def apply_custom_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=JetBrains+Mono:wght@400;600;800&display=swap');

        :root {{
            --bg: {COLORS['bg']};
            --surface: {COLORS['surface']};
            --surface-alt: {COLORS['surface_alt']};
            --border: {COLORS['border']};
            --ink: {COLORS['ink']};
            --ink-muted: {COLORS['ink_muted']};
            --ink-faint: {COLORS['ink_faint']};
            --primary: {COLORS['primary']};
            --primary-dark: {COLORS['primary_dark']};
            --primary-soft: {COLORS['primary_soft']};
            --accent: {COLORS['accent']};
            --accent-soft: {COLORS['accent_soft']};
            --warn: {COLORS['warn']};
            --warn-soft: {COLORS['warn_soft']};
            --danger: {COLORS['danger']};
            --danger-soft: {COLORS['danger_soft']};
            --pending: {COLORS['pending']};
            --gradient: {COLORS['gradient']};
            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 9px;
            --shadow-sm: 0 0 0 1px rgba(0,0,0,.4);
            --shadow-md: 0 0 24px rgba(0,240,255,.08);
            --shadow-lg: 0 24px 70px rgba(0,0,0,.55);
        }}

        /* ---------- base canvas & typography ---------- */
        html, body, [class*="css"] {{
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
        }}
        .stApp {{
            background:
                radial-gradient(1100px 600px at 80% -10%, rgba(0,240,255,0.08), transparent 60%),
                radial-gradient(900px 600px at -10% 110%, rgba(255,46,154,0.07), transparent 60%),
                var(--bg);
        }}
        .stApp::before {{
            content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
            background:
                linear-gradient(rgba(0,240,255,0.028) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,240,255,0.028) 1px, transparent 1px);
            background-size: 44px 44px;
            -webkit-mask-image: radial-gradient(ellipse at 50% 35%, #000 25%, transparent 78%);
                    mask-image: radial-gradient(ellipse at 50% 35%, #000 25%, transparent 78%);
        }}
        h1, h2, h3, h4 {{
            font-family: 'Orbitron', sans-serif !important;
            color: var(--ink) !important;
            letter-spacing: .05em;
        }}
        h1 {{ font-weight: 700 !important; }}
        h2, h3 {{ font-weight: 700 !important; }}
        p, span, div, label {{ color: var(--ink); }}
        [data-testid="stMarkdownContainer"] p {{ color: var(--ink-muted); }}

        /* hide default chrome */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background: transparent; }}
        .block-container {{
            padding-top: 1.1rem;
            padding-bottom: 2.2rem;
            max-width: 1150px;
        }}

        /* ---------- sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #070c1a 0%, #0b1126 100%);
            border-right: 1px solid rgba(0,240,255,.12);
        }}
        section[data-testid="stSidebar"] * {{ color: #cdd6f4 !important; }}
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: #7b86b8 !important; }}
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stTextInput label {{ color: #7b86b8 !important; }}
        div[data-testid="stSidebarNav"] {{ padding-top: 0.5rem; }}
        div[data-testid="stSidebarNav"] ul {{ padding-left: 0.4rem; }}
        div[data-testid="stSidebarNav"] a {{
            border-radius: 9px; margin: 2px 8px; padding: 8px 10px !important;
            font-weight: 600; font-size: 0.85rem;
            transition: background .15s ease, box-shadow .15s ease;
        }}
        div[data-testid="stSidebarNav"] a:hover {{
            background: rgba(0,240,255,.08);
            box-shadow: inset 2px 0 0 var(--primary);
        }}
        div[data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: rgba(0,240,255,.12) !important;
            box-shadow: inset 3px 0 0 var(--primary), 0 0 18px rgba(0,240,255,.15);
        }}

        /* ---------- metrics (dark, kept for other pages) ---------- */
        div[data-testid="stMetric"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 16px 18px;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            transition: all .25s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            border-color: rgba(0,240,255,.4);
            box-shadow: 0 0 24px rgba(0,240,255,.08);
        }}
        [data-testid="stMetricLabel"] {{
            color: var(--ink-muted) !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-size: .68rem !important;
        }}
        [data-testid="stMetricValue"] {{
            color: var(--ink) !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 700 !important;
        }}

        /* ---------- charts ---------- */
        div[data-testid="stPlotlyChart"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 10px 10px 2px;
            box-shadow: 0 0 30px rgba(0,240,255,.05);
        }}

        /* ---------- dataframes / tables ---------- */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}

        /* ---------- buttons ---------- */
        .stButton>button, .stFormSubmitButton>button {{
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--ink);
            font-weight: 600;
            padding: .5rem 1.1rem;
            transition: all .18s ease;
        }}
        .stButton>button:hover, .stFormSubmitButton>button:hover {{
            border-color: var(--primary);
            color: var(--primary);
            box-shadow: 0 0 14px rgba(0,240,255,.25);
        }}
        .stFormSubmitButton>button {{
            background: var(--gradient);
            color: #04060d;
            border: none;
        }}
        .stFormSubmitButton>button:hover {{ color: #04060d; filter: brightness(1.1); }}

        button[kind="primary"],
        button[kind="primary"]:hover,
        button[kind="primary"]:focus,
        button[kind="primary"]:active {{
            background: var(--gradient) !important;
            color: #04060d !important;
            border: none !important;
            font-weight: 700;
        }}
        button[kind="primary"]:hover {{
            filter: brightness(1.1);
            box-shadow: 0 0 20px rgba(0,240,255,.35);
        }}
        button[kind="primary"] p {{ color: #04060d !important; }}

        /* ---------- inputs ---------- */
        .stTextInput input, .stTextArea textarea, .stDateInput input {{
            border-radius: var(--radius-sm) !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            color: var(--ink) !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px var(--primary-soft) !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div {{
            border-radius: var(--radius-sm) !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            color: var(--ink) !important;
        }}
        div[data-baseweb="popover"] > div {{
            background: #0d1428 !important;
            border: 1px solid rgba(0,240,255,.2) !important;
        }}
        div[data-baseweb="popover"] li[role="option"] {{
            background: transparent !important;
            color: var(--ink) !important;
        }}
        div[data-baseweb="popover"] li[role="option"]:hover,
        div[data-baseweb="popover"] li[aria-selected="true"] {{
            background: var(--primary-soft) !important;
            color: var(--primary) !important;
        }}
        div[data-baseweb="select"] svg {{ fill: var(--ink-muted) !important; opacity: 1 !important; }}
        div[data-baseweb="select"], div[data-baseweb="select"] * {{ cursor: pointer !important; }}

        /* ---------- expander ---------- */
        details {{
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            background: var(--surface) !important;
            box-shadow: var(--shadow-sm);
        }}
        summary {{ font-weight: 600 !important; }}

        /* ---------- tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid var(--border); }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            font-weight: 600;
            color: var(--ink-muted);
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--primary) !important;
            background: var(--primary-soft);
        }}

        /* ---------- alerts ---------- */
        div[data-testid="stAlert"] {{
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            background: var(--surface);
            box-shadow: var(--shadow-sm);
        }}

        /* ---------- misc ---------- */
        hr {{ border-color: rgba(0,240,255,.12) !important; }}
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #1c2a4a; border-radius: 8px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #2a3d6b; }}

        /* ---------- custom components ---------- */
        .hero {{
            background: linear-gradient(90deg, rgba(0,240,255,.08), rgba(255,46,154,.06)), var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 12px 20px;
            margin-bottom: 14px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
            box-shadow: 0 0 30px rgba(0,240,255,.06);
        }}
        .hero::before {{
            content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
            background: var(--gradient);
        }}
        .hero::after {{
            content: ''; position: absolute; inset: 0; pointer-events: none;
            background: radial-gradient(320px 120px at 95% 0%, rgba(0,240,255,.12), transparent 60%);
        }}
        .hero-eyebrow {{
            flex: 0 0 auto;
            display: inline-flex; align-items: center; gap: 6px;
            color: var(--primary);
            border: 1px solid rgba(0,240,255,.35);
            background: rgba(0,240,255,.07);
            font-size: .62rem; font-weight: 700;
            letter-spacing: .14em; text-transform: uppercase;
            padding: 4px 10px; border-radius: 999px;
            margin: 0;
        }}
        .hero-title {{
            font-family: 'Orbitron', sans-serif;
            color: var(--ink); font-size: 1.02rem; font-weight: 700;
            margin: 0; letter-spacing: .06em;
            flex: 0 0 auto;
        }}
        .hero-subtitle {{
            color: var(--ink-muted);
            font-size: .78rem; margin: 0 0 0 auto;
            flex: 1 1 240px; text-align: right;
        }}

        .section-header {{
            display: flex; align-items: center; gap: 12px;
            margin: 6px 0 10px 0;
        }}
        .section-header .bar {{
            width: 4px; height: 22px; border-radius: 3px;
            background: var(--gradient);
            box-shadow: 0 0 12px rgba(0,240,255,.5);
        }}
        .section-header h3 {{ margin: 0 !important; font-size: 1rem !important; letter-spacing: .05em; }}
        .section-header .sub {{ color: var(--ink-faint); font-size: .78rem; margin-left: 4px; }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            margin-bottom: 8px;
        }}
        .kpi-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 18px 20px;
            box-shadow: var(--shadow-sm);
            transition: all .25s ease;
            position: relative;
            overflow: hidden;
        }}
        .kpi-card:hover {{
            border-color: rgba(0,240,255,.4);
            box-shadow: 0 0 24px rgba(0,240,255,.08);
        }}
        .kpi-card .kpi-icon {{
            width: 36px; height: 36px; border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem; margin-bottom: 10px;
        }}
        .kpi-card .kpi-label {{
            color: var(--ink-muted);
            font-size: .68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: .08em;
            margin-bottom: 6px;
        }}
        .kpi-card .kpi-value {{
            font-family: 'Orbitron', sans-serif;
            font-size: 1.7rem; font-weight: 700; color: var(--ink);
            line-height: 1.1;
        }}
        .kpi-card .kpi-delta {{
            font-size: .75rem; font-weight: 600; margin-top: 6px;
            display: inline-block;
        }}

        .badge {{
            display: inline-flex; align-items: center; gap: 5px;
            padding: 3px 10px; border-radius: 999px;
            font-size: .7rem; font-weight: 700;
            letter-spacing: .02em;
        }}
        .badge-dot {{ width: 6px; height: 6px; border-radius: 50%; }}

        .glass-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px 22px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 18px;
        }}

        /* ---------- mobile ---------- */
        @media(max-width: 640px) {{
            .block-container {{ padding-top: 3.4rem; padding-bottom: 1.6rem; max-width: 100%; }}
            .hero {{ padding: 10px 14px; gap: 8px; }}
            .hero-title {{ font-size: .88rem; }}
            .hero-subtitle {{ text-align: left; margin: 0; flex-basis: 100%; }}
            .section-header h3 {{ font-size: .9rem !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Make the sidebar open/close buttons clearly visible on the dark theme
    # (covers different Streamlit versions' test-ids). Plain string, NOT f-string.
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] { visibility: visible !important; z-index: 999990; }
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarHeader"] button {
            visibility: visible !important;
            opacity: 1 !important;
            display: flex !important;
            align-items: center; justify-content: center;
            background: rgba(4,6,13,.92) !important;
            border: 1px solid rgba(0,240,255,.5) !important;
            border-radius: 10px !important;
            box-shadow: 0 0 14px rgba(0,240,255,.3);
            color: #00f0ff !important;
            z-index: 999991 !important;
        }
        [data-testid="stExpandSidebarButton"] *,
        [data-testid="collapsedControl"] *,
        [data-testid="stSidebarCollapsedControl"] *,
        [data-testid="stSidebarCollapseButton"] button *,
        [data-testid="stSidebarHeader"] button * {
            color: #00f0ff !important;
            fill: #00f0ff !important;
        }
        @media(max-width:700px){
            [data-testid="stExpandSidebarButton"],
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"] {
                width: 44px; height: 44px; margin: 6px 0 0 8px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Embedded route map iframe (see Dashboard.py). Plain string (NOT f-string).
    # Desktop: full width, height is set by the map itself (JS inside the iframe).
    # Mobile: tall fixed viewport; the map pans / pinch-zooms inside it.
    st.markdown(
        """
        <style>
        div[data-testid="stIFrame"] iframe,
        .stIFrame iframe,
        iframe[height="1180"] {
            display: block;
            width: 100% !important;
            max-width: 1150px;
            margin: 0 auto;
            background: #04060d;
            border: 1px solid rgba(0,240,255,.18);
            border-radius: 14px;
            box-shadow: 0 0 40px rgba(0,240,255,.07);
        }
        @media(max-width:700px){
            div[data-testid="stIFrame"] iframe, .stIFrame iframe, iframe[height="1180"] {
                height: 78vh !important;
                min-height: 460px;
                border-radius: 10px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Reusable HTML components
# --------------------------------------------------------------------------

def hero(eyebrow: str, title: str, subtitle: str = ""):
    """Compact single-line hero banner."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = ""):
    """Small accent-bar header used above chart / table sections."""
    sub_html = f'<span class="sub">{subtitle}</span>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="bar"></div>
            <h3>{title}</h3>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card_html(label, value, icon, tint, delta=None, delta_color="var(--accent)"):
    tint_bg = {
        "primary": "var(--primary-soft)",
        "accent": "var(--accent-soft)",
        "warn": "var(--warn-soft)",
        "danger": "var(--danger-soft)",
    }.get(tint, "var(--primary-soft)")
    tint_fg = {
        "primary": "var(--primary)",
        "accent": "var(--accent)",
        "warn": "var(--warn)",
        "danger": "var(--danger)",
    }.get(tint, "var(--primary)")
    delta_html = f'<div class="kpi-delta" style="color:{delta_color};">{delta}</div>' if delta else ""
    return f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:{tint_bg}; color:{tint_fg};">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
    """


def kpi_row(cards):
    """Render a responsive row of KPI cards (kept for other pages)."""
    html = '<div class="kpi-grid">'
    for c in cards:
        html += _kpi_card_html(
            c["label"], c["value"], c.get("icon", "•"), c.get("tint", "primary"),
            c.get("delta"), c.get("delta_color", "var(--accent)")
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def badge(text: str, tint: str = "accent"):
    color_map = {
        "accent": ("var(--accent-soft)", "var(--accent)"),
        "primary": ("var(--primary-soft)", "var(--primary)"),
        "warn": ("var(--warn-soft)", "var(--warn)"),
        "danger": ("var(--danger-soft)", "var(--danger)"),
    }
    bg, fg = color_map.get(tint, color_map["accent"])
    return (
        f'<span class="badge" style="background:{bg}; color:{fg};">'
        f'<span class="badge-dot" style="background:{fg};"></span>{text}</span>'
    )