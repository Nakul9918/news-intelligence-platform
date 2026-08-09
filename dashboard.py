"""
=====================================================
News Intelligence Command Center — Enterprise Dashboard
Version : 17.0 (Resolved Key Mismatches & Live Telemetry Volume Rendering)
=====================================================
"""

import time
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(interval=10000, key=None):
        return 0

# =====================================================
# CONFIGURATION & THEME TOKENS
# =====================================================
st.set_page_config(
    page_title="News Intelligence Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = "http://127.0.0.1:8000"

COLORS = {
    "bg": "#0B0F17",
    "card": "#121824",
    "card_border": "#1E2638",
    "text": "#E5E7EB",
    "muted": "#9CA3AF",
    "cyan": "#06B6D4",
    "blue": "#3B82F6",
    "purple": "#8B5CF6",
    "green": "#10B981",
    "orange": "#F59E0B",
    "red": "#EF4444",
}

SENTIMENT_COLOR = {"Positive": COLORS["green"], "Neutral": COLORS["muted"], "Negative": COLORS["red"]}

# =====================================================
# SCHEMA-SAFE DATA HELPERS (Defensive Contracts)
# =====================================================

def fmt_num(v, default="--"):
    """Format numeric values safely without raising exceptions."""
    try:
        if v is None:
            return default
        return f"{float(v):,.0f}" if float(v).is_integer() else f"{float(v):,.1f}"
    except (TypeError, ValueError):
        return default


def fmt_pct(v, default="--"):
    """Format growth or percentage values safely."""
    try:
        if v is None:
            return default
        return f"{float(v):+.0f}%"
    except (TypeError, ValueError):
        return default


def first_present(d: dict, keys: list, default=None):
    """Retrieve the first non-null key found from possible API variants."""
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def normalize_records(records, field_aliases: dict, numeric_fields=None):
    """Ensure API dict lists conform to standardized key names."""
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
    """Best-effort relative time string generator."""
    if not ts:
        return "--"
    try:
        s = str(ts).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = (now - dt).total_seconds()
        if delta < 0:
            return "just now"
        if delta < 60:
            return f"{int(delta)}s ago"
        if delta < 3600:
            return f"{int(delta // 60)}m ago"
        if delta < 86400:
            return f"{int(delta // 3600)}h ago"
        return f"{int(delta // 86400)}d ago"
    except Exception:
        return str(ts)[:16] if ts else "--"


# =====================================================
# API CLIENT LAYER (Fault-Tolerant)
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
        return {"error": f"API returned HTTP {resp.status_code}"}, False
    except Exception as e:
        return {"error": str(e)}, False


def render_unavailable_box(section_name: str):
    st.markdown(f"""
        <div style="text-align:center; padding:20px; border:1px dashed {COLORS['card_border']}; border-radius:8px; background:{COLORS['card']}; color:{COLORS['muted']}; font-size:12.5px;">
            <b>{section_name} Temporarily Unavailable</b><br>
            <span style="font-size:11px;">The system is retrying in the background. Other sections remain live.</span>
        </div>
    """, unsafe_allow_html=True)


def render_empty_box(message: str):
    st.markdown(f"""
        <div style="text-align:center; padding:20px; border:1px dashed {COLORS['card_border']}; border-radius:8px; background:{COLORS['card']}; color:{COLORS['muted']}; font-size:12.5px;">
            {message}
        </div>
    """, unsafe_allow_html=True)


# =====================================================
# CLEAN HIGH-DENSITY STYLING
# =====================================================
st.markdown(f"""
<style>
    .stApp {{
        background-color: {COLORS['bg']};
        color: {COLORS['text']};
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: #080C14;
        border-right: 1px solid {COLORS['card_border']};
    }}
    
    header[data-testid="stHeader"] {{ background: transparent; }}
    #MainMenu, footer {{ visibility: hidden; }}

    .card-box {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['card_border']};
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }}

    .badge {{
        display: inline-block;
        padding: 2px 8px;
        font-size: 10.5px;
        font-weight: 700;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}
    .badge-cyan {{ background: rgba(6,182,212,0.15); color: {COLORS['cyan']}; border: 1px solid rgba(6,182,212,0.3); }}
    .badge-purple {{ background: rgba(139,92,246,0.15); color: {COLORS['purple']}; border: 1px solid rgba(139,92,246,0.3); }}
    .badge-green {{ background: rgba(16,185,129,0.15); color: {COLORS['green']}; border: 1px solid rgba(16,185,129,0.3); }}
    .badge-muted {{ background: rgba(156,163,175,0.15); color: {COLORS['muted']}; border: 1px solid rgba(156,163,175,0.3); }}
    .badge-red {{ background: rgba(239,68,68,0.15); color: {COLORS['red']}; border: 1px solid rgba(239,68,68,0.3); }}

    .section-title {{
        font-size: 13.5px;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: {COLORS['text']};
        border-bottom: 1px solid {COLORS['card_border']};
        padding-bottom: 6px;
        margin-bottom: 12px;
    }}

    .trace-box {{
        background: #070A11;
        border: 1px solid {COLORS['card_border']};
        border-radius: 6px;
        padding: 12px;
        font-family: monospace;
        font-size: 11.5px;
        color: {COLORS['green']};
    }}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR NAVIGATION & SYSTEM STATUS
# =====================================================
st.sidebar.markdown(f"""
<div style="display:flex; align-items:center; gap:8px; padding: 4px 0 10px 0;">
    <span style="font-size:22px;">🛡️</span>
    <div>
        <div style="font-weight:800; font-size:14px; color:#F9FAFB; letter-spacing:0.3px;">NEWS INTELLIGENCE</div>
        <div style="font-size:10px; color:{COLORS['cyan']}; font-weight:700;">COMMAND CENTER</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

NAV_GROUPS = {
    "COMMAND CENTER": ["Command Center"],
    "NEWS": ["Live News Feed", "Search Workspace", "Article Inspector"],
    "INTELLIGENCE": ["Temporal Analytics", "AI Analyst (RAG)"],
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
auto_refresh = st.sidebar.checkbox("Enable Refresh", value=True)
refresh_sec = st.sidebar.select_slider("Interval (seconds)", options=[5, 10, 15, 30], value=10, label_visibility="collapsed")
if auto_refresh:
    st_autorefresh(interval=refresh_sec * 1000, key="nav_autorefresh")

st.sidebar.markdown("---")

health_res, health_ok = fetch_api("/health")
metrics_res, metrics_ok = fetch_api("/api/metrics")

mongo_status = first_present(health_res, ["mongodb", "mongo"], "down")
es_status = first_present(health_res, ["elasticsearch", "es"], "down")
kafka_status = first_present(health_res, ["kafka"], "unknown")

def status_dot(ok):
    return f'<span style="color:{COLORS["green"]}">●</span> Healthy' if ok else f'<span style="color:{COLORS["red"]}">●</span> Offline'

st.sidebar.caption("INFRASTRUCTURE STATUS")
services = [
    ("API Server", health_ok),
    ("MongoDB", mongo_status in ("ok", "healthy", "up")),
    ("Elasticsearch", es_status in ("ok", "healthy", "up")),
]
for name, ok in services:
    st.sidebar.markdown(f"<div style='font-size:12px; display:flex; justify-content:space-between; padding:2px 0;'><span>{name}</span><span>{status_dot(ok)}</span></div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
freshness_ts = first_present(metrics_res, ["last_updated"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if metrics_ok else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.sidebar.caption("DATA FRESHNESS")
st.sidebar.markdown(f"<div style='font-size:12px; color:{COLORS['green']}; font-weight:600;'>Updated {time_ago(freshness_ts)}</div>", unsafe_allow_html=True)


def apply_plotly_dark_theme(fig, height=230):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(color=COLORS["text"], family="sans-serif", size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=COLORS["card_border"]),
    )
    return fig


# =====================================================
# HEADER BAR (Shared Across Pages)
# =====================================================
def render_header(title, subtitle):
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"""
            <div>
                <h1 style="margin:0; font-size:24px; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px;">{title}</h1>
                <p style="margin:2px 0 0 0; font-size:12.5px; color:{COLORS['muted']};">{subtitle}</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div style="text-align:right; padding-top:6px;">
                <span class="badge badge-red">● LIVE PIPELINE</span>
                <span style="font-size:11.5px; color:{COLORS['muted']}; margin-left:10px;">Syncing continuously</span>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# PAGE 1 — COMMAND CENTER
# =====================================================
if page == "Command Center":
    render_header("COMMAND CENTER", "Real-time news ingestion, volume metrics, and high-level distribution analytics")

    total_art = first_present(metrics_res, ["total_articles"], 0) or 0
    today_art = first_present(metrics_res, ["today_articles"], 0) or 0
    completed_art = first_present(metrics_res, ["completed_articles"], 0) or 0
    pending_art = (first_present(metrics_res, ["pending_articles"], 0) or 0) + (first_present(metrics_res, ["failed_articles"], 0) or 0)
    sources_dict = first_present(metrics_res, ["top_sources", "sources"], {}) or {}
    active_sources = len([s for s, c in sources_dict.items() if c and c > 0]) if sources_dict else 0

    spikes_res, spikes_ok = fetch_api("/api/analytics/spikes")
    spike_list = first_present(spikes_res, ["spikes"], []) or []

    # KPI METRICS
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Corpus", fmt_num(total_art), "Indexed articles")
    m2.metric("Articles Today", fmt_num(today_art), "Since midnight")
    m3.metric("Processed Stream", fmt_num(max(total_art - pending_art, 0)), "In real-time")
    m4.metric("NLP Enriched", fmt_num(completed_art), f"{(completed_art/total_art*100):.1f}% complete" if total_art else "--")
    m5.metric("Active Sources", fmt_num(active_sources) if sources_dict else "--", "Publishers")
    m6.metric("Spike Alerts", fmt_num(len(spike_list)), "Anomalies" if spike_list else "Normal")

    st.markdown("<br>", unsafe_allow_html=True)

    # BREAKING ANOMALY ALERT BANNER & 24H VOLUME CHART
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown('<div class="section-title">BREAKING ANOMALY STATUS</div>', unsafe_allow_html=True)
        if not spikes_ok:
            render_unavailable_box("Spike Detection Telemetry")
        elif not spike_list:
            st.markdown(f"""
                <div class="card-box" style="border-left: 4px solid {COLORS['green']};">
                    <div style="font-weight:700; color:{COLORS['green']}; font-size:13px;">🟢 STABLE INGESTION STATUS</div>
                    <div style="font-size:12px; margin-top:4px; color:{COLORS['muted']};">
                        All ingestion pipelines streaming normally. No abnormal category spikes detected.
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            top = spike_list[0] if isinstance(spike_list[0], dict) else {}
            cat = top.get("category") or "General"
            curr = fmt_num(top.get("current_volume"))
            mult = top.get("multiplier")
            mult_s = f"{float(mult):.2f}x" if isinstance(mult, (int, float)) else "--"
            st.markdown(f"""
                <div class="card-box" style="border-left: 4px solid {COLORS['red']}; background:rgba(239,68,68,0.08);">
                    <div style="font-weight:700; color:{COLORS['red']}; font-size:13px;">⚠️ VOLUME SPIKE DETECTED</div>
                    <div style="font-size:13px; font-weight:700; margin-top:4px;">Category: {cat}</div>
                    <div style="font-size:12px; color:{COLORS['muted']}; margin-top:4px;">
                        Current Velocity: <b>{curr}</b> art/hr<br>
                        Spike Multiplier: <span style="color:{COLORS['orange']}; font-weight:700;">{mult_s}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">24-HOUR ARTICLE VOLUME TREND</div>', unsafe_allow_html=True)
        vol_res, vol_ok = fetch_api("/api/analytics/volume", params={"window": "24h", "bucket": "1h"})
        vol_data = first_present(vol_res, ["data", "timeline", "items"], []) if vol_ok else []
        if not vol_ok or not vol_data:
            render_empty_box("Volume telemetry data initializing...")
        else:
            try:
                df_vol = pd.DataFrame(vol_data)
                time_col = "timestamp" if "timestamp" in df_vol.columns else ("time" if "time" in df_vol.columns else df_vol.columns[0])
                count_col = "count" if "count" in df_vol.columns else df_vol.columns[1]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_vol[time_col], y=df_vol[count_col], mode="lines+markers", fill="tozeroy",
                    line=dict(color=COLORS["cyan"], width=2.5),
                    marker=dict(size=5, color=COLORS["cyan"]),
                    fillcolor="rgba(6, 182, 212, 0.15)",
                    hovertemplate="%{x}<br>Volume: <b>%{y} articles</b><extra></extra>"
                ))
                st.plotly_chart(apply_plotly_dark_theme(fig, height=160), use_container_width=True)
            except Exception:
                render_unavailable_box("Volume Chart")

    st.markdown("<br>", unsafe_allow_html=True)

    # LIVE NEWS FEED & DISTRIBUTION CHARTS
    f_col, c_col = st.columns([1, 1])

    with f_col:
        st.markdown('<div class="section-title">LATEST LIVE ARTICLES</div>', unsafe_allow_html=True)
        feed_res, feed_ok = fetch_api("/api/live-feed", params={"limit": 5})
        articles = first_present(feed_res, ["articles"], []) if feed_ok else []
        if not feed_ok:
            render_unavailable_box("Live News Feed")
        elif not articles:
            render_empty_box("No live articles ingested yet.")
        else:
            for a in articles[:5]:
                if not isinstance(a, dict):
                    continue
                sent = a.get("sentiment") or "Neutral"
                sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
                st.markdown(f"""
                    <div class="card-box" style="margin-bottom:8px; padding:10px 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:start;">
                            <div style="font-size:13px; font-weight:600; color:#F3F4F6; flex:1;">{a.get('title','Untitled')}</div>
                            <span style="font-size:10.5px; color:{COLORS['muted']}; white-space:nowrap; margin-left:8px;">{time_ago(a.get('published_date'))}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <div>
                                <span class="badge badge-purple">{a.get('category','General')}</span>
                                <span style="font-size:11px; color:{COLORS['muted']}; margin-left:6px;">{a.get('source','Unknown')}</span>
                            </div>
                            <span class="badge {sent_cls}">{sent}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with c_col:
        st.markdown('<div class="section-title">ANALYTICS DISTRIBUTION</div>', unsafe_allow_html=True)
        t_src, t_cat, t_sent = st.tabs(["Top Sources", "Categories", "Sentiment Breakdown"])

        with t_src:
            if sources_dict:
                df_src = pd.DataFrame(list(sources_dict.items()), columns=["Source", "Articles"]).sort_values("Articles")
                total_src_art = df_src["Articles"].sum() or 1
                top_src_name = df_src.iloc[-1]["Source"] if len(df_src) > 0 else "Unknown"
                top_src_count = df_src.iloc[-1]["Articles"] if len(df_src) > 0 else 0
                top_src_pct = (top_src_count / total_src_art) * 100

                fig_src = px.bar(
                    df_src, x="Articles", y="Source", orientation="h",
                    color="Source",
                    color_discrete_sequence=[COLORS["cyan"], COLORS["blue"], COLORS["purple"], COLORS["green"]],
                    text="Articles"
                )
                fig_src.update_traces(
                    texttemplate='%{text:,}',
                    textposition='outside',
                    marker_line_color='rgba(255,255,255,0.1)',
                    marker_line_width=1
                )
                fig_src.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
                st.plotly_chart(apply_plotly_dark_theme(fig_src, height=210), use_container_width=True)

                st.markdown(f"""
                    <div style="background:rgba(6,182,212,0.08); border:1px solid rgba(6,182,212,0.25); border-radius:6px; padding:8px 12px; font-size:11.5px; color:{COLORS['text']};">
                        💡 <b>Source Insight:</b> <b>{top_src_name}</b> is the leading provider with <b>{fmt_num(top_src_count)}</b> articles (<b>{top_src_pct:.1f}%</b> volume share across publishers).
                    </div>
                """, unsafe_allow_html=True)
            else:
                render_empty_box("No source distribution data available.")

        with t_cat:
            cats = first_present(metrics_res, ["categories", "category_distribution", "top_categories"], {}) or {}
            if cats:
                df_cat = pd.DataFrame(list(cats.items()), columns=["Category", "Count"])
                sorted_cat = df_cat.sort_values("Count", ascending=False)
                top_cat = sorted_cat.iloc[0]["Category"] if len(sorted_cat) > 0 else "General"
                top_cat_cnt = sorted_cat.iloc[0]["Count"] if len(sorted_cat) > 0 else 0
                top_cat_pct = (top_cat_cnt / df_cat["Count"].sum() * 100) if df_cat["Count"].sum() > 0 else 0

                fig_cat = px.pie(
                    df_cat, values="Count", names="Category", hole=0.55,
                    color_discrete_sequence=[COLORS["blue"], COLORS["cyan"], COLORS["purple"], COLORS["green"], COLORS["orange"], COLORS["red"]]
                )
                fig_cat.update_traces(
                    textposition='inside',
                    textinfo='percent',
                    insidetextorientation='horizontal',
                    hoverinfo='label+value+percent'
                )
                st.plotly_chart(apply_plotly_dark_theme(fig_cat, height=210), use_container_width=True)

                st.markdown(f"""
                    <div style="background:rgba(139,92,246,0.08); border:1px solid rgba(139,92,246,0.25); border-radius:6px; padding:8px 12px; font-size:11.5px; color:{COLORS['text']};">
                        💡 <b>Category Insight:</b> <b>{top_cat}</b> makes up <b>{top_cat_pct:.1f}%</b> of incoming raw feed articles. Real-time NLP classifiers categorize sub-topics into Business, Tech, Politics & World.
                    </div>
                """, unsafe_allow_html=True)
            else:
                render_empty_box("No category distribution data available.")

        with t_sent:
            sents = first_present(metrics_res, ["sentiment", "sentiment_distribution"], {}) or {}
            if sents:
                df_sent = pd.DataFrame(list(sents.items()), columns=["Sentiment", "Count"])
                total_sent = df_sent["Count"].sum() or 1
                neu_cnt = df_sent[df_sent["Sentiment"] == "Neutral"]["Count"].sum() if len(df_sent[df_sent["Sentiment"] == "Neutral"]) > 0 else 0
                pos_cnt = df_sent[df_sent["Sentiment"] == "Positive"]["Count"].sum() if len(df_sent[df_sent["Sentiment"] == "Positive"]) > 0 else 0
                neg_cnt = df_sent[df_sent["Sentiment"] == "Negative"]["Count"].sum() if len(df_sent[df_sent["Sentiment"] == "Negative"]) > 0 else 0

                fig_sent = px.pie(
                    df_sent, values="Count", names="Sentiment", hole=0.55,
                    color="Sentiment", color_discrete_map=SENTIMENT_COLOR
                )
                fig_sent.update_traces(
                    textposition='inside',
                    textinfo='percent',
                    hoverinfo='label+value+percent'
                )
                st.plotly_chart(apply_plotly_dark_theme(fig_sent, height=210), use_container_width=True)

                st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:6px; padding:8px 12px; font-size:11.5px; color:{COLORS['text']};">
                        💡 <b>Sentiment Insight:</b> <b>{(neu_cnt/total_sent*100):.1f}%</b> objective neutral reporting, with <b>{(pos_cnt/total_sent*100):.1f}%</b> positive market trends & <b>{(neg_cnt/total_sent*100):.1f}%</b> negative anomaly alerts.
                    </div>
                """, unsafe_allow_html=True)
            else:
                render_empty_box("No sentiment overview data available.")


# =====================================================
# PAGE 2 — LIVE NEWS FEED
# =====================================================
elif page == "Live News Feed":
    render_header("LIVE NEWS FEED & FILTERING", "Inspect incoming articles with multi-parameter filter controls")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sel_source = st.selectbox("Filter Source", ["All Sources", "Economic Times", "The Hindu", "Indian Express", "Hindustan Times"])
    with c2:
        sel_cat = st.selectbox("Filter Category", ["All Categories", "Business", "Technology", "Politics", "Sports", "World", "General"])
    with c3:
        sel_sent = st.selectbox("Filter Sentiment", ["All Sentiments", "Positive", "Neutral", "Negative"])
    with c4:
        search_kw = st.text_input(
            "Headline Keyword Search 🔍",
            placeholder="e.g. RBI, inflation, Kerala, stocks...",
            help="Type any word or phrase (e.g., company, leader, city) to filter article headlines live."
        )

    st.markdown(f"""
        <div style="background:rgba(6,182,212,0.06); border:1px solid rgba(6,182,212,0.2); border-radius:6px; padding:8px 12px; font-size:12px; margin: 6px 0 14px 0; color:{COLORS['text']};">
            💡 <b>How Search Works:</b> Type any topic keyword (e.g., <i>'market'</i>, <i>'railway'</i>, <i>'elections'</i>, <i>'Kerala'</i>) into <b>Headline Keyword Search</b> to filter article titles in real time.
        </div>
    """, unsafe_allow_html=True)

    feed_res, feed_ok = fetch_api("/api/live-feed", params={"limit": 50})
    if not feed_ok:
        render_unavailable_box("Live News Feed")
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

        st.caption(f"Showing **{len(filtered)}** of **{len(articles)}** live ingested articles")

        if not filtered:
            render_empty_box("No articles match the current filter selection.")
        else:
            for a in filtered:
                sent = a.get("sentiment") or "Neutral"
                sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
                with st.expander(f"[{a.get('source','Unknown')}] {a.get('title','Untitled')}"):
                    st.markdown(f"**Category:** `{a.get('category','--')}` &nbsp;|&nbsp; **Sentiment:** <span class='badge {sent_cls}'>{sent}</span> &nbsp;|&nbsp; **Published:** {time_ago(a.get('published_date'))}", unsafe_allow_html=True)
                    st.write(a.get("summary") or "No summary available.")
                    if a.get("link") and a.get("link") != "#":
                        st.markdown(f"[Open Original Article Link →]({a.get('link')})")


# =====================================================
# PAGE 3 — SEARCH WORKSPACE
# =====================================================
elif page == "Search Workspace":
    render_header("SEARCH WORKSPACE", "Hybrid RRF, lexical BM25, and 384-dimensional dense vector KNN search")

    st.info("💡 **Analytics Logic Context:** Hybrid search combines exact keyword matching (BM25) with semantic vector similarity (all-MiniLM-L6-v2) using Reciprocal Rank Fusion (RRF reranking) to maximize retrieval precision.")

    tabs = st.tabs(["Hybrid RRF Search", "BM25 Keyword Search", "Dense Vector KNN Search"])
    modes = ["hybrid", "bm25", "knn"]

    for tab, mode in zip(tabs, modes):
        with tab:
            q = st.text_input("Enter query phrase", key=f"q_{mode}", placeholder="e.g. RBI inflation rate decision...")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                search_cat = st.selectbox("Category Filter", ["All", "Business", "Technology", "Politics", "Sports", "World"], key=f"cat_{mode}")
            with sc2:
                search_sent = st.selectbox("Sentiment Filter", ["All", "Positive", "Neutral", "Negative"], key=f"sent_{mode}")
            with sc3:
                search_limit = st.slider("Results Count", 5, 30, 10, key=f"lim_{mode}")

            if q.strip():
                params = {"q": q.strip(), "type": mode, "limit": search_limit}
                if search_cat != "All":
                    params["category"] = search_cat

                s_res, s_ok = fetch_api("/api/search", params=params)
                if not s_ok:
                    render_unavailable_box("Search Engine")
                else:
                    hits = [h for h in (first_present(s_res, ["articles", "results"], []) or []) if isinstance(h, dict)]
                    if not hits:
                        render_empty_box("No matching documents found for this query.")
                    else:
                        st.caption(f"Retrieved **{len(hits)}** matching documents using **{mode.upper()}** engine")
                        for h in hits:
                            score = h.get("_score") or h.get("score")
                            score_s = f"{float(score):.3f}" if isinstance(score, (int, float)) else "--"
                            st.markdown(f"""
                                <div class="card-box">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                        <span class="badge badge-cyan">{h.get('source','Unknown')}</span>
                                        <span style="font-size:11px; color:{COLORS['muted']}; font-family:monospace;">Relevance Score: {score_s}</span>
                                    </div>
                                    <div style="font-size:15px; font-weight:700; margin:6px 0;">
                                        <a href="{h.get('link','#')}" target="_blank" style="color:{COLORS['cyan']}; text-decoration:none;">{h.get('title','Untitled')}</a>
                                    </div>
                                    <div style="font-size:12.5px; color:{COLORS['muted']};">{h.get('summary','No summary available.')}</div>
                                </div>
                            """, unsafe_allow_html=True)


# =====================================================
# PAGE 4 — TEMPORAL ANALYTICS
# =====================================================
elif page == "Temporal Analytics":
    render_header("TEMPORAL ANALYTICS & TREND INTELLIGENCE", "Sliding window volume trends, z-score volume spike alerts, and cross-source signal discovery")

    st.markdown("""
    <div style="background:rgba(59,130,246,0.08); border-left:4px solid #3B82F6; padding:12px 14px; border-radius:6px; font-size:12.5px; margin-bottom:16px;">
        <b>Analytics Logic & Context:</b><br>
        • <b>Volume Trends:</b> Measures article generation rate over sliding windows (15m, 1h, 6h, 24h, 7d).<br>
        • <b>Volume Spikes:</b> Flags categories where current hourly volume exceeds historical baseline average volume by 2.0x+.<br>
        • <b>Cross-Source Signals:</b> Identifies breaking news topics appearing across 2 or more distinct publishers simultaneously.
    </div>
    """, unsafe_allow_html=True)

    time_win = st.select_slider("Select Sliding Window", options=["15m", "1h", "6h", "24h", "7d"], value="24h")

    t1, t2, t3, t4 = st.tabs(["Source Trends", "Category Trends", "Sentiment Timeline", "Spikes & Signals"])

    with t1:
        src_res, src_ok = fetch_api("/api/analytics/source-trends", params={"window": time_win, "bucket": "1h"})
        src_data = first_present(src_res, ["data", "timeline", "items"], []) if src_ok else []
        if not src_ok or not src_data:
            render_empty_box("No source trend data found for this window.")
        else:
            try:
                df = pd.DataFrame(src_data)
                time_col = "timestamp" if "timestamp" in df.columns else ("time" if "time" in df.columns else df.columns[0])
                df_m = df.melt(id_vars=[time_col], var_name="source", value_name="count")
                fig = px.line(df_m, x=time_col, y="count", color="source", color_discrete_sequence=[COLORS["cyan"], COLORS["blue"], COLORS["purple"], COLORS["green"]])
                st.plotly_chart(apply_plotly_dark_theme(fig, height=320), use_container_width=True)
            except Exception:
                render_unavailable_box("Source Trends")

    with t2:
        cat_res, cat_ok = fetch_api("/api/analytics/category-trends", params={"window": time_win, "bucket": "1h"})
        cat_data = first_present(cat_res, ["data", "timeline", "items"], []) if cat_ok else []
        if not cat_ok or not cat_data:
            render_empty_box("No category trend data found for this window.")
        else:
            try:
                df = pd.DataFrame(cat_data)
                time_col = "timestamp" if "timestamp" in df.columns else ("time" if "time" in df.columns else df.columns[0])
                df_m = df.melt(id_vars=[time_col], var_name="category", value_name="count")
                fig = px.area(df_m, x=time_col, y="count", color="category")
                st.plotly_chart(apply_plotly_dark_theme(fig, height=320), use_container_width=True)
            except Exception:
                render_unavailable_box("Category Trends")

    with t3:
        sent_res, sent_ok = fetch_api("/api/analytics/sentiment-trends", params={"window": time_win, "bucket": "1h"})
        sent_data = first_present(sent_res, ["data", "timeline", "items"], []) if sent_ok else []
        if not sent_ok or not sent_data:
            render_empty_box("No sentiment trend data found for this window.")
        else:
            try:
                df = pd.DataFrame(sent_data)
                time_col = "timestamp" if "timestamp" in df.columns else ("time" if "time" in df.columns else df.columns[0])
                df_m = df.melt(id_vars=[time_col], var_name="sentiment", value_name="count")
                fig = px.line(df_m, x=time_col, y="count", color="sentiment", color_discrete_map=SENTIMENT_COLOR)
                st.plotly_chart(apply_plotly_dark_theme(fig, height=320), use_container_width=True)
            except Exception:
                render_unavailable_box("Sentiment Timeline")

    with t4:
        sp_res, sp_ok = fetch_api("/api/analytics/spikes")
        spikes = first_present(sp_res, ["spikes"], []) if sp_ok else []
        if spikes:
            for sp in spikes:
                if isinstance(sp, dict):
                    st.warning(f"⚠️ Activity Spike in **{sp.get('category','General')}**: Current volume **{fmt_num(sp.get('current_volume'))} art/hr** vs baseline **{fmt_num(sp.get('baseline_volume'))} art/hr** (Multiplier: {sp.get('multiplier',1):.2f}x)")
        else:
            st.success("🟢 Volume activity status normal. No anomalous spikes detected.")

        st.markdown("---")
        st.markdown("#### Emerging Keywords & Named Entities Velocity")
        k_col, e_col = st.columns(2)
        with k_col:
            kw_res, kw_ok = fetch_api("/api/analytics/keywords")
            kws = first_present(kw_res, ["keywords"], []) if kw_ok else []
            if kws:
                st.dataframe(keywords_to_display_df(kws), use_container_width=True, hide_index=True)
            else:
                render_empty_box("No emerging keyword velocity data.")

        with e_col:
            ent_res, ent_ok = fetch_api("/api/analytics/entities")
            ents = first_present(ent_res, ["entities"], []) if ent_ok else []
            if ents:
                st.dataframe(entities_to_display_df(ents), use_container_width=True, hide_index=True)
            else:
                render_empty_box("No emerging entity velocity data.")


# =====================================================
# PAGE 5 — AI ANALYST (RAG)
# =====================================================
elif page == "AI Analyst (RAG)":
    render_header("AI NEWS ANALYST", "Grounded Agentic RAG assistant with intent routing and citation provenance")

    st.info("💡 **Analytics Logic Context:** The AI Analyst classifies user intent, queries Elasticsearch vector & BM25 indices deterministically, synthesizes a grounded answer, and lists exact article citations to prevent AI hallucinations.")

    b1, b2, b3 = st.columns(3)
    user_q = st.session_state.get("ai_q", "")
    if b1.button("What's trending in Indian markets today?"):
        user_q = "What's trending in Indian markets today?"
    if b2.button("What major news volume spikes occurred today?"):
        user_q = "What major news volume spikes occurred today?"
    if b3.button("What topics are reported across multiple sources?"):
        user_q = "What topics are reported across multiple sources?"

    input_q = st.text_area("Enter question for AI Analyst", value=user_q, placeholder="e.g. Compare coverage of market trends across Economic Times and The Hindu...")

    if st.button("Ask AI Analyst", type="primary") and input_q.strip():
        with st.spinner("Routing intent & generating grounded synthesis..."):
            rag_res, rag_ok = post_api("/api/ai/ask", {"question": input_q.strip()})

        if not rag_ok:
            st.error(f"AI Analyst temporarily unavailable: {rag_res.get('error','API unreachable')}")
        else:
            answer = rag_res.get("answer")
            st.markdown("#### AI Synthesized Answer")
            if answer:
                st.info(answer)
            else:
                st.warning("Insufficient evidence was found in the indexed corpus to answer this query.")

            insights = first_present(rag_res, ["insights"], []) or []
            if insights:
                st.markdown("#### Key Takeaways")
                for ins in insights:
                    st.markdown(f"- {ins}")

            sources = [s for s in (first_present(rag_res, ["sources"], []) or []) if isinstance(s, dict)]
            if sources:
                st.markdown("#### Source Evidence & Citations")
                for idx, src in enumerate(sources, 1):
                    st.markdown(f"""
                        <div class="card-box">
                            <div style="font-weight:700; color:{COLORS['cyan']};">[{idx}] {src.get('title','Untitled')}</div>
                            <div style="font-size:11.5px; color:{COLORS['muted']}; margin-top:3px;">Source: {src.get('source','--')} · Published: {time_ago(src.get('published_date'))}</div>
                        </div>
                    """, unsafe_allow_html=True)

            with st.expander("Execution Trace & Tool Provenance"):
                tools = first_present(rag_res, ["tools_executed"], []) or []
                st.markdown(f"""
                    <div class="trace-box">
                        Intent Detected : {rag_res.get('intent','UNKNOWN')}<br>
                        Provider        : {rag_res.get('provider','RAG')}<br>
                        Tools Executed  : {', '.join(tools) if tools else '--'}<br>
                        Retrieved Docs  : {len(sources)}
                    </div>
                """, unsafe_allow_html=True)


# =====================================================
# PAGE 6 — ARTICLE INSPECTOR
# =====================================================
elif page == "Article Inspector":
    render_header("ARTICLE INSPECTOR", "Inspect raw documents, extracted entities, NLP metadata, and pipeline lease statuses")

    target_id = st.text_input("Enter Article ID or Article Link URL")
    if target_id.strip():
        art_res, art_ok = fetch_api(f"/api/articles/{target_id.strip()}")
        if not art_ok or not art_res:
            st.error("Article not found in database.")
        else:
            st.markdown(f"### {art_res.get('title','Untitled Article')}")
            st.caption(f"Source: **{art_res.get('source','--')}** · Published: **{time_ago(art_res.get('published_date'))}**")

            tabs = st.tabs(["Summary", "Full Content", "Keywords", "Entities", "Source Link", "Pipeline Metadata"])
            with tabs[0]:
                st.write(art_res.get("summary") or "No summary extracted.")
            with tabs[1]:
                st.text_area("Cleaned Text Body", art_res.get("clean_content") or "No content available.", height=250)
            with tabs[2]:
                kws = art_res.get("keywords") or []
                st.write(", ".join(kws) if kws else "No keywords extracted.")
            with tabs[3]:
                ents = art_res.get("entities") or []
                if ents:
                    st.dataframe(entities_to_display_df(ents), use_container_width=True, hide_index=True)
                else:
                    st.caption("No named entities extracted.")
            with tabs[4]:
                if art_res.get("link") and art_res.get("link") != "#":
                    st.markdown(f"[Open Original Publisher Link →]({art_res.get('link')})")
                else:
                    st.caption("No valid URL available.")
            with tabs[5]:
                st.json(art_res.get("processing") or {})


# =====================================================
# PAGE 7 — SYSTEM HEALTH
# =====================================================
elif page == "System Health":
    render_header("SYSTEM HEALTH & INFRASTRUCTURE MONITORING", "Node connection states, database health, and pipeline queue metrics")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("API Server", "Healthy" if health_ok else "Offline")
    m2.metric("MongoDB", "Healthy" if mongo_status in ("ok", "healthy", "up") else "Offline")
    m3.metric("Elasticsearch", "Healthy" if es_status in ("ok", "healthy", "up") else "Offline")
    m4.metric("Total Corpus Documents", fmt_num(first_present(metrics_res, ["total_articles"], 0)))

    st.markdown("---")
    st.markdown("#### Pipeline Queue Metrics")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Completed Queue", fmt_num(first_present(metrics_res, ["completed_articles"], 0)))
    q2.metric("Pending Queue", fmt_num(first_present(metrics_res, ["pending_articles"], 0)))
    q3.metric("Failed / Retry", fmt_num(first_present(metrics_res, ["failed_articles"], 0)))
    q4.metric("Consumer Lag", fmt_num(first_present(metrics_res, ["consumer_lag"], None)))

    st.markdown("---")
    st.markdown("#### Service Status Registry")
    for name, ok in services:
        st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid {COLORS['card_border']}; display:flex; justify-content:space-between;'><span>{name}</span>{status_dot(ok)}</div>", unsafe_allow_html=True)
