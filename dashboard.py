"""
=====================================================
News Intelligence Command Center — Enterprise Dashboard
Version : 18.0 (Real-Time News Intelligence & Current Affairs Center)
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
        <div style="font-size:10px; color:{COLORS['cyan']}; font-weight:700;">COMMAND CENTER</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

NAV_GROUPS = {
    "COMMAND CENTER": ["Top 10 & Command Center"],
    "NEWS INTELLIGENCE": ["NL Intelligence Search", "Live Feed & Date Explorer", "Monthly Intelligence"],
    "CROSS-SOURCE & COMPARISON": ["4-Newspaper Comparison", "Current Affairs & Developing"],
    "SEARCH & DEEP DIVES": ["Category, Keyword & Entity Deep-Dive", "Search Workspace"],
    "AI & SYSTEM": ["AI News Analyst (RAG)", "System Health"],
}
flat_pages = [p for group in NAV_GROUPS.values() for p in group]

for group_name, items in NAV_GROUPS.items():
    st.sidebar.caption(group_name)
    for item in items:
        pass

page = st.sidebar.radio("Navigate", flat_pages, label_visibility="collapsed")

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
# PAGE 1 — TOP 10 & COMMAND CENTER
# =====================================================
if page == "Top 10 & Command Center":
    render_header("REAL-TIME COMMAND CENTER", "Top 10 ranked stories right now, live news throughput, and telemetry alerts")

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

    # TOP 10 NEWS RIGHT NOW SECTION
    st.markdown('<div class="section-title">🔥 TOP 10 NEWS RIGHT NOW</div>', unsafe_allow_html=True)
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
# PAGE 2 — NL INTELLIGENCE SEARCH
# =====================================================
elif page == "NL Intelligence Search":
    render_header("FREE-TEXT & NATURAL LANGUAGE INTELLIGENCE SEARCH", "Ask about any topic, person, event, organization, or custom date range...")

    nl_query = st.text_input(
        "Enter your query in plain English:",
        placeholder="e.g. 'crime news from August 1 to August 7', 'top technology news this month', 'latest RBI updates'..."
    )

    b1, b2, b3, b4 = st.columns(4)
    if b1.button("top 10 news today"):
        nl_query = "top 10 news today"
    if b2.button("crime news this week"):
        nl_query = "crime news this week"
    if b3.button("compare all four newspapers on economy"):
        nl_query = "compare all four newspapers on economy"
    if b4.button("developing stories right now"):
        nl_query = "developing stories right now"

    if nl_query.strip():
        with st.spinner("Parsing intent & querying corpus..."):
            nl_res, nl_ok = post_api("/api/news/nl-search", {"query": nl_query.strip()})

        if not nl_ok:
            render_unavailable_box("Natural Language Intelligence Search")
        else:
            parsed = nl_res.get("parsed", {})
            results = nl_res.get("results", {})

            st.markdown(f"""
                <div class="trace-box" style="margin-bottom:14px;">
                    Intent Detected  : <b>{parsed.get('intent','ARTICLE_SEARCH')}</b><br>
                    Parsed Filters   : Source={parsed.get('filters',{}).get('source') or 'Any'} | Category={parsed.get('filters',{}).get('category') or 'Any'} | Time={parsed.get('filters',{}).get('time_window')} | Range=({parsed.get('filters',{}).get('start_date')} to {parsed.get('filters',{}).get('end_date')})<br>
                    Executed Tools   : {', '.join(parsed.get('tools',[]))}
                </div>
            """, unsafe_allow_html=True)

            articles = first_present(results, ["articles", "results"], []) or []
            if isinstance(results, dict) and "developing_stories" in results:
                st.markdown("#### Developing Stories Results")
                for dev in results["developing_stories"]:
                    st.markdown(f"• **{dev.get('story_topic')}** [{dev.get('status')}] — {dev.get('update_count')} updates across {len(dev.get('sources_involved',[]))} sources")
            elif isinstance(results, dict) and "publishers" in results:
                st.markdown("#### 4-Newspaper Comparison Results")
                for pub, p_data in results["publishers"].items():
                    st.info(f"**{pub}**: {p_data.get('data_derived_coverage_theme')}")
            elif articles:
                st.caption(f"Retrieved **{len(articles)}** matching documents")
                for a in articles:
                    sent = a.get("sentiment") or "Neutral"
                    sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
                    st.markdown(f"""
                        <div class="card-box">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span class="badge badge-cyan">{a.get('source','Unknown')}</span>
                                    <span class="badge badge-purple" style="margin-left:4px;">{a.get('category','General')}</span>
                                </div>
                                <span class="badge {sent_cls}">{sent}</span>
                            </div>
                            <div style="font-size:14.5px; font-weight:700; margin:6px 0;">
                                <a href="{a.get('link','#')}" target="_blank" style="color:{COLORS['cyan']}; text-decoration:none;">{a.get('headline', a.get('title','Untitled'))}</a>
                            </div>
                            <div style="font-size:12.5px; color:{COLORS['muted']};">{a.get('summary','No summary available.')}</div>
                        </div>
                    """, unsafe_allow_html=True)


# =====================================================
# PAGE 3 — LIVE FEED & DATE EXPLORER
# =====================================================
elif page == "Live Feed & Date Explorer":
    render_header("DATE-WISE NEWS EXPLORER & LIVE FEED", "Filter news by preset date ranges or pick custom dates (e.g. Aug 1 → Aug 7)")

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        date_preset = st.selectbox("Date Selector", ["Today", "Yesterday", "Last 7 Days", "Last 30 Days", "This Month", "Custom Date Range"])
    with d_col2:
        sel_source = st.selectbox("Filter Source", ["All Sources", "Economic Times", "The Hindu", "Indian Express", "Hindustan Times"])
    with d_col3:
        sel_cat = st.selectbox("Filter Category", ["All Categories"] + DEFAULT_CATEGORIES)
    with d_col4:
        sel_sent = st.selectbox("Filter Sentiment", ["All Sentiments", "Positive", "Neutral", "Negative"])

    now_date = datetime.now()
    start_d, end_d = None, None

    if date_preset == "Today":
        start_d = now_date.strftime("%Y-%m-%d")
        end_d = now_date.strftime("%Y-%m-%d")
    elif date_preset == "Yesterday":
        yest = now_date - timedelta(days=1)
        start_d = yest.strftime("%Y-%m-%d")
        end_d = yest.strftime("%Y-%m-%d")
    elif date_preset == "Last 7 Days":
        start_d = (now_date - timedelta(days=7)).strftime("%Y-%m-%d")
        end_d = now_date.strftime("%Y-%m-%d")
    elif date_preset == "Last 30 Days":
        start_d = (now_date - timedelta(days=30)).strftime("%Y-%m-%d")
        end_d = now_date.strftime("%Y-%m-%d")
    elif date_preset == "This Month":
        start_d = now_date.replace(day=1).strftime("%Y-%m-%d")
        end_d = now_date.strftime("%Y-%m-%d")
    elif date_preset == "Custom Date Range":
        c_start, c_end = st.columns(2)
        with c_start:
            custom_start = st.date_input("Start Date", value=now_date - timedelta(days=7))
            start_d = custom_start.strftime("%Y-%m-%d")
        with c_end:
            custom_end = st.date_input("End Date", value=now_date)
            end_d = custom_end.strftime("%Y-%m-%d")

    ex_params = {}
    if start_d:
        ex_params["start_date"] = start_d
    if end_d:
        ex_params["end_date"] = end_d
    if sel_source != "All Sources":
        ex_params["source"] = sel_source
    if sel_cat != "All Categories":
        ex_params["category"] = sel_cat
    if sel_sent != "All Sentiments":
        ex_params["sentiment"] = sel_sent

    exp_res, exp_ok = fetch_api("/api/news/explorer", params=ex_params)
    if not exp_ok:
        render_unavailable_box("Date Explorer")
    else:
        st.markdown(f"#### Period Summary ({exp_res.get('start_date')} to {exp_res.get('end_date')}) — **{exp_res.get('total_articles',0)}** Articles")
        
        articles = exp_res.get("articles", [])
        if not articles:
            render_empty_box("No articles indexed for this date selection.")
        else:
            for a in articles:
                sent = a.get("sentiment") or "Neutral"
                sent_cls = "badge-green" if sent == "Positive" else ("badge-red" if sent == "Negative" else "badge-muted")
                with st.expander(f"[{a.get('source','Unknown')}] {a.get('title','Untitled')}"):
                    st.markdown(f"**Category:** `{a.get('category','--')}` &nbsp;|&nbsp; **Sentiment:** <span class='badge {sent_cls}'>{sent}</span> &nbsp;|&nbsp; **Published:** {time_ago(a.get('published_date'))}", unsafe_allow_html=True)
                    st.write(a.get("summary") or "No summary available.")
                    if a.get("link") and a.get("link") != "#":
                        st.markdown(f"[Open Original Article Link →]({a.get('link')})")


# =====================================================
# PAGE 4 — MONTHLY INTELLIGENCE
# =====================================================
elif page == "Monthly Intelligence":
    render_header("MONTHLY NEWS INTELLIGENCE", "Monthly archive timelines, top stories, and emerging category trends")

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        sel_year = st.selectbox("Select Year", [2026, 2025])
    with m_col2:
        sel_month = st.selectbox("Select Month", ["August", "July", "June", "May", "April", "March", "February", "January"])
    
    month_num_map = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8}
    m_num = month_num_map[sel_month]

    m_res, m_ok = fetch_api("/api/news/monthly", params={"year": sel_year, "month": m_num})
    if not m_ok:
        render_unavailable_box("Monthly News Intelligence")
    else:
        st.markdown(f"### {m_res.get('month_name','Monthly Report')} Overview")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Monthly News", fmt_num(m_res.get("total_articles")))
        c2.metric("Most Active Category", m_res.get("most_active_category","--"))
        c3.metric("Top Emerging Keyword", m_res.get("most_emerging_keyword","--"))

        st.markdown("---")
        st.markdown("#### Top Stories of the Month")
        for s in m_res.get("top_stories", []):
            st.markdown(f"""
                <div class="card-box">
                    <div style="font-weight:700; font-size:14px; color:{COLORS['cyan']};">[{s.get('date')}] {s.get('title')}</div>
                    <div style="font-size:11.5px; color:{COLORS['muted']}; margin:3px 0;">Source: {s.get('source')} · Category: {s.get('category')}</div>
                    <div style="font-size:12.5px;">{s.get('summary')}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Monthly Timeline Breakdown")
        t_df = pd.DataFrame(m_res.get("monthly_timeline", []))
        if not t_df.empty:
            st.dataframe(t_df, use_container_width=True, hide_index=True)


