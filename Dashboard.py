import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

from utils.ui import apply_custom_css, hero, section_header
from utils.data_fetcher import fetch_overview_data
from utils.plotly_charts import generate_plotly_chart


# ---------------------------------------------------------------- Route map embed
# CSS + JS injected ONLY into the embedded copy of route_map.html.
# (Plain strings, not f-strings, so braces stay single.)
MAP_CSS = """
<style>
html,body{margin:0!important;padding:0!important;height:100%!important;background:#04060d!important}
body::before{display:none!important}
#stage{max-width:none!important;width:100%!important;height:100%!important;margin:0!important;
  border:none!important;border-radius:0!important;box-shadow:none!important;
  display:flex!important;flex-direction:column!important;box-sizing:border-box!important;position:relative}
/* the holder is the scroll/pan viewport; JS sets the SVG width (= zoom level) */
#svgHolder{flex:1 1 auto;min-height:0!important;padding:0!important;display:block!important;
  overflow:auto!important;-webkit-overflow-scrolling:touch;touch-action:pan-x pan-y;
  scrollbar-width:thin;cursor:grab}
#svgHolder.dragging{cursor:grabbing}
#map{display:block!important;height:auto!important;max-width:none!important;max-height:none!important;margin:0 auto!important}
@media(max-width:700px){.hud-bar,.hud-progress{display:none!important}}
/* zoom toolbar */
#zoomCtl{position:absolute;right:10px;bottom:12px;z-index:50;display:flex;flex-direction:column;gap:6px}
#zoomCtl button{width:40px;height:40px;border-radius:10px;border:1px solid rgba(0,240,255,.45);
  background:rgba(4,6,13,.88);color:#00f0ff;font:700 20px/1 'JetBrains Mono',monospace;
  cursor:pointer;box-shadow:0 0 12px rgba(0,240,255,.25);-webkit-tap-highlight-color:transparent}
#zoomCtl button:active{background:rgba(0,240,255,.2)}
</style>
"""

