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

# ── CSS: dark sci-fi theme (matches utils/ui.py) — single-line pieces, NO blank lines ──
css_parts = [
    "<style>",
    "*{box-sizing:border-box}",
    ".tsheet{font-family:'JetBrains Mono',monospace;color:#e9f6ff;background:#0a1020;",
    "  border:1px solid rgba(0,240,255,.16);border-radius:16px;padding:20px 22px 22px;margin-top:-8px;",
    "  box-shadow:0 0 30px rgba(0,240,255,.06);",
    "  background-image:radial-gradient(rgba(0,240,255,.07) 1px,transparent 1.2px);background-size:22px 22px;}",
    ".tsheet div,.tsheet span,.tsheet a,.tsheet h1{color:inherit}",
    ".thead{display:flex;align-items:center;gap:12px;padding-bottom:12px;border-bottom:2px solid #00f0ff;",
    "  position:relative;margin-bottom:4px;box-shadow:0 8px 14px -12px rgba(0,240,255,.6)}",
    ".thead::after{content:'';position:absolute;left:0;right:0;bottom:-5px;height:1px;background:rgba(255,46,154,.55)}",
    ".thead .mark{flex:none;width:30px;height:30px;color:#00f0ff;filter:drop-shadow(0 0 6px rgba(0,240,255,.6))}",
    ".thead h1{font-family:'Orbitron',sans-serif!important;font-size:18px;font-weight:700;letter-spacing:.07em;",
    "  text-transform:uppercase;margin:0;padding:0;line-height:1.15;color:#e9f6ff!important}",
    ".thead .rev{margin-left:auto;flex:none;font:600 10px 'JetBrains Mono',monospace;letter-spacing:.12em;",
    "  border:1.5px solid #00f0ff;color:#00f0ff;border-radius:6px;padding:4px 8px;background:rgba(0,240,255,.10)}",
    ".tcap{display:flex;align-items:center;gap:10px;margin:20px 0 12px;",
    "  font:600 10.5px 'JetBrains Mono',monospace;letter-spacing:.16em;color:#7b86b8}",
    ".tcap .n{color:#00f0ff}",
    ".tcap .rule{flex:1;height:1px;background:rgba(0,240,255,.16)}",
    ".tcap .r{letter-spacing:.08em;font-weight:500;color:#57608f}",
    ".tcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}",
    ".tcard{background:#0d1428;border:1px solid rgba(0,240,255,.16);border-radius:14px;padding:16px 16px 14px;",
    "  display:flex;flex-direction:column;gap:9px;transition:transform .12s,border-color .15s,box-shadow .15s}",
    ".tcard:hover{border-color:#00f0ff;transform:translateY(-2px);box-shadow:0 0 22px rgba(0,240,255,.22)}",
    ".tcard .tic{flex:none;width:38px;height:38px;border-radius:10px;background:rgba(0,240,255,.08);",
    "  border:1px solid rgba(0,240,255,.4);display:flex;align-items:center;justify-content:center;font-size:19px}",
    ".tcard .tnm{font-family:'Orbitron',sans-serif;font-weight:700;font-size:.92rem;letter-spacing:.04em;",
    "  color:#e9f6ff!important;text-decoration:none!important;line-height:1.3}",
    ".tcard .tnm:hover{color:#00f0ff!important}",
    ".tcard .tds{font:400 12.5px/1.55 'JetBrains Mono',monospace;color:#7b86b8;flex:1}",
    ".tcard .tft{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:2px;flex-wrap:wrap}",
    ".tcard .ttg{font:600 9px 'JetBrains Mono',monospace;letter-spacing:.12em;color:#00f0ff;",
    "  border:1px solid rgba(0,240,255,.5);background:rgba(0,240,255,.08);border-radius:999px;padding:3px 9px}",
    ".tcard .tgo{font:600 10.5px 'JetBrains Mono',monospace;letter-spacing:.1em;color:#00f0ff!important;",
    "  text-decoration:none!important;border:1px solid rgba(0,240,255,.5);border-radius:10px;padding:8px 12px;",
    "  transition:background .15s,color .15s,box-shadow .15s}",
    ".tcard .tgo:hover{background:linear-gradient(90deg,#00f0ff,#ff2e9a);color:#04060d!important;",
    "  border-color:transparent;box-shadow:0 0 16px rgba(0,240,255,.4)}",
    "@media(max-width:640px){.tsheet{padding:14px 12px 16px}.thead h1{font-size:15px}.tcap .r{display:none}}",
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