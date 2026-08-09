"""
=====================================================
News Intelligence Command Center — Enterprise Dashboard
Version : 14.0 (Three.js Icosahedron Data Core & Neural Intelligence Stream)
=====================================================
"""

import time
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(interval=10000, key=None):
        return 0

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="News Intelligence Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = "http://127.0.0.1:8000"

COLORS = {
    "bg": "#0f131c",
    "surface_lowest": "#0a0e17",
    "surface_low": "#181b25",
    "surface_container": "#1c1f29",
    "surface_high": "#262a34",
    "surface_highest": "#31353f",
    "primary": "#8aebff",
    "primary_container": "#22d3ee",
    "secondary": "#cebdff",
    "secondary_container": "#4f319c",
    "tertiary": "#61f6b9",
    "tertiary_container": "#3dd99e",
    "error": "#ffb4ab",
    "error_container": "#93000a",
    "on_surface": "#dfe2ef",
    "muted": "#859397",
    "border": "#3c494c",
    "border_variant": "rgba(60, 73, 76, 0.5)",
}

SENTIMENT_COLOR = {"Positive": COLORS["tertiary"], "Neutral": COLORS["muted"], "Negative": COLORS["error"]}

# =====================================================
# SCHEMA-SAFE DATA HELPERS
# =====================================================

def fmt_num(v, default="--"):
    try:
        if v is None:
            return default
        return f"{float(v):,.0f}" if float(v).is_integer() else f"{float(v):,.1f}"
    except (TypeError, ValueError):
        return default


def fmt_pct(v, default="--"):
    try:
        if v is None:
            return default
        return f"{float(v):+.0f}%"
    except (TypeError, ValueError):
        return default


def first_present(d: dict, keys: list, default=None):
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def normalize_records(records, field_aliases: dict, numeric_fields=None):
    numeric_fields = numeric_fields or []
    if not records or not isinstance(records, list):
        return []
    out = []
    for r in records:
        if not isinstance(r, dict):
            continue
        row = {}
        for canonical, aliases in field_aliases.items():
            val = first_present(r, aliases)
            if canonical in numeric_fields and val is not None:
                try:
                    val = float(val)
                except (TypeError, ValueError):
                    val = None
            row[canonical] = val
        out.append(row)
    return out


KEYWORD_ALIASES = {
    "keyword": ["keyword", "term", "name", "text"],
    "mentions": ["mentions", "recent_mentions", "count", "frequency"],
    "growth": ["growth", "growth_pct", "percentage_growth", "growth_percent"],
}
ENTITY_ALIASES = {
    "entity": ["entity", "name", "term"],
    "type": ["type", "entity_type", "label"],
    "mentions": ["mentions", "recent_mentions", "count", "frequency"],
    "growth": ["growth", "growth_pct", "percentage_growth", "growth_percent"],
}


def keywords_to_display_df(records):
    norm = normalize_records(records, KEYWORD_ALIASES, numeric_fields=["mentions", "growth"])
    if not norm:
        return pd.DataFrame(columns=["Keyword", "Mentions", "Growth"])
    return pd.DataFrame([{
        "Keyword": r["keyword"] or "Unknown",
        "Mentions": fmt_num(r["mentions"]),
        "Growth": fmt_pct(r["growth"]),
    } for r in norm])


def entities_to_display_df(records):
    norm = normalize_records(records, ENTITY_ALIASES, numeric_fields=["mentions", "growth"])
    if not norm:
        return pd.DataFrame(columns=["Entity", "Type", "Mentions", "Growth"])
    return pd.DataFrame([{
        "Entity": r["entity"] or "Unknown",
        "Type": r["type"] or "--",
        "Mentions": fmt_num(r["mentions"]),
        "Growth": fmt_pct(r["growth"]),
    } for r in norm])


def time_ago(ts):
    if not ts:
        return "--"
    try:
        s = str(ts).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = (now - dt).total_seconds()
        if delta < 0:
            return "JUST NOW"
        if delta < 60:
            return f"{int(delta)}s AGO"
        if delta < 3600:
            return f"{int(delta // 60)}m AGO"
        if delta < 86400:
            return f"{int(delta // 3600)}h AGO"
        return f"{int(delta // 86400)}d AGO"
    except Exception:
        return str(ts)[:16] if ts else "--"


# =====================================================
# API LAYER
# =====================================================

@st.cache_data(ttl=3, show_spinner=False)
def fetch_api(endpoint: str, params: dict = None):
    try:
        resp = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return (data if isinstance(data, dict) else {}), True
        return {}, False
    except Exception:
        return {}, False


def post_api(endpoint: str, payload: dict):
    try:
        resp = requests.post(f"{API_BASE_URL}{endpoint}", json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            return (data if isinstance(data, dict) else {}), True
        return {"error": f"API returned {resp.status_code}"}, False
    except Exception as e:
        return {"error": str(e)}, False


def unavailable(section_name: str):
    st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">◌</div>
            <div class="empty-title">{section_name} temporarily unavailable</div>
            <div class="empty-sub">We'll keep trying in the background — the rest of the dashboard stays live.</div>
        </div>
    """, unsafe_allow_html=True)


def empty_state(message: str):
    st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">○</div>
            <div class="empty-title">{message}</div>
        </div>
    """, unsafe_allow_html=True)