MAP_JS = """
<script>
(function(){
  function ready(fn){document.readyState!=='loading'?fn():document.addEventListener('DOMContentLoaded',fn);}
  ready(function(){
    var holder=document.getElementById('svgHolder');
    var svg=document.getElementById('map')||(holder&&holder.querySelector('svg'));
    var stage=document.getElementById('stage')||document.body;
    if(!holder||!svg) return;

    var vb=svg.viewBox&&svg.viewBox.baseVal;
    var natW=(vb&&vb.width)||parseFloat(svg.getAttribute('width'))||900;
    var natH=(vb&&vb.height)||parseFloat(svg.getAttribute('height'))||1180;
    var MIN=1, MAX=6, zoom=1;
    var isMobile=function(){return window.innerWidth<=700;};
    var fitW=function(){return Math.max(holder.clientWidth,200);};

    function resizeFrame(){           // desktop only: iframe = natural height of the map (measured once, no feedback)
      if(isMobile()||zoom!==1) return;
      try{
        var fe=window.frameElement; if(!fe) return;
        var sv=[stage.style.height,stage.style.flex,holder.style.flex,holder.style.height,holder.style.overflow];
        stage.style.setProperty('height','auto','important');
        holder.style.flex='none'; holder.style.height='auto'; holder.style.overflow='visible';
        var h=stage.offsetHeight;                       // natural height, independent of current iframe height
        stage.style.removeProperty('height'); if(sv[0]) stage.style.height=sv[0];
        holder.style.flex=sv[2]; holder.style.height=sv[3]; holder.style.overflow=sv[4];
        var maxH=Math.ceil(fitW()*natH/natW)+400;       // sanity cap
        h=Math.min(Math.max(Math.ceil(h)+4,300),maxH);
        if(Math.abs(fe.offsetHeight-h)>2) fe.style.height=h+'px';
      }catch(e){}
    }

    function apply(){
      var w=Math.round(fitW()*zoom);
      svg.style.setProperty('width',w+'px','important');
      svg.style.setProperty('height',Math.round(w*natH/natW)+'px','important');
      resizeFrame();
    }

    function setZoom(z,cx,cy){        // zoom around a point (viewport coords) so content stays put
      z=Math.min(MAX,Math.max(MIN,z));
      var oldW=svg.getBoundingClientRect().width, oldH=svg.getBoundingClientRect().height;
      cx=(cx==null)?holder.clientWidth/2:cx; cy=(cy==null)?holder.clientHeight/2:cy;
      var fx=(holder.scrollLeft+cx)/oldW, fy=(holder.scrollTop+cy)/oldH;
      zoom=z; apply();
      holder.scrollLeft=fx*svg.getBoundingClientRect().width-cx;
      holder.scrollTop =fy*svg.getBoundingClientRect().height-cy;
    }

    // initial zoom: desktop = fit width; mobile = ~native size so text is readable
    function initialZoom(){
      if(!isMobile()) return 1;
      return Math.min(3,Math.max(1.6,natW/fitW()));
    }
    zoom=initialZoom(); apply();
    if(isMobile()){ holder.scrollLeft=(svg.getBoundingClientRect().width-holder.clientWidth)/2; }

    // zoom buttons
    var ctl=document.createElement('div'); ctl.id='zoomCtl';
    ctl.innerHTML='<button type="button" data-a="in" aria-label="Zoom in">+</button>'+
                  '<button type="button" data-a="out" aria-label="Zoom out">&minus;</button>';
    stage.appendChild(ctl);
    ctl.addEventListener('click',function(e){
      var a=e.target.getAttribute&&e.target.getAttribute('data-a'); if(!a) return;
      if(a==='in') setZoom(zoom*1.35); else if(a==='out') setZoom(zoom/1.35);
    });

    // pinch to zoom (touch)
    var pinch=null;
    function dist(t){var dx=t[0].clientX-t[1].clientX,dy=t[0].clientY-t[1].clientY;return Math.sqrt(dx*dx+dy*dy);}
    holder.addEventListener('touchstart',function(e){ if(e.touches.length===2) pinch={d:dist(e.touches),z:zoom}; },{passive:true});
    holder.addEventListener('touchmove',function(e){
      if(pinch&&e.touches.length===2){
        e.preventDefault();
        var r=holder.getBoundingClientRect();
        var cx=(e.touches[0].clientX+e.touches[1].clientX)/2-r.left;
        var cy=(e.touches[0].clientY+e.touches[1].clientY)/2-r.top;
        setZoom(pinch.z*dist(e.touches)/pinch.d,cx,cy);
      }
    },{passive:false});
    holder.addEventListener('touchend',function(e){ if(e.touches.length<2) pinch=null; },{passive:true});

    // mouse: ctrl/cmd + wheel zoom, drag to pan
    holder.addEventListener('wheel',function(e){
      if(!(e.ctrlKey||e.metaKey)) return;
      e.preventDefault();
      var r=holder.getBoundingClientRect();
      setZoom(zoom*(e.deltaY<0?1.12:1/1.12),e.clientX-r.left,e.clientY-r.top);
    },{passive:false});
    var drag=null;
    holder.addEventListener('mousedown',function(e){
      if(e.button!==0) return;
      drag={x:e.clientX,y:e.clientY,l:holder.scrollLeft,t:holder.scrollTop}; holder.classList.add('dragging');
    });
    window.addEventListener('mousemove',function(e){
      if(!drag) return;
      holder.scrollLeft=drag.l-(e.clientX-drag.x); holder.scrollTop=drag.t-(e.clientY-drag.y);
    });
    window.addEventListener('mouseup',function(){ drag=null; holder.classList.remove('dragging'); });

    // keep layout right on rotate / resize
    var lastMobile=isMobile(), lastW=window.innerWidth, t=null;
    window.addEventListener('resize',function(){
      if(window.innerWidth===lastW) return;            // ignore height-only changes (prevents resize loops)
      lastW=window.innerWidth;
      clearTimeout(t); t=setTimeout(function(){
        var m=isMobile();
        if(m!==lastMobile){ lastMobile=m; zoom=initialZoom(); }
        apply();
      },120);
    });
  });
})();
</script>
"""


def embed_route_map(html: str) -> str:
    """Inject the responsive CSS + zoom/pan JS into the embedded route map."""
    html = html.replace("</head>", MAP_CSS + "</head>", 1) if "</head>" in html else MAP_CSS + html
    html = html.replace("</body>", MAP_JS + "</body>", 1) if "</body>" in html else html + MAP_JS
    return html

# ---------------------------------------------------------------- Page setup
st.set_page_config(
    page_title="Utility Relocation Monitor",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_css()

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;padding:6px 4px 18px 4px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,#00f0ff,#ff2e9a);
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;box-shadow:0 0 14px rgba(0,240,255,.5);">🚆</div>
            <div>
                <div style="font-family:'Orbitron',sans-serif;font-weight:700;
                            font-size:0.9rem;color:#e9f6ff;letter-spacing:.04em;">Utility Relocation</div>
                <div style="font-size:0.7rem;color:#7b86b8;">Monitor</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------- Data
df = fetch_overview_data()

# ---------------------------------------------------------------- Hero (compact)
hero(
    eyebrow="Program Overview",
    title="🏠 Utility Relocation Dashboard",
)

if not df.empty:
    section_header("📈 Station Progress Overview")
    fig = generate_plotly_chart(df)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("")
    section_header("🗺️ Route Map")

    try:
        html_content = (Path(__file__).parent / "route_map.html").read_text(encoding="utf-8")
        components.html(embed_route_map(html_content), height=1180, scrolling=False)
    except FileNotFoundError:
        st.warning("route_map.html not found next to Dashboard.py.")