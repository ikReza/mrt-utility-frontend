import streamlit as st

from utils.ui import apply_custom_css

st.set_page_config(page_title="Tools", page_icon="🧰", layout="wide")
apply_custom_css()

# ════════════════════════════════════════════════════════════════════════
# TOOL REGISTRY — add new tools here. One dict = one card. Nothing else to edit.
# ════════════════════════════════════════════════════════════════════════
TOOLS = [
    dict(emoji="📏", name="Slope Calculator",
         url="https://ikreza.github.io/utility-tools/",
         desc="Check / calculate slope on site.",
         tag="SITE · HYDRAULICS"),
    # --- copy this block and edit it to add the next tool ---
    # dict(emoji="🧮", name="Next Tool Name",
    #      url="https://ikreza.github.io/utility-tools/",
    #      desc="One line: what it does.",
    #      tag="SITE"),
]

# ── CSS: assembled from single-line pieces — MUST contain no blank lines ──
css_parts = [
    "<link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap' rel='stylesheet'>",
    "<style>",
    "*{box-sizing:border-box}",
    ".tsheet{font-family:'Space Grotesk',ui-sans-serif,sans-serif;color:#242820;background:#F4F0E6;",
    "  border:1px solid rgba(36,40,32,.16);border-radius:16px;padding:20px 22px 22px;margin-top:-8px;",
    "  background-image:radial-gradient(rgba(36,40,32,.06) 1px,transparent 1.2px);background-size:22px 22px;}",
    ".tsheet a{color:inherit}",
    ".thead{display:flex;align-items:center;gap:12px;padding-bottom:12px;border-bottom:2px solid #242820;",
    "  position:relative;margin-bottom:4px}",
    ".thead::after{content:'';position:absolute;left:0;right:0;bottom:-5px;height:1px;background:#242820}",
    ".thead .mark{flex:none;width:30px;height:30px;color:#0E6B5B}",
    ".thead h1{font-size:19px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin:0;line-height:1.15}",
    ".thead .rev{margin-left:auto;flex:none;font:600 10px 'IBM Plex Mono',monospace;letter-spacing:.12em;",
    "  border:1.5px solid #0E6B5B;color:#0E6B5B;border-radius:6px;padding:4px 8px;background:#E7EFE9}",
    ".tcap{display:flex;align-items:center;gap:10px;margin:20px 0 12px;",
    "  font:600 10.5px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:#6A6E5F}",
    ".tcap .n{color:#0E6B5B}",
    ".tcap .rule{flex:1;height:1px;background:rgba(36,40,32,.16)}",
    ".tcap .r{letter-spacing:.08em;font-weight:500}",
    ".tcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}",
    ".tcard{background:#FBF8F1;border:1px solid rgba(36,40,32,.16);border-radius:14px;padding:16px 16px 14px;",
    "  display:flex;flex-direction:column;gap:9px;transition:transform .12s,border-color .15s,box-shadow .15s}",
    ".tcard:hover{border-color:#0E6B5B;transform:translateY(-2px);box-shadow:0 3px 0 rgba(14,107,91,.35)}",
    ".tcard .tic{flex:none;width:38px;height:38px;border-radius:10px;background:#FDFBF5;",
    "  border:1px solid rgba(36,40,32,.55);display:flex;align-items:center;justify-content:center;font-size:19px}",
    ".tcard .tnm{font-weight:700;font-size:1rem;color:#242820;text-decoration:none;line-height:1.25}",
    ".tcard .tnm:hover{color:#0E6B5B}",
    ".tcard .tds{font:400 12.5px/1.55 'IBM Plex Mono',monospace;color:#6A6E5F;flex:1}",
    ".tcard .tft{display:flex;justify-content:space-between;align-items:center;margin-top:2px}",
    ".tcard .ttg{font:600 9px 'IBM Plex Mono',monospace;letter-spacing:.12em;color:#0E6B5B;",
    "  border:1px solid #0E6B5B;background:#E7EFE9;border-radius:999px;padding:3px 9px}",
    ".tcard .tgo{font:600 10.5px 'IBM Plex Mono',monospace;letter-spacing:.1em;color:#0E6B5B;",
    "  text-decoration:none;border:1px solid rgba(36,40,32,.55);border-radius:10px;padding:6px 10px;",
    "  transition:background .15s,color .15s}",
    ".tcard .tgo:hover{background:#242820;color:#F4F0E6}",
    "</style>",
]
st.markdown("\n".join(css_parts), unsafe_allow_html=True)

# ── Cards: every card is ONE continuous string — no blank lines possible ──
cards_html = "".join(
    "<div class='tcard'>"
    f"<div class='tic'>{t['emoji']}</div>"
    f"<a class='tnm' href='{t['url']}' target='_blank'>{t['name']}</a>"
    f"<div class='tds'>{t['desc']}</div>"
    "<div class='tft'>"
    f"<span class='ttg'>{t['tag']}</span>"
    f"<a class='tgo' href='{t['url']}' target='_blank'>OPEN &#8599;</a>"
    "</div>"
    "</div>"
    for t in TOOLS
)

page_html = (
    "<div class='tsheet'>"
    "<div class='thead'>"
    "<svg class='mark' viewBox='0 0 30 30' fill='none' stroke='currentColor' aria-hidden='true'>"
    "<path d='M3 5h24' stroke-width='2.4'/>"
    "<path d='M15 5v14M15 19l-7.5-8M15 19l7.5-8' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/>"
    "</svg>"
    "<h1>Tools &amp; Calculators</h1>"
    f"<span class='rev'>{len(TOOLS)} TOOLS</span>"
    "</div>"
    "<div class='tcap'><span class='n'>01</span> TOOLBOX <span class='rule'></span>"
    "<span class='r'>EXTERNAL LINKS · OPEN IN NEW TAB</span></div>"
    f"<div class='tcards'>{cards_html}</div>"
    "</div>"
)
st.markdown(page_html, unsafe_allow_html=True)