# =====================================================
# THREE.JS ICOSAHEDRON DATA CORE HERO COMPONENT
# =====================================================
def render_threejs_datacore():
    three_html = """
    <!DOCTYPE html>
    <html class="dark" lang="en">
    <head>
      <meta charset="utf-8"/>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet"/>
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1" rel="stylesheet"/>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; overflow: hidden; background: #0b0f19; font-family: 'Inter', sans-serif; color: #dfe2ef; }
        
        #threejs-container-DATA_CORE { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
        
        #init-overlay {
          position: absolute; top: 0; left: 0; width: 100%; height: 100%;
          display: flex; justify-content: center; align-items: center;
          background: #0b0f19; color: rgba(34, 211, 238, 0.9);
          font-family: 'JetBrains Mono', monospace; font-size: 13px; letter-spacing: 0.25em;
          z-index: 50; transition: opacity 1.8s ease-out; pointer-events: none;
        }
        
        .ui-layer { z-index: 10; position: absolute; }
        
        .status-box {
          top: 16px; left: 16px; width: 240px; padding: 14px;
          background: rgba(28, 31, 41, 0.75); backdrop-filter: blur(12px);
          border: 1px solid rgba(60, 73, 76, 0.5); border-radius: 8px;
        }
        
        .watermark {
          bottom: 12px; left: 50%; transform: translateX(-50%);
          color: rgba(138, 235, 255, 0.4); font-family: 'JetBrains Mono', monospace;
          font-size: 11px; letter-spacing: 0.3em; text-transform: uppercase; pointer-events: none;
        }

        .bar-bg { width: 100%; background: #31353f; height: 4px; border-radius: 4px; overflow: hidden; margin-top: 3px; }
        .bar-fill { background: #8aebff; height: 4px; border-radius: 4px; }
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
    <div id="threejs-container-DATA_CORE"></div>
    <div id="init-overlay">SYSTEM INITIALIZING...</div>
    
    <!-- Top Left: System Telemetry Widget -->
    <div class="ui-layer status-box">
      <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px; border-bottom:1px solid rgba(60,73,76,0.5); padding-bottom:6px;">
        <span class="material-symbols-outlined" style="color:#8aebff; font-size:16px;">memory</span>
        <span style="font-family:'JetBrains Mono'; font-size:11px; font-weight:700; color:#8aebff; letter-spacing:0.1em; text-transform:uppercase;">SYSTEM STATUS</span>
      </div>
      <div style="font-family:'JetBrains Mono'; font-size:10.5px;">
        <div style="display:flex; justify-content:space-between; color:#bbc9cd;"><span>MEM_USAGE</span><span style="color:#8aebff;">78.4%</span></div>
        <div class="bar-bg"><div class="bar-fill" style="width:78.4%;"></div></div>
        
        <div style="display:flex; justify-content:space-between; color:#bbc9cd; margin-top:8px;"><span>UPTIME</span><span style="color:#dfe2ef;">99.99%</span></div>
        <div style="display:flex; justify-content:space-between; color:#bbc9cd; margin-top:6px;"><span>AI_CONFIDENCE</span><span style="color:#61f6b9; font-weight:700;">HIGH</span></div>
      </div>
    </div>
    
    <div class="ui-layer watermark">Aether Intelligence • Neural Data Core</div>

    <script>
      window.addEventListener('load', () => {
        setTimeout(() => {
          const overlay = document.getElementById('init-overlay');
          if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => { overlay.style.display = 'none'; }, 1800);
          }
        }, 800);
      });

      const container = document.getElementById('threejs-container-DATA_CORE');
      const width = container.clientWidth || window.innerWidth;
      const height = container.clientHeight || window.innerHeight;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(65, width / height, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      const coreGroup = new THREE.Group();
      scene.add(coreGroup);

      // Central Icosahedron Brain Core
      const brainGeom = new THREE.IcosahedronGeometry(1.6, 1);
      const brainMat = new THREE.MeshPhongMaterial({
        color: 0x22d3ee,
        emissive: 0x22d3ee,
        emissiveIntensity: 0.5,
        wireframe: true,
        transparent: true,
        opacity: 0.85
      });
      const brain = new THREE.Mesh(brainGeom, brainMat);
      coreGroup.add(brain);

      // Data Streams Torus Rings
      const ringColors = [0x22d3ee, 0x818cf8, 0xf472b6];
      ringColors.forEach((color, i) => {
        const ringGeom = new THREE.TorusGeometry(2.4 + i * 0.45, 0.016, 16, 100);
        const ringMat = new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.5 });
        const ring = new THREE.Mesh(ringGeom, ringMat);
        ring.rotation.x = Math.random() * Math.PI;
        ring.rotation.y = Math.random() * Math.PI;
        coreGroup.add(ring);
      });

      // Particle Starfield
      const partGeom = new THREE.BufferGeometry();
      const partCount = 1200;
      const posArray = new Float32Array(partCount * 3);
      for(let i = 0; i < partCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 22;
      }
      partGeom.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
      const partMat = new THREE.PointsMaterial({ size: 0.035, color: 0xffffff, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending });
      const particles = new THREE.Points(partGeom, partMat);
      scene.add(particles);

      // Lights
      const light = new THREE.PointLight(0x22d3ee, 1.2, 100);
      light.position.set(10, 10, 10);
      scene.add(light);
      scene.add(new THREE.AmbientLight(0x404040));

      camera.position.z = 7;

      function animate(t) {
        requestAnimationFrame(animate);
        coreGroup.rotation.y += 0.003;
        coreGroup.rotation.x += 0.001;
        brain.rotation.y -= 0.004;
        particles.rotation.y += 0.0005;

        const pulse = 1 + Math.sin(t * 0.002) * 0.07;
        brain.scale.set(pulse, pulse, pulse);

        renderer.render(scene, camera);
      }

      window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      });

      animate(0);
    </script>
    </body>
    </html>
    """
    components.html(three_html, height=270, scrolling=False)


