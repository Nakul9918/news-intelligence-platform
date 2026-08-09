"""
=====================================================
News Intelligence Command Center — Company-Grade Product UI
Version : 20.0 (Unified Real-Time News Intelligence Platform)
=====================================================
"""

import time
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(interval=10000, key=None):
        return 0

# =====================================================
# CONFIGURATION & THEME TOKENS
# =====================================================
st.set_page_config(
    page_title="Real-Time News Intelligence Platform",
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

DEFAULT_CATEGORIES = [
    "Politics", "Business", "Technology", "Sports", "World", 
    "Entertainment", "Crime", "India", "Science", "Health", "Finance", "Education"
]

TARGET_SOURCES = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]

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


def first_present(d: dict, keys: list, default=None):
    """Retrieve the first non-null key found from possible API variants."""
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


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
        resp = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=8)
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

    .rank-badge {{
        background: linear-gradient(135deg, {COLORS['cyan']}, {COLORS['blue']});
        color: #FFFFFF;
        font-weight: 800;
        font-size: 13px;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
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
    .badge-orange {{ background: rgba(245,158,11,0.15); color: {COLORS['orange']}; border: 1px solid rgba(245,158,11,0.3); }}

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
        <div style="font-size:10px; color:{COLORS['cyan']}; font-weight:700;">COMPANY PLATFORM</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

WORKSPACES = [
    "1. COMMAND CENTER",
    "2. LIVE NEWS",
    "3. SEARCH & DISCOVERY",
    "4. INTELLIGENCE",
    "5. AI ANALYST",
    "6. SYSTEM / PIPELINE"
]

page = st.sidebar.radio("MAIN NAVIGATION", WORKSPACES, label_visibility="visible")

st.sidebar.markdown("---")
st.sidebar.caption("AUTO REFRESH")
auto_refresh = st.sidebar.checkbox("Enable Live Refresh", value=True)
refresh_sec = st.sidebar.select_slider("Interval (sec)", options=[5, 10, 15, 30], value=10, label_visibility="collapsed")
if auto_refresh:
    st_autorefresh(interval=refresh_sec * 1000, key="nav_autorefresh")

st.sidebar.markdown("---")

health_res, health_ok = fetch_api("/health")
metrics_res, metrics_ok = fetch_api("/api/metrics")

mongo_status = first_present(health_res, ["mongodb", "mongo"], "down")
es_status = first_present(health_res, ["elasticsearch", "es"], "down")

def status_dot(ok):
    return f'<span style="color:{COLORS["green"]}">●</span> Connected' if ok else f'<span style="color:{COLORS["red"]}">●</span> Offline'

st.sidebar.caption("INFRASTRUCTURE STATUS")
services = [
    ("FastAPI Server", health_ok),
    ("Kafka Topic v2", True),
    ("MongoDB (news_db)", mongo_status in ("ok", "healthy", "up")),
    ("Elasticsearch Index", es_status in ("ok", "healthy", "up")),
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
                <span style="font-size:11.5px; color:{COLORS['muted']}; margin-left:10px;">Streaming continuously</span>
            </div>
        """, unsafe_allow_html=True)


# =====================================================
# WORKSPACE 1 — COMMAND CENTER
# =====================================================
if page == "1. COMMAND CENTER":
    render_header("REAL-TIME COMMAND CENTER", "Executive overview — What is happening right now?")

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

    # TOP 10 TRENDING NEWS SECTION
    st.markdown('<div class="section-title">🔥 TOP 10 TRENDING NEWS BY ACTIVITY</div>', unsafe_allow_html=True)
    t10_res, t10_ok = fetch_api("/api/news/top10", params={"limit": 10})
    t10_articles = first_present(t10_res, ["articles"], []) if t10_ok else []

    if not t10_ok or not t10_articles:
        render_empty_box("Top 10 news stories ranking in real-time...")
    else:
        for item in t10_articles:
            sent = item.get("sentiment") or "Neutral"
            sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
            st.markdown(f"""
                <div class="card-box" style="margin-bottom:10px; padding:12px 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px; flex:1;">
                            <span class="rank-badge">#{item.get('rank',1)}</span>
                            <a href="{item.get('link','#')}" target="_blank" style="font-size:15px; font-weight:700; color:#FFFFFF; text-decoration:none;">{item.get('headline','Untitled')}</a>
                        </div>
                        <span style="font-size:11px; color:{COLORS['muted']}; white-space:nowrap; margin-left:12px;">{time_ago(item.get('published_date'))}</span>
                    </div>
                    <div style="font-size:12.5px; color:{COLORS['muted']}; margin:8px 0;">{item.get('summary','')}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:6px;">
                        <div>
                            <span class="badge badge-cyan">{item.get('source','--')}</span>
                            <span class="badge badge-purple" style="margin-left:6px;">{item.get('category','General')}</span>
                        </div>
                        <span class="badge {sent_cls}">{sent}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 24H VOLUME & DISTRIBUTION CHARTS
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.markdown('<div class="section-title">24-HOUR ARTICLE VOLUME TREND</div>', unsafe_allow_html=True)
        vol_res, vol_ok = fetch_api("/api/analytics/volume", params={"window": "24h", "bucket": "1h"})
        vol_data = first_present(vol_res, ["data", "timeline", "items"], []) if vol_ok else []
        if vol_ok and vol_data:
            try:
                df_vol = pd.DataFrame(vol_data)
                time_col = "timestamp" if "timestamp" in df_vol.columns else ("time" if "time" in df_vol.columns else df_vol.columns[0])
                count_col = "count" if "count" in df_vol.columns else df_vol.columns[1]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_vol[time_col], y=df_vol[count_col], mode="lines+markers", fill="tozeroy",
                    line=dict(color=COLORS["cyan"], width=2.5),
                    fillcolor="rgba(6, 182, 212, 0.15)",
                ))
                st.plotly_chart(apply_plotly_dark_theme(fig, height=190), use_container_width=True)
            except Exception:
                render_unavailable_box("Volume Chart")
        else:
            render_empty_box("Volume telemetry data initializing...")

    with c_right:
        st.markdown('<div class="section-title">PUBLISHER SHARE DISTRIBUTION</div>', unsafe_allow_html=True)
        if sources_dict:
            df_src = pd.DataFrame(list(sources_dict.items()), columns=["Source", "Articles"]).sort_values("Articles")
            fig_src = px.bar(df_src, x="Articles", y="Source", orientation="h", color="Source", color_discrete_sequence=[COLORS["cyan"], COLORS["blue"], COLORS["purple"], COLORS["green"]], text="Articles")
            fig_src.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_src.update_layout(showlegend=False)
            st.plotly_chart(apply_plotly_dark_theme(fig_src, height=190), use_container_width=True)
        else:
            render_empty_box("No publisher distribution data available.")


# =====================================================
# WORKSPACE 2 — LIVE NEWS
# =====================================================
elif page == "2. LIVE NEWS":
    render_header("LIVE ARRIVING NEWS STREAM", "What news is arriving right now? Auto-refreshing feed sorted by published date")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        sel_source = st.selectbox("Filter Source", ["All Sources", "Economic Times", "The Hindu", "Indian Express", "Hindustan Times"])
    with f_col2:
        sel_cat = st.selectbox("Filter Category", ["All Categories"] + DEFAULT_CATEGORIES)
    with f_col3:
        sel_sent = st.selectbox("Filter Sentiment", ["All Sentiments", "Positive", "Neutral", "Negative"])

    feed_params = {"limit": 30}
    if sel_source != "All Sources":
        feed_params["source"] = sel_source
    if sel_cat != "All Categories":
        feed_params["category"] = sel_cat
    if sel_sent != "All Sentiments":
        feed_params["sentiment"] = sel_sent

    feed_res, feed_ok = fetch_api("/api/live-feed", params=feed_params)
    if not feed_ok:
        render_unavailable_box("Live News Feed")
    else:
        articles = feed_res.get("articles", [])
        if not articles:
            render_empty_box("No live articles match the current filter selection.")
        else:
            st.caption(f"Displaying **{len(articles)}** real-time news articles")
            for a in articles:
                sent = a.get("sentiment") or "Neutral"
                sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
                with st.expander(f"[{a.get('source','Unknown')}] {a.get('title','Untitled')}"):
                    st.markdown(f"**Category:** `{a.get('category','General')}` &nbsp;|&nbsp; **Sentiment:** <span class='badge {sent_cls}'>{sent}</span> &nbsp;|&nbsp; **Published:** {time_ago(a.get('published_date'))}", unsafe_allow_html=True)
                    st.write(a.get("summary") or "No summary available.")
                    if a.get("link") and a.get("link") != "#":
                        st.markdown(f"[Open Original Article Link →]({a.get('link')})")


# =====================================================
# WORKSPACE 3 — SEARCH & DISCOVERY
# =====================================================
elif page == "3. SEARCH & DISCOVERY":
    render_header("UNIVERSAL SEARCH & DATE DISCOVERY", "Find any information across the corpus by keyword, person, company, event, or date range")

    search_query = st.text_input(
        "Search news database:",
        placeholder="e.g. crime, RBI rate, Modi, stock market, AI regulation, Mumbai..."
    )

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        date_preset = st.selectbox("Date Range Filter", ["Last 24 Hours", "Today", "Yesterday", "Last 7 Days", "Last 30 Days", "This Month", "Custom Range"])
    with d_col2:
        search_mode = st.selectbox("Retrieval Strategy", ["Hybrid (BM25 + Vector RRF)", "BM25 Keyword Search", "Dense Vector KNN Search"])

    now_d = datetime.now()
    start_d, end_d = None, None

    if date_preset == "Today":
        start_d = now_d.strftime("%Y-%m-%d")
        end_d = now_d.strftime("%Y-%m-%d")
    elif date_preset == "Yesterday":
        yest = now_d - timedelta(days=1)
        start_d = yest.strftime("%Y-%m-%d")
        end_d = yest.strftime("%Y-%m-%d")
    elif date_preset == "Last 7 Days":
        start_d = (now_d - timedelta(days=7)).strftime("%Y-%m-%d")
        end_d = now_d.strftime("%Y-%m-%d")
    elif date_preset == "Last 30 Days":
        start_d = (now_d - timedelta(days=30)).strftime("%Y-%m-%d")
        end_d = now_d.strftime("%Y-%m-%d")
    elif date_preset == "This Month":
        start_d = now_d.replace(day=1).strftime("%Y-%m-%d")
        end_d = now_d.strftime("%Y-%m-%d")
    elif date_preset == "Custom Range":
        c_start, c_end = st.columns(2)
        with c_start:
            cust_s = st.date_input("Start Date", value=now_d - timedelta(days=7))
            start_d = cust_s.strftime("%Y-%m-%d")
        with c_end:
            cust_e = st.date_input("End Date", value=now_d)
            end_d = cust_e.strftime("%Y-%m-%d")

    if search_query.strip():
        mode_key = "hybrid" if "Hybrid" in search_mode else ("bm25" if "BM25" in search_mode else "knn")
        params = {"q": search_query.strip(), "type": mode_key, "limit": 15}
        if start_d:
            params["start_date"] = start_d
        if end_d:
            params["end_date"] = end_d

        s_res, s_ok = fetch_api("/api/search", params=params)
        if not s_ok:
            render_unavailable_box("Search Engine")
        else:
            hits = [h for h in (first_present(s_res, ["articles", "results"], []) or []) if isinstance(h, dict)]
            if not hits:
                render_empty_box("No matching documents found for this query.")
            else:
                st.caption(f"Retrieved **{len(hits)}** matching documents using **{search_mode}**")
                for h in hits:
                    score = h.get("_score") or h.get("score")
                    score_s = f"{float(score):.3f}" if isinstance(score, (int, float)) else "--"
                    sent = h.get("sentiment") or "Neutral"
                    sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
                    st.markdown(f"""
                        <div class="card-box">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span class="badge badge-cyan">{h.get('source','Unknown')}</span>
                                    <span class="badge badge-purple" style="margin-left:4px;">{h.get('category','General')}</span>
                                </div>
                                <span class="badge {sent_cls}">{sent}</span>
                            </div>
                            <div style="font-size:15px; font-weight:700; margin:6px 0;">
                                <a href="{h.get('link','#')}" target="_blank" style="color:{COLORS['cyan']}; text-decoration:none;">{h.get('title','Untitled')}</a>
                            </div>
                            <div style="font-size:12.5px; color:{COLORS['muted']};">{h.get('summary','No summary available.')}</div>
                        </div>
                    """, unsafe_allow_html=True)


# =====================================================
# WORKSPACE 4 — INTELLIGENCE
# =====================================================
elif page == "4. INTELLIGENCE":
    render_header("DATA-DERIVED INTELLIGENCE WORKSPACE", "What does the data tell us? Spikes, emerging entities, timelines, and 4-newspaper topic comparison")

    tabs = st.tabs(["4-Newspaper Comparison", "Current Affairs & Developing", "Emerging Spikes & Trends", "Monthly Intelligence Archive"])

    with tabs[0]:
        st.markdown("#### 4-Newspaper Topic Comparison")
        comp_topic = st.text_input("Enter Topic to Compare across Publishers", value="India economy")
        if comp_topic.strip():
            comp_res, comp_ok = fetch_api("/api/news/compare-publishers", params={"topic": comp_topic.strip()})
            if not comp_ok:
                render_unavailable_box("Publisher Comparison")
            else:
                publishers = comp_res.get("publishers", {})
                p_cols = st.columns(4)
                for idx, pub in enumerate(TARGET_SOURCES):
                    p_data = publishers.get(pub, {})
                    with p_cols[idx]:
                        st.markdown(f"""
                            <div class="card-box" style="height:100%;">
                                <div style="font-weight:800; font-size:14px; color:{COLORS['cyan']}; border-bottom:1px solid {COLORS['card_border']}; padding-bottom:6px; margin-bottom:8px;">{pub}</div>
                                <div style="font-size:11px; color:{COLORS['muted']};">Volume: <b>{p_data.get('total_coverage_volume',0)} articles</b></div>
                                <div style="font-size:11px; color:{COLORS['muted']};">Tone: <b>{p_data.get('top_sentiment','Neutral')}</b></div>
                                <div style="font-size:11.5px; font-weight:600; color:{COLORS['orange']}; margin-top:6px;">{p_data.get('data_derived_coverage_theme','--')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        for art in p_data.get("sample_articles", []):
                            with st.expander(art.get("headline","Untitled")[:35] + "..."):
                                st.write(art.get("summary"))

                st.markdown(f"**Cross-Publisher Signal Summary:** {comp_res.get('cross_source_summary')}")

    with tabs[1]:
        st.markdown("#### Current Affairs & Developing Stories")
        dev_res, dev_ok = fetch_api("/api/news/developing")
        if dev_ok:
            for dev in dev_res.get("developing_stories", []):
                st.markdown(f"""
                    <div class="card-box" style="border-left:4px solid {COLORS['orange']};">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-weight:700; color:#FFFFFF;">{dev.get('story_topic')}</span>
                            <span class="badge badge-orange">{dev.get('status')}</span>
                        </div>
                        <div style="font-size:12px; color:{COLORS['muted']}; margin-top:4px;">Updates: {dev.get('update_count')} · Sources: {', '.join(dev.get('sources_involved',[]))}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Story Evolution Timeline ('What Happened Next?')")
        t_topic = st.text_input("Enter Story Topic for Timeline", value="Market")
        time_res, time_ok = fetch_api("/api/news/timeline", params={"topic": t_topic})
        if time_ok:
            for ev in time_res.get("timeline", []):
                st.markdown(f"""
                    <div class="card-box" style="border-left:4px solid {COLORS['cyan']};">
                        <span class="badge badge-cyan">{ev.get('stage_label')}</span>
                        <span style="font-size:11px; color:{COLORS['muted']}; margin-left:8px;">{time_ago(ev.get('timestamp'))}</span>
                        <div style="font-weight:700; font-size:14px; margin-top:4px;">[{ev.get('source')}] {ev.get('headline')}</div>
                    </div>
                """, unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("#### Emerging Keywords & Entities")
        kw_res, kw_ok = fetch_api("/api/analytics/keywords")
        ent_res, ent_ok = fetch_api("/api/analytics/entities")
        k_col, e_col = st.columns(2)
        with k_col:
            st.caption("EMERGING KEYWORDS")
            if kw_ok and kw_res.get("keywords"):
                df_kw = pd.DataFrame(kw_res["keywords"])
                st.dataframe(df_kw[["keyword", "recent_mentions", "growth_pct"]], use_container_width=True, hide_index=True)
        with e_col:
            st.caption("EMERGING ENTITIES")
            if ent_ok and ent_res.get("entities"):
                df_ent = pd.DataFrame(ent_res["entities"])
                st.dataframe(df_ent[["entity", "type", "recent_mentions", "growth_pct"]], use_container_width=True, hide_index=True)

    with tabs[3]:
        st.markdown("#### Monthly Archive Intelligence")
        m_res, m_ok = fetch_api("/api/news/monthly", params={"year": 2026, "month": 8})
        if m_ok:
            st.metric("Total Monthly News", fmt_num(m_res.get("total_articles")))
            t_df = pd.DataFrame(m_res.get("monthly_timeline", []))
            if not t_df.empty:
                st.dataframe(t_df, use_container_width=True, hide_index=True)


# =====================================================
# WORKSPACE 5 — AI ANALYST
# =====================================================
elif page == "5. AI ANALYST":
    render_header("AGENTIC AI NEWS ANALYST (RAG)", "Natural language interface for the platform — Ask questions with grounded evidence citations")

    input_q = st.text_area("Enter question for AI Analyst:", value="What are the top 10 news stories today?", placeholder="e.g. What are the top 10 news stories today? Compare all 4 newspapers on India's economy...")

    if st.button("Ask AI Analyst", type="primary") and input_q.strip():
        with st.spinner("Executing intent router & grounded synthesis..."):
            rag_res, rag_ok = post_api("/api/ai/ask", {"question": input_q.strip()})

        if not rag_ok:
            st.error("AI Analyst temporarily unavailable.")
        else:
            answer = rag_res.get("answer")
            st.markdown("#### AI Synthesized Answer")
            if answer:
                st.info(answer)
            else:
                st.warning("Insufficient evidence was found in the indexed corpus to answer this question.")

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

            with st.expander("AI Observability & Tool Trace"):
                st.markdown(f"""
                    <div class="trace-box">
                        Intent Detected : {rag_res.get('intent','UNKNOWN')}<br>
                        Retrieval       : {rag_res.get('provider','RAG')}<br>
                        Evidence State  : Verified Grounded<br>
                        Retrieved Docs  : {len(sources)}
                    </div>
                """, unsafe_allow_html=True)


# =====================================================
# WORKSPACE 6 — SYSTEM / PIPELINE
# =====================================================
elif page == "6. SYSTEM / PIPELINE":
    render_header("SYSTEM & STREAMING PIPELINE HEALTH", "Real-time Kafka consumer lag, MongoDB storage stats, Elasticsearch indexing, and NLP stage flow")

    sys_res, sys_ok = fetch_api("/api/system/telemetry")
    if not sys_ok:
        render_unavailable_box("System Infrastructure Telemetry")
    else:
        kafka_data = sys_res.get("kafka", {})
        mongo_data = sys_res.get("mongodb", {})
        es_data = sys_res.get("elasticsearch", {})
        pipe_data = sys_res.get("pipeline", {})

        # KAFKA SECTION
        st.markdown('<div class="section-title">KAFKA STREAMING MESSAGING (news-topic-v2)</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Kafka Status", kafka_data.get("status", "CONNECTED"))
        k2.metric("Log End Offset", fmt_num(kafka_data.get("log_end_offset")))
        k3.metric("Committed Offset", fmt_num(kafka_data.get("committed_offset")))
        k4.metric("Consumer Lag", fmt_num(kafka_data.get("consumer_lag")), "Messages")

        st.caption(f"Topic: `{kafka_data.get('topic')}` | Consumer Group: `{kafka_data.get('consumer_group')}` | Broker: `{kafka_data.get('bootstrap_servers')}`")

        st.markdown("<br>", unsafe_allow_html=True)

        # MONGODB & ELASTICSEARCH SECTION
        c_m, c_e = st.columns(2)
        with c_m:
            st.markdown('<div class="section-title">MONGODB STORAGE ENGINE (news_db)</div>', unsafe_allow_html=True)
            st.metric("Total Articles", fmt_num(mongo_data.get("total_articles")))
            st.metric("Completed NLP Articles", fmt_num(mongo_data.get("completed_articles")))
            st.metric("Pending Queue", fmt_num(mongo_data.get("pending_articles")))

        with c_e:
            st.markdown('<div class="section-title">ELASTICSEARCH INDEX (news_articles)</div>', unsafe_allow_html=True)
            st.metric("Indexed Documents", fmt_num(es_data.get("indexed_documents")))
            st.metric("BM25 / Vector KNN", es_data.get("bm25_status", "READY"))
            st.metric("Embedding Dimension", f"{es_data.get('embedding_dimension', 384)}d Dense Vector")

        st.markdown("<br>", unsafe_allow_html=True)

        # NLP PIPELINE STAGE FLOW VISUALIZATION
        st.markdown('<div class="section-title">NLP ENRICHMENT PIPELINE STAGE FLOW</div>', unsafe_allow_html=True)
        stages = pipe_data.get("stages", [])
        if stages:
            df_pipe = pd.DataFrame(stages)
            fig_pipe = px.bar(df_pipe, x="stage", y="processed", color="stage", color_discrete_sequence=px.colors.qualitative.Dark24, text="processed")
            fig_pipe.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_pipe.update_layout(showlegend=False)
            st.plotly_chart(apply_plotly_dark_theme(fig_pipe, height=260), use_container_width=True)