# =====================================================
# PAGE 5 — 4-NEWSPAPER COMPARISON
# =====================================================
elif page == "4-Newspaper Comparison":
    render_header("4-NEWSPAPER TOPIC COMPARISON", "Compare coverage of the SAME topic across Economic Times, The Hindu, Indian Express & Hindustan Times")

    topic_query = st.text_input("Enter Topic to Compare", value="India economy", placeholder="e.g. India economy, RBI, elections...")

    if topic_query.strip():
        comp_res, comp_ok = fetch_api("/api/news/compare-publishers", params={"topic": topic_query.strip()})
        if not comp_ok:
            render_unavailable_box("4-Newspaper Comparison")
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
                            if art.get("link") and art.get("link") != "#":
                                st.markdown(f"[Open Link →]({art.get('link')})")

            st.markdown("---")
            st.markdown(f"**Cross-Publisher Signal Summary:** {comp_res.get('cross_source_summary')}")


# =====================================================
# PAGE 6 — CURRENT AFFAIRS & DEVELOPING
# =====================================================
elif page == "Current Affairs & Developing":
    render_header("CURRENT AFFAIRS & DEVELOPING STORIES", "Track ongoing developing news, story timelines, and 'What Happened Next?'")

    t_ca, t_dev, t_time = st.tabs(["Current Affairs Center", "Developing Stories Tracker", "Story Evolution Timeline"])

    with t_ca:
        st.markdown("#### Current Affairs Center (Major Domains)")
        ca_cat = st.selectbox("Select Domain", ["Breaking Now", "Top Developments", "National", "International", "Business", "Technology", "Sports", "Science", "Market"])
        ca_res, ca_ok = fetch_api("/api/live-feed", params={"limit": 10})
        if ca_ok:
            for a in (ca_res.get("articles", []) or [])[:6]:
                st.markdown(f"""
                    <div class="card-box">
                        <div style="font-weight:700; color:#FFFFFF;">[{a.get('source')}] {a.get('title')}</div>
                        <div style="font-size:12px; color:{COLORS['muted']}; margin-top:4px;">{a.get('summary')}</div>
                    </div>
                """, unsafe_allow_html=True)

    with t_dev:
        st.markdown("#### Developing Stories Tracker")
        dev_res, dev_ok = fetch_api("/api/news/developing")
        if not dev_ok:
            render_unavailable_box("Developing Stories Tracker")
        else:
            dev_stories = dev_res.get("developing_stories", [])
            for dev in dev_stories:
                st.markdown(f"""
                    <div class="card-box" style="border-left:4px solid {COLORS['orange']};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; font-size:14px; color:#FFFFFF;">{dev.get('story_topic')}</span>
                            <span class="badge badge-orange">{dev.get('status')}</span>
                        </div>
                        <div style="font-size:12px; color:{COLORS['muted']}; margin-top:6px;">
                            Latest Headline: <b>{dev.get('latest_headline')}</b><br>
                            Updates Count: <b>{dev.get('update_count')}</b> · Sources: {', '.join(dev.get('sources_involved',[]))}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with t_time:
        st.markdown("#### Story Evolution Timeline ('What Happened Next?')")
        t_topic = st.text_input("Enter Topic or Event for Timeline", value="Market")
        time_res, time_ok = fetch_api("/api/news/timeline", params={"topic": t_topic})
        if time_ok:
            events = time_res.get("timeline", [])
            if not events:
                render_empty_box("No verified follow-up coverage found in the indexed data.")
            else:
                for ev in events:
                    st.markdown(f"""
                        <div class="card-box" style="border-left:4px solid {COLORS['cyan']};">
                            <span class="badge badge-cyan">{ev.get('stage_label')}</span>
                            <span style="font-size:11px; color:{COLORS['muted']}; margin-left:8px;">{time_ago(ev.get('timestamp'))}</span>
                            <div style="font-weight:700; font-size:14px; margin-top:6px;">[{ev.get('source')}] {ev.get('headline')}</div>
                            <div style="font-size:12.5px; color:{COLORS['muted']}; margin-top:4px;">{ev.get('summary')}</div>
                        </div>
                    """, unsafe_allow_html=True)


# =====================================================
# PAGE 7 — CATEGORY, KEYWORD & ENTITY DEEP-DIVE
# =====================================================
elif page == "Category, Keyword & Entity Deep-Dive":
    render_header("CATEGORY, KEYWORD & ENTITY DEEP-DIVE", "Type any custom term, person, company, place, or domain for instant intelligence analytics...")

    custom_term = st.text_input("Search any Keyword, Entity, or Category:", value="RBI", placeholder="e.g. RBI, Modi, stock market, cyber crime, IPL...")

    if custom_term.strip():
        k_res, k_ok = fetch_api("/api/news/keyword-intelligence", params={"q": custom_term.strip()})
        if k_ok and k_res:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Mentions", fmt_num(k_res.get("total_mentions")))
            c2.metric("First Appearance", time_ago(k_res.get("first_appearance")))
            c3.metric("Latest Appearance", time_ago(k_res.get("latest_appearance")))

            st.markdown("---")
            st.markdown("#### Sample Articles Mentioning Term")
            for sa in k_res.get("sample_articles", []):
                st.markdown(f"""
                    <div class="card-box">
                        <div style="font-weight:700; color:{COLORS['cyan']};">[{sa.get('source')}] {sa.get('headline')}</div>
                        <div style="font-size:12px; color:{COLORS['muted']}; margin-top:4px;">{sa.get('summary')}</div>
                    </div>
                """, unsafe_allow_html=True)


# =====================================================
# PAGE 8 — SEARCH WORKSPACE
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
                search_cat = st.selectbox("Category Filter", ["All"] + DEFAULT_CATEGORIES, key=f"cat_{mode}")
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
# PAGE 9 — AI ANALYST (RAG)
# =====================================================
elif page == "AI News Analyst (RAG)":
    render_header("AI NEWS ANALYST", "Grounded Agentic RAG assistant with intent routing and citation provenance")

    st.info("💡 **Analytics Logic Context:** The AI Analyst classifies user intent, queries Elasticsearch vector & BM25 indices deterministically, synthesizes a grounded answer, and lists exact article citations to prevent AI hallucinations.")

    b1, b2, b3, b4 = st.columns(4)
    user_q = st.session_state.get("ai_q", "")
    if b1.button("What are the top 10 news stories today?"):
        user_q = "What are the top 10 news stories today?"
    if b2.button("Compare all 4 newspapers on India's economy"):
        user_q = "Compare all 4 newspapers on India's economy"
    if b3.button("What stories are currently developing?"):
        user_q = "What stories are currently developing?"
    if b4.button("Show me crime news from August 1 to August 7"):
        user_q = "Show me crime news from August 1 to August 7"

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
                st.warning("Insufficient evidence was found in the indexed corpus to answer this question.")

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
# PAGE 10 — SYSTEM HEALTH
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