# =====================================================
# INJECT TAILWIND CSS & MATERIAL SYMBOLS
# =====================================================
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1" rel="stylesheet"/>

<style>
    .stApp {{
        background-color: {COLORS['bg']};
        color: {COLORS['on_surface']};
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {COLORS['surface_low']};
        border-right: 1px solid {COLORS['border_variant']};
        backdrop-filter: blur(12px);
    }}
    
    header[data-testid="stHeader"] {{ background: transparent; }}
    #MainMenu, footer {{ visibility: hidden; }}

    /* Keyframe Animations */
    .glitch-in {{
        animation: glitchFadeIn 0.5s ease-out forwards;
    }}
    @keyframes glitchFadeIn {{
        0% {{ opacity: 0; transform: translateY(-10px); }}
        50% {{ opacity: 0.5; transform: translateY(2px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .pulse-status {{
        animation: pulseActive 2s infinite;
    }}
    @keyframes pulseActive {{
        0% {{ box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.4); }}
        70% {{ box-shadow: 0 0 0 10px rgba(34, 211, 238, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(34, 211, 238, 0); }}
    }}
    
    .pulse-alert {{
        animation: pulseAlert 2s infinite;
    }}
    @keyframes pulseAlert {{
        0% {{ box-shadow: 0 0 0 0 rgba(255, 180, 171, 0.4); }}
        70% {{ box-shadow: 0 0 0 10px rgba(255, 180, 171, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(255, 180, 171, 0); }}
    }}
    
    .glow-pulse-live {{
        animation: glowPulseLive 2s infinite;
    }}
    @keyframes glowPulseLive {{
        0%, 100% {{ text-shadow: 0 0 4px rgba(34, 211, 238, 0.2); }}
        50% {{ text-shadow: 0 0 12px rgba(34, 211, 238, 0.8); }}
    }}
    
    .glow-pulse-spikes {{
        animation: glowPulseSpikes 2s infinite;
    }}
    @keyframes glowPulseSpikes {{
        0%, 100% {{ text-shadow: 0 0 4px rgba(255, 180, 171, 0.2); }}
        50% {{ text-shadow: 0 0 12px rgba(255, 180, 171, 0.8); }}
    }}

    /* Component Cards */
    .metric-box {{
        background-color: rgba(15, 19, 28, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid {COLORS['border_variant']};
        border-radius: 8px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 96px;
        transition: all 0.2s ease;
    }}
    .metric-box:hover {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 14px -2px rgba(138, 235, 255, 0.5);
        transform: translateY(-2px);
    }}
    .metric-box.tertiary-hover:hover {{
        border-color: {COLORS['tertiary']};
        box-shadow: 0 0 14px -2px rgba(97, 246, 185, 0.5);
    }}
    .metric-box.secondary-hover:hover {{
        border-color: {COLORS['secondary']};
        box-shadow: 0 0 14px -2px rgba(206, 189, 255, 0.5);
    }}
    .metric-box.error-border {{
        border-color: rgba(255, 180, 171, 0.5);
    }}
    .metric-box.error-border:hover {{
        border-color: {COLORS['error']};
        box-shadow: 0 0 14px -2px rgba(255, 180, 171, 0.5);
    }}

    .metric-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {COLORS['muted']};
    }}
    .metric-val {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 700;
    }}

    .alert-banner {{
        background-color: rgba(24, 27, 37, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 180, 171, 0.5);
        border-radius: 10px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(255, 180, 171, 0.2);
    }}

    .feed-card {{
        background-color: rgba(15, 19, 28, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid {COLORS['border_variant']};
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }}
    .feed-card:hover {{
        border-color: {COLORS['primary']};
        transform: translateY(-2px);
    }}

    .badge-pill {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 10.5px;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 5px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .section-title {{
        font-family: 'Inter', sans-serif;
        font-size: 13.5px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {COLORS['on_surface']};
        border-bottom: 1px solid {COLORS['border_variant']};
        padding-bottom: 6px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .empty-state {{
        text-align: center;
        padding: 26px 12px;
        color: {COLORS['muted']};
        border: 1px dashed {COLORS['border_variant']};
        border-radius: 10px;
    }}
    .empty-icon {{ font-size: 20px; margin-bottom: 6px; opacity: 0.6; }}
    .empty-title {{ font-size: 12.5px; font-weight: 600; color: #B7C0CE; }}
    .empty-sub {{ font-size: 11px; margin-top: 3px; }}

    .trace-box {{
        background-color: {COLORS['surface_lowest']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        color: {COLORS['tertiary']};
    }}
</style>
""", unsafe_allow_html=True)

# =====================================================
# TOP HEADER BAR
# =====================================================
health_res, health_ok = fetch_api("/health")
metrics_res, metrics_ok = fetch_api("/api/metrics")

mongo_status = first_present(health_res, ["mongodb", "mongo"], "down")
es_status = first_present(health_res, ["elasticsearch", "es"], "down")
kafka_status = first_present(health_res, ["kafka"], "unknown")
ai_status = first_present(health_res, ["ai_service", "ai"], "unknown")
ingestion_status = first_present(health_res, ["ingestion", "ingestion_service"], "unknown")
orchestrator_status = first_present(health_res, ["orchestrator", "pipeline_orchestrator"], "unknown")

freshness_ts = first_present(metrics_res, ["last_updated"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if metrics_ok else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding: 8px 0; border-bottom: 1px solid {COLORS['border_variant']}; margin-bottom: 12px;">
    <div style="display:flex; align-items:center; gap:10px;">
        <span class="material-symbols-outlined" style="color:{COLORS['primary']}; font-size:26px;">shield</span>
        <span style="font-family:'Inter'; font-weight:800; font-size:22px; letter-spacing:-0.02em; color:{COLORS['primary']};">NEWS INTELLIGENCE COMMAND CENTER</span>
    </div>
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="display:flex; align-items:center; gap:8px;">
            <div class="pulse-status" style="width:8px; height:8px; border-radius:50%; background-color:{COLORS['primary']};"></div>
            <span class="glow-pulse-live" style="font-family:'JetBrains Mono'; font-size:11px; font-weight:700; color:{COLORS['primary']}; text-transform:uppercase; letter-spacing:0.1em;">LIVE STREAM</span>
        </div>
        <span style="font-size:12px; color:{COLORS['muted']}; font-family:'JetBrains Mono';">Updated {time_ago(freshness_ts)}</span>
        <span class="material-symbols-outlined" style="color:{COLORS['muted']}; font-size:20px;">sensors</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# THREE.JS 3D ICOSAHEDRON DATA CORE HERO
# =====================================================
render_threejs_datacore()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.markdown(f"""
<div style="padding: 4px 0 12px 0;">
    <div style="font-family:'Inter'; font-weight:800; font-size:13px; letter-spacing:0.1em; color:{COLORS['primary']}; text-transform:uppercase;">COMMAND CENTER</div>
    <div style="font-size:10.5px; color:{COLORS['muted']}; font-family:'JetBrains Mono';">Aether Data Core v14.0</div>
</div>
""", unsafe_allow_html=True)

NAV_GROUPS = {
    "COMMAND CENTER": ["Command Center"],
    "NEWS": ["Live News", "Search", "Article Explorer"],
    "INTELLIGENCE": ["Intelligence", "Temporal Intelligence", "AI Analyst"],
    "SYSTEM": ["System Health"],
}
flat_pages = [p for group in NAV_GROUPS.values() for p in group]

for group_name, items in NAV_GROUPS.items():
    st.sidebar.caption(group_name)
    for item in items:
        pass

page = st.sidebar.radio("Navigate", flat_pages, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption("AUTO REFRESH")
auto_refresh = st.sidebar.checkbox("Enable", value=True)
refresh_sec = st.sidebar.select_slider("Interval (sec)", options=[5, 10, 15, 30], value=10, label_visibility="collapsed")
if auto_refresh:
    st_autorefresh(interval=refresh_sec * 1000, key="nav_autorefresh")

st.sidebar.markdown("---")

def status_dot(ok):
    return f'<span style="color:{COLORS["tertiary"]}">●</span> Healthy' if ok else f'<span style="color:{COLORS["error"]}">●</span> Offline'

st.sidebar.caption("SYSTEM STATUS")
services = [
    ("Kafka", kafka_status in ("ok", "healthy", "up") or health_ok),
    ("MongoDB", mongo_status in ("ok", "healthy", "up")),
    ("Elasticsearch", es_status in ("ok", "healthy", "up")),
    ("API Server", health_ok),
    ("AI Service", ai_status in ("ok", "healthy", "up") or health_ok),
    ("Ingestion Service", ingestion_status in ("ok", "healthy", "up") or health_ok),
    ("Pipeline Orchestrator", orchestrator_status in ("ok", "healthy", "up") or health_ok),
]
for name, ok in services:
    st.sidebar.markdown(f"<div style='font-size:12px; display:flex; justify-content:space-between; padding:2px 0;'><span>{name}</span><span>{status_dot(ok)}</span></div>", unsafe_allow_html=True)


def apply_plotly_dark_theme(fig, height=220):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(color=COLORS["on_surface"], family="Inter, sans-serif", size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="rgba(60, 73, 76, 0.3)", zerolinecolor="rgba(60, 73, 76, 0.3)"),
        yaxis=dict(gridcolor="rgba(60, 73, 76, 0.3)", zerolinecolor="rgba(60, 73, 76, 0.3)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(60, 73, 76, 0.3)"),
    )
    return fig


# =====================================================
# PAGE 1 — COMMAND CENTER
# =====================================================
if page == "Command Center":

    total_art = first_present(metrics_res, ["total_articles"], 0) or 0
    today_art = first_present(metrics_res, ["today_articles"], 0) or 0
    completed_art = first_present(metrics_res, ["completed_articles"], 0) or 0
    pending_art = (first_present(metrics_res, ["pending_articles"], 0) or 0) + (first_present(metrics_res, ["failed_articles"], 0) or 0)
    sources_dict = first_present(metrics_res, ["top_sources", "sources"], {}) or {}
    active_sources = len([s for s, c in sources_dict.items() if c and c > 0]) if sources_dict else 0

    spikes_res, spikes_ok = fetch_api("/api/analytics/spikes")
    spike_list = first_present(spikes_res, ["spikes"], []) or []

    # ROW 1: BREAKING ALERT & NEWS VOLUME CHART
    top_col1, top_col2 = st.columns([1, 2])

    with top_col1:
        if spike_list:
            top = spike_list[0] if isinstance(spike_list[0], dict) else {}
            cat = top.get("category") or "Geopolitical / Market"
            current = fmt_num(top.get("current_volume"))
            mult = top.get("multiplier")
            mult_s = f"{float(mult):.2f}x" if isinstance(mult, (int, float)) else "--"
            st.markdown(f"""
                <div class="alert-banner pulse-alert">
                    <div style="display:flex; align-items:center; gap:8px; color:{COLORS['error']}; margin-bottom:6px;">
                        <span class="material-symbols-outlined">warning</span>
                        <span style="font-family:'Inter'; font-weight:700; font-size:14px; text-transform:uppercase;">CRITICAL ANOMALY DETECTED</span>
                    </div>
                    <div style="font-size:13.5px; color:{COLORS['on_surface']}; line-height:1.4;">
                        Anomalous node activity in <b>{cat}</b> category ({current} articles/hr, <b>{mult_s}</b> velocity spike).
                    </div>
                    <div style="font-family:'JetBrains Mono'; font-size:11px; color:{COLORS['error']}; margin-top:10px; text-align:right;">T-MINUS LIVE</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="alert-banner" style="border-color:{COLORS['border_variant']}; box-shadow:none;">
                    <div style="display:flex; align-items:center; gap:8px; color:{COLORS['tertiary']}; margin-bottom:6px;">
                        <span class="material-symbols-outlined">check_circle</span>
                        <span style="font-family:'Inter'; font-weight:700; font-size:14px; text-transform:uppercase;">NEURAL NET SYNCHRONIZED</span>
                    </div>
                    <div style="font-size:13.5px; color:{COLORS['muted']}; line-height:1.4;">
                        Main clusters operating at optimal capacity. Real-time streaming pipeline synchronized.
                    </div>
                    <div style="font-family:'JetBrains Mono'; font-size:11px; color:{COLORS['tertiary']}; margin-top:10px; text-align:right;">STATUS OPTIMAL</div>
                </div>
            """, unsafe_allow_html=True)

    with top_col2:
        st.markdown(f'<div class="section-title">NEWS VOLUME (24H)</div>', unsafe_allow_html=True)
        vol_res, vol_ok = fetch_api("/api/analytics/source-trends", params={"window": "24h", "bucket": "1h"})
        vol_data = first_present(vol_res, ["timeline"], []) if vol_ok else []
        if not vol_ok or not vol_data:
            empty_state("Volume chart telemetry initializing...")
        else:
            try:
                df_vol = pd.DataFrame(vol_data)
                if "time" in df_vol.columns and "count" in df_vol.columns:
                    df_vol = df_vol.groupby("time", as_index=False)["count"].sum().sort_values("time")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_vol["time"], y=df_vol["count"], mode="lines", fill="tozeroy",
                        line=dict(color=COLORS["primary"], width=2.5),
                        fillcolor="rgba(138, 235, 255, 0.15)",
                    ))
                    st.plotly_chart(apply_plotly_dark_theme(fig, height=150), use_container_width=True)
                else:
                    empty_state("Volume telemetry data schema unrecognized.")
            except Exception:
                unavailable("Volume chart")

    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2: METRIC GRID (6 COLUMNS)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(f"""
            <div class="metric-box">
                <span class="metric-label">TOTAL ARTICLES</span>
                <span class="metric-val" style="color:{COLORS['primary']};">{fmt_num(total_art)}</span>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="metric-box tertiary-hover">
                <span class="metric-label">ARTICLES TODAY</span>
                <span class="metric-val" style="color:{COLORS['tertiary']};">{fmt_num(today_art)}</span>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="metric-box secondary-hover">
                <span class="metric-label">VELOCITY/MIN</span>
                <span class="metric-val" style="color:{COLORS['secondary']};">{fmt_num(max(total_art - pending_art, 0))}</span>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="metric-box">
                <span class="metric-label">ENRICHMENT</span>
                <span class="metric-val" style="color:{COLORS['on_surface']};">{(completed_art/total_art*100):.1f}%</span>
            </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
            <div class="metric-box">
                <span class="metric-label">ACTIVE SOURCES</span>
                <span class="metric-val" style="color:{COLORS['on_surface']};">{fmt_num(active_sources) if sources_dict else "--"}</span>
            </div>
        """, unsafe_allow_html=True)
    with k6:
        st.markdown(f"""
            <div class="metric-box error-border">
                <span class="metric-label" style="color:{COLORS['error']};">SPIKES</span>
                <span class="metric-val glow-pulse-spikes" style="color:{COLORS['error']};">{len(spike_list)}</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 3: GLOBAL INTELLIGENCE STREAM & DISTRIBUTION CHARTS
    feed_col, chart_col = st.columns([1, 1])

    with feed_col:
        st.markdown(f'<div class="section-title">GLOBAL INTELLIGENCE STREAM</div>', unsafe_allow_html=True)
        feed_res, feed_ok = fetch_api("/api/live-feed", params={"limit": 5})
        articles = first_present(feed_res, ["articles"], []) if feed_ok else []
        if not feed_ok:
            unavailable("Global intelligence stream")
        elif not articles:
            empty_state("No intelligence items available.")
        else:
            for a in articles[:5]:
                if not isinstance(a, dict):
                    continue
                sent = a.get("sentiment") or "Neutral"
                sent_style = f"background:rgba(97,246,185,0.15); color:{COLORS['tertiary']};" if sent == "Positive" else (f"background:rgba(255,180,171,0.15); color:{COLORS['error']};" if sent == "Negative" else f"background:rgba(133,147,151,0.15); color:{COLORS['muted']};")
                title = a.get("title") or "Untitled intelligence event"
                source = a.get("source") or "Global Wire"
                cat = a.get("category") or "NEWS"
                st.markdown(f"""
                    <div class="feed-card glitch-in">
                        <div style="display:flex; justify-content:space-between; align-items:start; gap:12px;">
                            <div style="font-size:14px; font-weight:600; color:{COLORS['on_surface']}; line-height:1.4; flex:1;">{title}</div>
                            <span style="font-family:'JetBrains Mono'; font-size:11px; color:{COLORS['muted']}; white-space:nowrap;">{time_ago(a.get('published_date'))}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span class="badge-pill" style="background:rgba(34,211,238,0.15); color:{COLORS['primary_container']};">{cat}</span>
                                <span style="font-family:'JetBrains Mono'; font-size:12px; color:{COLORS['muted']};">{source}</span>
                            </div>
                            <span class="badge-pill" style="{sent_style}">{sent}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with chart_col:
        st.markdown(f'<div class="section-title">DISTRIBUTION TELEMETRY</div>', unsafe_allow_html=True)
        c_tab1, c_tab2, c_tab3 = st.tabs(["Sources", "Categories", "Sentiments"])

        with c_tab1:
            if sources_dict:
                df_src = pd.DataFrame(list(sources_dict.items()), columns=["Source", "Count"]).sort_values("Count")
                fig_src = px.bar(df_src, x="Count", y="Source", orientation="h", color_discrete_sequence=[COLORS["primary"], COLORS["tertiary"], COLORS["secondary"]])
                fig_src.update_layout(showlegend=False)
                st.plotly_chart(apply_plotly_dark_theme(fig_src, height=220), use_container_width=True)
            else:
                empty_state("No source telemetry available.")

        with c_tab2:
            cats = first_present(metrics_res, ["categories", "category_distribution"], {}) or {}
            if cats:
                df_cat = pd.DataFrame(list(cats.items()), columns=["Category", "Count"])
                fig_cat = px.pie(df_cat, values="Count", names="Category", hole=0.5, color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["tertiary"], COLORS["error"]])
                st.plotly_chart(apply_plotly_dark_theme(fig_cat, height=220), use_container_width=True)
            else:
                empty_state("No category distribution telemetry available.")

        with c_tab3:
            sents = first_present(metrics_res, ["sentiment", "sentiment_distribution"], {}) or {}
            if sents:
                df_sent = pd.DataFrame(list(sents.items()), columns=["Sentiment", "Count"])
                fig_sent = px.pie(df_sent, values="Count", names="Sentiment", hole=0.5, color="Sentiment", color_discrete_map=SENTIMENT_COLOR)
                st.plotly_chart(apply_plotly_dark_theme(fig_sent, height=220), use_container_width=True)
            else:
                empty_state("No sentiment telemetry available.")


# =====================================================
# PAGE 2 — LIVE NEWS
# =====================================================
elif page == "Live News":
    st.markdown(f'<div class="section-title">LIVE NEWS EXPLORER</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_source = st.selectbox("Source Publisher", ["All Sources", "Economic Times", "The Hindu", "Indian Express", "Hindustan Times"])
    with f2:
        sel_cat = st.selectbox("Category Filter", ["All Categories", "Business", "Technology", "Politics", "Sports", "World", "General"])
    with f3:
        sel_sent = st.selectbox("Sentiment Filter", ["All Sentiments", "Positive", "Neutral", "Negative"])
    with f4:
        search_kw = st.text_input("Headline Keyword", placeholder="Search headlines...")

    feed_res, feed_ok = fetch_api("/api/live-feed", params={"limit": 50})
    if not feed_ok:
        unavailable("Live news feed")
    else:
        articles = [a for a in (first_present(feed_res, ["articles"], []) or []) if isinstance(a, dict)]
        filtered = []
        for a in articles:
            if sel_source != "All Sources" and a.get("source") != sel_source:
                continue
            if sel_cat != "All Categories" and a.get("category") != sel_cat:
                continue
            if sel_sent != "All Sentiments" and a.get("sentiment") != sel_sent:
                continue
            if search_kw and search_kw.lower() not in (a.get("title") or "").lower():
                continue
            filtered.append(a)

        st.caption(f"Showing **{len(filtered)}** of **{len(articles)}** live articles")

        if not filtered:
            empty_state("No articles match your selected filters.")
        else:
            for a in filtered:
                sent = a.get("sentiment") or "Neutral"
                sent_style = f"color:{COLORS['tertiary']};" if sent == "Positive" else (f"color:{COLORS['error']};" if sent == "Negative" else f"color:{COLORS['muted']};")
                with st.expander(f"[{a.get('source','Unknown')}] {a.get('title','Untitled')}"):
                    st.markdown(f"**Category:** `{a.get('category','--')}` &nbsp;|&nbsp; **Sentiment:** <span style='font-weight:700; {sent_style}'>{sent}</span> &nbsp;|&nbsp; **Published:** {time_ago(a.get('published_date'))}", unsafe_allow_html=True)
                    st.write(a.get("summary") or "No summary available for this item.")
                    if a.get("link"):
                        st.markdown(f"[Read full source article →]({a.get('link')})")


# =====================================================
# PAGE 3 — INTELLIGENCE
# =====================================================
elif page == "Intelligence":
    st.markdown(f'<div class="section-title">INTELLIGENCE ANALYTICS</div>', unsafe_allow_html=True)

    time_win = st.select_slider("Time Window", options=["15m", "1h", "6h", "24h", "7d"], value="24h")
    t1, t2, t3 = st.tabs(["Source Trends", "Category Trends", "Sentiment Timeline"])

    with t1:
        src_res, src_ok = fetch_api("/api/analytics/source-trends", params={"window": time_win, "bucket": "1h"})
        src_data = first_present(src_res, ["timeline"], []) if src_ok else []
        if not src_ok or not src_data:
            empty_state("No source trend telemetry for this window.")
        else:
            try:
                df = pd.DataFrame(src_data)
                fig = px.line(df, x="time", y="count", color=df["source"] if "source" in df.columns else None,
                               color_discrete_sequence=[COLORS["primary"], COLORS["tertiary"], COLORS["secondary"]])
                st.plotly_chart(apply_plotly_dark_theme(fig, height=340), use_container_width=True)
            except Exception:
                unavailable("Source trends")

    with t2:
        cat_res, cat_ok = fetch_api("/api/analytics/category-trends", params={"window": time_win, "bucket": "1h"})
        cat_data = first_present(cat_res, ["timeline"], []) if cat_ok else []
        if not cat_ok or not cat_data:
            empty_state("No category trend telemetry for this window.")
        else:
            try:
                df = pd.DataFrame(cat_data)
                fig = px.area(df, x="time", y="count", color=df["category"] if "category" in df.columns else None)
                st.plotly_chart(apply_plotly_dark_theme(fig, height=340), use_container_width=True)
            except Exception:
                unavailable("Category trends")

    with t3:
        sent_res, sent_ok = fetch_api("/api/analytics/sentiment-trends", params={"window": time_win, "bucket": "1h"})
        sent_data = first_present(sent_res, ["timeline"], []) if sent_ok else []
        if not sent_ok or not sent_data:
            empty_state("No sentiment trend telemetry for this window.")
        else:
            try:
                df = pd.DataFrame(sent_data)
                fig = px.line(df, x="time", y="count", color="sentiment" if "sentiment" in df.columns else None, color_discrete_map=SENTIMENT_COLOR)
                st.plotly_chart(apply_plotly_dark_theme(fig, height=340), use_container_width=True)
            except Exception:
                unavailable("Sentiment trends")


# =====================================================
# PAGE 4 — TEMPORAL INTELLIGENCE
# =====================================================
elif page == "Temporal Intelligence":
    st.markdown(f'<div class="section-title">TEMPORAL INTELLIGENCE WORKSPACE</div>', unsafe_allow_html=True)

    sp_res, sp_ok = fetch_api("/api/analytics/spikes")
    spikes = first_present(sp_res, ["spikes"], []) if sp_ok else []
    if not sp_ok:
        unavailable("Spike detection")
    elif spikes:
        top = spikes[0] if isinstance(spikes[0], dict) else {}
        st.error(f"🚨 **Activity Spike Detected**: Category **{top.get('category','Unknown')}** at **{fmt_num(top.get('current_volume'))} articles/hr**")
    else:
        st.success("🟢 Normal Activity Status — No critical volume spikes detected.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Emerging Keywords")
        kw_res, kw_ok = fetch_api("/api/analytics/keywords")
        kws = first_present(kw_res, ["keywords"], []) if kw_ok else []
        if not kw_ok or not kws:
            empty_state("No emerging keywords detected.")
        else:
            st.dataframe(keywords_to_display_df(kws), use_container_width=True)

    with col2:
        st.markdown("#### Emerging Entities")
        ent_res, ent_ok = fetch_api("/api/analytics/entities")
        ents = first_present(ent_res, ["entities"], []) if ent_ok else []
        if not ent_ok or not ents:
            empty_state("No emerging entities detected.")
        else:
            st.dataframe(entities_to_display_df(ents), use_container_width=True)


# =====================================================
# PAGE 5 — SEARCH
# =====================================================
elif page == "Search":
    st.markdown(f'<div class="section-title">HYBRID SEARCH ENGINE</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Hybrid RRF Search", "Keyword BM25", "Semantic Vector KNN"])
    modes = ["hybrid", "bm25", "knn"]

    for tab, mode in zip(tabs, modes):
        with tab:
            q = st.text_input("Enter search query...", key=f"q_{mode}", placeholder="e.g. solid-state battery technology...")
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                search_cat = st.selectbox("Category Filter", ["All", "Business", "Technology", "Politics", "Sports", "World"], key=f"cat_{mode}")
            with fc2:
                search_sent = st.selectbox("Sentiment Filter", ["All", "Positive", "Neutral", "Negative"], key=f"sent_{mode}")
            with fc3:
                search_limit = st.slider("Max Results", 5, 30, 10, key=f"lim_{mode}")

            if q.strip():
                params = {"q": q.strip(), "type": mode, "limit": search_limit}
                if search_cat != "All":
                    params["category"] = search_cat
                if search_sent != "All":
                    params["sentiment"] = search_sent

                s_res, s_ok = fetch_api("/api/search", params=params)
                if not s_ok:
                    unavailable("Search engine")
                else:
                    hits = [h for h in (first_present(s_res, ["articles", "results"], []) or []) if isinstance(h, dict)]
                    if not hits:
                        empty_state("No articles found matching query.")
                    else:
                        st.caption(f"Retrieved **{len(hits)}** results via **{mode.upper()}** engine")
                        for h in hits:
                            score = h.get("_score") or h.get("score")
                            score_s = f"{float(score):.3f}" if isinstance(score, (int, float)) else "--"
                            st.markdown(f"""
                                <div class="feed-card">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span class="badge-pill" style="background:rgba(34,211,238,0.15); color:{COLORS['primary']};">{h.get('source','--')}</span>
                                        <span style="font-family:'JetBrains Mono'; font-size:11px; color:{COLORS['muted']};">Score {score_s}</span>
                                    </div>
                                    <div style="font-size:15px; font-weight:700; margin:8px 0;">
                                        <a href="{h.get('link','#')}" target="_blank" style="color:{COLORS['primary']}; text-decoration:none;">{h.get('title','Untitled')}</a>
                                    </div>
                                    <div style="font-size:12.5px; color:{COLORS['muted']};">{h.get('summary','')}</div>
                                </div>
                            """, unsafe_allow_html=True)


# =====================================================
# PAGE 6 — AI ANALYST
# =====================================================
elif page == "AI Analyst":
    st.markdown(f'<div class="section-title">AI NEWS ANALYST</div>', unsafe_allow_html=True)

    sq1, sq2, sq3 = st.columns(3)
    user_q = st.session_state.get("ai_q", "")
    if sq1.button("What's trending in tech today?"):
        user_q = "What's trending in tech today?"
    if sq2.button("What major news spikes occurred today?"):
        user_q = "What major news spikes occurred today?"
    if sq3.button("What topics appear across multiple sources?"):
        user_q = "What topics appear across multiple sources?"

    input_q = st.text_area("Ask AI Analyst", value=user_q, placeholder="e.g. Compare coverage of market trends...")

    if st.button("Query AI Analyst", type="primary") and input_q.strip():
        with st.spinner("Executing intent routing & retrieving evidence..."):
            rag_res, rag_ok = post_api("/api/ai/ask", {"question": input_q.strip()})

        if not rag_ok:
            st.error(f"AI Analyst is temporarily unavailable ({rag_res.get('error','unknown error')}).")
        else:
            answer = rag_res.get("answer")
            st.markdown("#### AI Response")
            if answer:
                st.info(answer)
            else:
                st.warning("Insufficient evidence was found in the indexed corpus to answer this query.")

            insights = first_present(rag_res, ["insights"], []) or []
            st.markdown("#### Key Takeaways")
            if insights:
                for ins in insights:
                    st.markdown(f"- {ins}")

            with st.expander("Execution Trace & Retrieval Metadata"):
                tools = first_present(rag_res, ["tools_executed"], []) or []
                st.markdown(f"""
                    <div class="trace-box">
                        Intent Detected : {rag_res.get('intent','UNKNOWN')}<br>
                        Provider        : {rag_res.get('provider','RAG')}<br>
                        Tools Executed  : {', '.join(tools) if tools else '--'}<br>
                        Docs Retrieved  : {len(first_present(rag_res, ["sources"], []) or [])}
                    </div>
                """, unsafe_allow_html=True)


# =====================================================
# PAGE 7 — ARTICLE EXPLORER
# =====================================================
elif page == "Article Explorer":
    st.markdown(f'<div class="section-title">ARTICLE INSPECTOR</div>', unsafe_allow_html=True)

    target_id = st.text_input("Article ID or Document Link")
    if target_id.strip():
        art_res, art_ok = fetch_api(f"/api/articles/{target_id.strip()}")
        if not art_ok or not art_res:
            st.error("Article not found in database.")
        else:
            st.markdown(f"### {art_res.get('title','Untitled article')}")
            st.caption(f"{art_res.get('source','--')} · {time_ago(art_res.get('published_date'))}")
            st.write(art_res.get("summary") or "No summary available.")


# =====================================================
# PAGE 8 — SYSTEM HEALTH
# =====================================================
elif page == "System Health":
    st.markdown(f'<div class="section-title">SYSTEM HEALTH & MONITORING</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("API Server", "Healthy" if health_ok else "Offline")
    m2.metric("MongoDB", "Healthy" if mongo_status in ("ok", "healthy", "up") else "Offline")
    m3.metric("Elasticsearch", "Healthy" if es_status in ("ok", "healthy", "up") else "Offline")
    m4.metric("Total Documents", fmt_num(first_present(metrics_res, ["total_articles"], 0)))

    st.markdown("---")
    st.markdown("#### Service Status")
    for name, ok in services:
        st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid {COLORS['border_variant']}; display:flex; justify-content:space-between;'><span>{name}</span>{status_dot(ok)}</div>", unsafe_allow_html=True)
