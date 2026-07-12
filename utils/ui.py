"""
Design system for the Utility Relocation Monitor.

This module centralises every visual choice (colors, type, spacing,
component chrome) so the rest of the app only ever calls small,
semantic helpers like `kpi_row(...)` or `section_header(...)`.
"""

import streamlit as st


# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------

COLORS = {
    "bg": "#0b0f1a",              # app canvas (deep navy, not pure black)
    "bg_soft": "#f4f6fb",         # light canvas used behind content cards
    "surface": "#ffffff",
    "surface_alt": "#f8f9fd",
    "border": "#e7e9f3",
    "ink": "#12142b",
    "ink_muted": "#5c6079",
    "ink_faint": "#9598ad",
    "primary": "#5b5bf6",         # electric indigo
    "primary_dark": "#3d3dd6",
    "primary_soft": "#eef0ff",
    "accent": "#12c2a9",          # teal accent for "in progress / positive"
    "accent_soft": "#e6faf6",
    "warn": "#f5a623",
    "warn_soft": "#fef4e2",
    "danger": "#ef4a5f",
    "danger_soft": "#feecee",
    "gradient": "linear-gradient(135deg, #5b5bf6 0%, #8a5bf6 45%, #12c2a9 100%)",
}


def apply_custom_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg-soft: {COLORS['bg_soft']};
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
            --gradient: {COLORS['gradient']};
            --radius-lg: 20px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --shadow-sm: 0 1px 2px rgba(18, 20, 43, 0.04);
            --shadow-md: 0 8px 24px -8px rgba(18, 20, 43, 0.12);
            --shadow-lg: 0 20px 40px -16px rgba(18, 20, 43, 0.22);
        }}

        /* ---------- base canvas & typography ---------- */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        .stApp {{
            background:
                radial-gradient(1200px 500px at 100% -10%, rgba(91,91,246,0.10), transparent 60%),
                radial-gradient(900px 500px at -10% 10%, rgba(18,194,169,0.08), transparent 55%),
                var(--bg-soft);
        }}
        h1, h2, h3, h4 {{
            font-family: 'Space Grotesk', 'Inter', sans-serif !important;
            color: var(--ink) !important;
            letter-spacing: -0.01em;
        }}
        h1 {{ font-weight: 700 !important; }}
        h2, h3 {{ font-weight: 600 !important; }}
        p, span, div, label {{ color: var(--ink); }}
        [data-testid="stMarkdownContainer"] p {{ color: var(--ink-muted); }}

        /* hide default chrome for a cleaner canvas */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{
            background: transparent;
        }}
        .block-container {{
            padding-top: 2.2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* ---------- sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #12142b 0%, #191b3a 100%);
            border-right: none;
        }}
        section[data-testid="stSidebar"] * {{
            color: #e7e8f7 !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: #b6b8d6 !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stTextInput label {{
            color: #b6b8d6 !important;
        }}
        div[data-testid="stSidebarNav"] {{
            padding-top: 0.5rem;
        }}
        div[data-testid="stSidebarNav"] ul {{
            padding-left: 0.4rem;
        }}
        div[data-testid="stSidebarNav"] a {{
            border-radius: 10px;
            margin: 2px 8px;
            padding: 8px 10px !important;
            font-weight: 500;
            font-size: 0.92rem;
            transition: background 0.15s ease, transform 0.15s ease;
        }}
        div[data-testid="stSidebarNav"] a:hover {{
            background: rgba(255,255,255,0.08);
            transform: translateX(2px);
        }}
        div[data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: var(--gradient) !important;
            box-shadow: 0 6px 16px -4px rgba(91,91,246,0.55);
        }}

        /* ---------- generic surfaces ---------- */
        div[data-testid="stMetric"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 22px 20px;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
            transition: all 0.25s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
            border-color: rgba(91,91,246,0.35);
        }}
        [data-testid="stMetricLabel"] {{
            color: var(--ink-muted) !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-size: 0.72rem !important;
        }}
        [data-testid="stMetricValue"] {{
            color: var(--ink) !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
        }}

        /* dataframes / tables */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}

        /* buttons */
        .stButton>button, .stFormSubmitButton>button {{
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--ink);
            font-weight: 600;
            padding: 0.5rem 1.1rem;
            transition: all 0.18s ease;
        }}
        .stButton>button:hover, .stFormSubmitButton>button:hover {{
            border-color: var(--primary);
            color: var(--primary-dark);
            box-shadow: 0 6px 16px -6px rgba(91,91,246,0.45);
            transform: translateY(-1px);
        }}
        .stFormSubmitButton>button {{
            background: var(--gradient);
            color: #fff;
            border: none;
        }}
        .stFormSubmitButton>button:hover {{
            color: #fff;
            filter: brightness(1.06);
        }}

        button[kind="primary"],
        button[kind="primary"]:hover,
        button[kind="primary"]:focus,
        button[kind="primary"]:active {{
            background: var(--gradient) !important;
            color: #ffffff !important;
            border: none !important;
        }}
        button[kind="primary"]:hover {{
            filter: brightness(1.08);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px -6px rgba(91,91,246,0.55);
        }}
        button[kind="primary"] p {{
            color: #ffffff !important;
        }}

        /* inputs */
        .stTextInput input, .stTextArea textarea, .stDateInput input,
        .stSelectbox div[data-baseweb="select"] > div {{
            border-radius: var(--radius-sm) !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px var(--primary-soft) !important;
        }}

        /* expander */
        details {{
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            background: var(--surface) !important;
            box-shadow: var(--shadow-sm);
        }}
        summary {{ font-weight: 600 !important; }}

        /* tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid var(--border);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px 10px 0 0;
            font-weight: 600;
            color: var(--ink-muted);
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--primary) !important;
            background: var(--primary-soft);
        }}

        /* alerts */
        div[data-testid="stAlert"] {{
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
        }}

        /* horizontal rule */
        hr {{ border-color: var(--border) !important; }}

        /* scrollbar */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: #c7cae3; border-radius: 8px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: #a9adcf; }}

        /* ---------- custom components ---------- */
        .hero {{
            background: var(--gradient);
            border-radius: var(--radius-lg);
            padding: 34px 38px;
            margin-bottom: 26px;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-lg);
        }}
        .hero::after {{
            content: "";
            position: absolute; inset: 0;
            background: radial-gradient(400px 200px at 90% 0%, rgba(255,255,255,0.25), transparent 60%);
        }}
        .hero-eyebrow {{
            display: inline-flex; align-items: center; gap: 6px;
            color: rgba(255,255,255,0.85);
            font-size: 0.75rem; font-weight: 700;
            letter-spacing: 0.10em; text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .hero-title {{
            font-family: 'Space Grotesk', sans-serif;
            color: #fff; font-size: 2.0rem; font-weight: 700;
            margin: 0 0 8px 0; letter-spacing: -0.02em;
        }}
        .hero-subtitle {{
            color: rgba(255,255,255,0.88);
            font-size: 0.98rem; margin: 0; max-width: 640px;
        }}

        .section-header {{
            display: flex; align-items: center; gap: 12px;
            margin: 8px 0 16px 0;
        }}
        .section-header .bar {{
            width: 5px; height: 26px; border-radius: 4px;
            background: var(--gradient);
        }}
        .section-header h3 {{
            margin: 0 !important; font-size: 1.15rem !important;
        }}
        .section-header .sub {{
            color: var(--ink-faint); font-size: 0.85rem; margin-left: 4px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 8px;
        }}
        .kpi-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 20px 22px;
            box-shadow: var(--shadow-sm);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-md);
            border-color: rgba(91,91,246,0.35);
        }}
        .kpi-card .kpi-icon {{
            width: 38px; height: 38px;
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.05rem;
            margin-bottom: 12px;
        }}
        .kpi-card .kpi-label {{
            color: var(--ink-muted);
            font-size: 0.72rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.06em;
            margin-bottom: 6px;
        }}
        .kpi-card .kpi-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.9rem; font-weight: 700; color: var(--ink);
            line-height: 1.1;
        }}
        .kpi-card .kpi-delta {{
            font-size: 0.78rem; font-weight: 600; margin-top: 6px;
            display: inline-block;
        }}

        .badge {{
            display: inline-flex; align-items: center; gap: 5px;
            padding: 3px 10px; border-radius: 999px;
            font-size: 0.72rem; font-weight: 700;
            letter-spacing: 0.02em;
        }}
        .badge-dot {{ width: 6px; height: 6px; border-radius: 50%; }}

        .glass-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 22px 24px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 18px;
        }}
        
        div[data-baseweb="popover"] li[role="option"] {{
            background: var(--surface) !important;
            color: var(--ink) !important;
        }}
        div[data-baseweb="popover"] li[role="option"]:hover,
        div[data-baseweb="popover"] li[aria-selected="true"] {{
            background: var(--primary-soft) !important;
            color: var(--primary-dark) !important;
        }}

        /* selectbox dropdown arrow/chevron icon */
        div[data-baseweb="select"] svg {{
            fill: var(--ink-muted) !important;
            opacity: 1 !important;
        }}

        /* selectbox: show pointer cursor instead of text-caret */
        div[data-baseweb="select"] {{
            cursor: pointer !important;
        }}
        div[data-baseweb="select"] * {{
            cursor: pointer !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Reusable HTML components
# --------------------------------------------------------------------------

def hero(eyebrow: str, title: str, subtitle: str = ""):
    """Top-of-page gradient hero banner."""
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
    """
    Render a responsive row of KPI cards.
    `cards` is a list of dicts: {label, value, icon, tint, delta?, delta_color?}
    tint in {"primary", "accent", "warn", "danger"}
    """
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
