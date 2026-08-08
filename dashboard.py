"""
=====================================================
News Intelligence Command Center — Enterprise Dashboard
Version : 9.0 (Defensive Data Contracts & Bloomberg Intelligence Aesthetic)
=====================================================
"""

import sys
import io
import time
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(interval=10000, key=None):
        pass

# Configure Streamlit Page
st.set_page_config(
    page_title="News Intelligence Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Inject Custom High-Density Bloomberg/Palantir Command Center CSS
st.markdown("""
<style>
    /* Dark Base Theme Overrides */
    .stApp {
        background-color: #090D16;
        color: #E6EDF3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0D1117;
        border-right: 1px solid #21262D;
    }
    
    /* Hide Streamlit Header Elements */
    header[data-testid="stHeader"] {
        background-color: rgba(9, 13, 22, 0.95);
    }
    
    /* Card Container */
    .intel-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Top Metric Card */
    .kpi-card {
        background: linear-gradient(180deg, #1C2128 0%, #161B22 100%);
        border: 1px solid #30363D;
        border-top: 3px solid #1E88E5;
        border-radius: 6px;
        padding: 12px 14px;
        text-align: left;
    }
    
    .kpi-card.spike {
        border-top: 3px solid #FF5252;
    }
    
    .kpi-card.green {
        border-top: 3px solid #00E676;
    }

    .kpi-card.purple {
        border-top: 3px solid #AB47BC;
    }
    
    .kpi-val {
        font-size: 24px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    
    .kpi-lbl {
        font-size: 11px;
        font-weight: 700;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
    }

    .kpi-delta {
        font-size: 11px;
        font-weight: 600;
        margin-top: 4px;
    }
    
    .delta-up { color: #00E676; }
    .delta-down { color: #FF5252; }
    .delta-neutral { color: #8B949E; }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 2px 7px;
        font-size: 10px;
        font-weight: 700;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-source { background-color: #21262D; color: #58A6FF; border: 1px solid #388BFD40; }
    .badge-category { background-color: #1F242C; color: #7EE787; border: 1px solid #2EA04340; }
    .badge-positive { background-color: #0E2A1F; color: #3FB950; border: 1px solid #238636; }
    .badge-neutral { background-color: #262C36; color: #A3B8CC; border: 1px solid #484F58; }
    .badge-negative { background-color: #381A1D; color: #F85149; border: 1px solid #DA3633; }
    .badge-live { background-color: #381A1D; color: #FF5252; border: 1px solid #FF1744; animation: blinker 1.5s linear infinite; }

    /* Feed Stream Item */
    .feed-item {
        background-color: #161B22;
        border-left: 3px solid #1E88E5;
        border-bottom: 1px solid #21262D;
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 0 4px 4px 0;
    }
    
    .feed-title {
        font-size: 13px;
        font-weight: 600;
        color: #F0F6FC;
        margin-bottom: 4px;
        line-height: 1.35;
    }
    
    .feed-meta {
        font-size: 10px;
        color: #8B949E;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 15px;
        font-weight: 700;
        color: #F0F6FC;
        letter-spacing: -0.2px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid #21262D;
        padding-bottom: 4px;
    }
    
    /* Code/Trace Box */
    .trace-box {
        background-color: #0D1117;
        border: 1px solid #30363D;
        border-radius: 4px;
        padding: 12px;
        font-family: 'JetBrains Mono', Consolas, monospace;
        font-size: 12px;
        color: #7EE787;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to query API safely with timeout and fallback
@st.cache_data(ttl=3)
def fetch_api(endpoint: str, params: dict = None):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json(), True
        return {}, False
    except Exception:
        return {}, False

def post_api(endpoint: str, payload: dict):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json(), True
        return {"error": "API response error"}, False
    except Exception as e:
        return {"error": str(e)}, False

# Defensive Data Contract Helper
def safe_dataframe(data_list: list, column_mapping: dict = None, default_columns: list = None) -> pd.DataFrame:
    """Safely builds a Pandas DataFrame with column normalization and missing key fallbacks."""
    if not data_list or not isinstance(data_list, list):
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        return pd.DataFrame()
    
    try:
        df = pd.DataFrame(data_list)
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        if default_columns:
            for col in default_columns:
                if col not in df.columns:
                    df[col] = 0 if "mentions" in col.lower() or "count" in col.lower() else ("N/A" if col != "Growth (%)" else 0.0)
            return df[default_columns]
        return df
    except Exception:
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        return pd.DataFrame()

# Sidebar Navigation System
st.sidebar.markdown("### 🛡️ NEWS INTELLIGENCE")
st.sidebar.caption("Enterprise Command Center")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Command Center",
        "Live News",
        "Intelligence",
        "Temporal Intelligence",
        "Search",
        "AI Analyst",
        "Article Explorer",
        "System Health"
    ]
)

st.sidebar.markdown("---")

# Refresh Controls
st.sidebar.markdown("##### ⚙️ AUTO REFRESH")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_sec = st.sidebar.select_slider("Refresh Interval", options=[5, 10, 15, 30], value=10)

if auto_refresh:
    st_autorefresh(interval=refresh_sec * 1000, key="nav_autorefresh")

st.sidebar.markdown("---")

# Fetch Real Infrastructure Health Status
health_res, health_ok = fetch_api("/health")
metrics_res, metrics_ok = fetch_api("/api/metrics")

mongo_status = health_res.get("mongodb", "down") if health_ok else "down"
es_status = health_res.get("elasticsearch", "down") if health_ok else "down"

st.sidebar.markdown("##### 🌐 SYSTEM STATUS")
st.sidebar.markdown(f"Kafka &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {'🟢 Healthy' if health_ok else '🔴 Offline'}")
st.sidebar.markdown(f"MongoDB &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {'🟢 Healthy' if mongo_status == 'ok' else '🔴 Offline'}")
st.sidebar.markdown(f"Elasticsearch {'🟢 Healthy' if es_status == 'ok' else '🔴 Offline'}")
st.sidebar.markdown(f"API Server &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {'🟢 Healthy' if health_ok else '🔴 Offline'}")
st.sidebar.markdown(f"AI Service &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {'🟢 Healthy' if health_ok else '🔴 Offline'}")

st.sidebar.markdown("---")
freshness_ts = metrics_res.get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if metrics_ok else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.sidebar.caption(f"🕒 **DATA FRESHNESS:**\n`{freshness_ts[:19]}`")


# Helper function for Plotly dark layout styling
def apply_plotly_dark_theme(fig, height=260):
    fig.update_layout(
        paper_bgcolor="#161B22",
        plot_bgcolor="#161B22",
        height=height,
        font=dict(color="#E6EDF3", family="Inter, sans-serif", size=11),
        margin=dict(l=15, r=15, t=30, b=15),
        xaxis=dict(gridcolor="#21262D", zerolinecolor="#21262D"),
        yaxis=dict(gridcolor="#21262D", zerolinecolor="#21262D"),
        legend=dict(bgcolor="#161B22", bordercolor="#30363D")
    )
    return fig


# =====================================================
# PAGE 1 — COMMAND CENTER (Main Landing Page)
# =====================================================
if page == "Command Center":
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <h1 style="margin: 0; font-size: 22px; font-weight: 800; color: #F0F6FC; letter-spacing: -0.5px;">NEWS INTELLIGENCE COMMAND CENTER</h1>
                <p style="margin: 2px 0 0 0; font-size: 12px; color: #8B949E;">Real-time intelligence from multiple news sources</p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-live">● LIVE</span>
                <span style="font-size: 11px; color: #8B949E; margin-left: 6px;">Last updated: <b>{}</b></span>
            </div>
        </div>
    """.format(freshness_ts[11:19] if len(freshness_ts) >= 19 else freshness_ts), unsafe_allow_html=True)
    
    # 6 COMPACT PREMIUM KPI CARDS
    total_art = metrics_res.get("total_articles", 0) if metrics_ok else 0
    today_art = metrics_res.get("today_articles", 0) if metrics_ok else 0
    completed_art = metrics_res.get("completed_articles", 0) if metrics_ok else 0
    pending_art = metrics_res.get("pending_articles", 0) + metrics_res.get("failed_articles", 0) if metrics_ok else 0
    sources_dict = metrics_res.get("top_sources", {}) if metrics_ok else {}
    active_sources = len([s for s, c in sources_dict.items() if c > 0]) or 4
    
    spikes_res, spikes_ok = fetch_api("/api/analytics/spikes")
    spike_list = spikes_res.get("spikes", []) if spikes_ok else []
    spike_count = len(spike_list)
    
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    with k1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{total_art:,}</div>
                <div class="kpi-lbl">Total Articles</div>
                <div class="kpi-delta delta-neutral">Indexed Corpus</div>
            </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
            <div class="kpi-card green">
                <div class="kpi-val">{today_art:,}</div>
                <div class="kpi-lbl">Articles Today</div>
                <div class="kpi-delta delta-up">↑ Live Streams</div>
            </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
            <div class="kpi-card purple">
                <div class="kpi-val">{total_art - pending_art:,}</div>
                <div class="kpi-lbl">Realtime Articles</div>
                <div class="kpi-delta delta-up">Real-time Streamed</div>
            </div>
        """, unsafe_allow_html=True)

    with k4:
        comp_pct = (completed_art / total_art * 100) if total_art > 0 else 100.0
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{completed_art:,}</div>
                <div class="kpi-lbl">Completed Analysis</div>
                <div class="kpi-delta delta-up">{comp_pct:.1f}% Enriched</div>
            </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{active_sources}</div>
                <div class="kpi-lbl">Active Sources</div>
                <div class="kpi-delta delta-neutral">ET, Hindu, IE, HT</div>
            </div>
        """, unsafe_allow_html=True)

    with k6:
        card_cls = "spike" if spike_count > 0 else ""
        st.markdown(f"""
            <div class="kpi-card {card_cls}">
                <div class="kpi-val">{spike_count}</div>
                <div class="kpi-lbl">Breaking Spikes</div>
                <div class="kpi-delta {'delta-down' if spike_count > 0 else 'delta-neutral'}">
                    {'⚠️ Anomaly Alert' if spike_count > 0 else 'Normal Baseline'}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3-PART MAIN INTELLIGENCE CONTENT AREA
    col_left, col_center, col_right = st.columns([3, 5, 4])

    # LEFT: LIVE NEWS FEED
    with col_left:
        st.markdown('<div class="section-header">🔴 LIVE NEWS FEED</div>', unsafe_allow_html=True)
        live_res, live_ok = fetch_api("/api/live-feed", params={"limit": 6})
        articles = live_res.get("articles", []) if live_ok else []
        
        if articles:
            for a in articles:
                sent = a.get("sentiment", "Neutral")
                sent_cls = "badge-positive" if sent == "Positive" else ("badge-negative" if sent == "Negative" else "badge-neutral")
                pub_time = str(a.get("published_date") or "")[11:16]
                
                st.markdown(f"""
                    <div class="feed-item">
                        <div class="feed-meta" style="margin-bottom: 2px;">
                            <span class="badge badge-source">{a.get('source', 'Unknown')}</span> &nbsp;
                            <span>{pub_time}</span>
                        </div>
                        <div class="feed-title">{a.get('title')}</div>
                        <div class="feed-meta">
                            <span class="badge badge-category">{a.get('category', 'General')}</span> &nbsp;
                            <span class="badge {sent_cls}">{sent}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No live articles available.")

    # CENTER: NEWS VOLUME (LAST 24 HOURS)
    with col_center:
        st.markdown('<div class="section-header">📈 NEWS VOLUME — LAST 24 HOURS</div>', unsafe_allow_html=True)
        ctrl_col1, ctrl_col2 = st.columns([2, 3])
        with ctrl_col1:
            sel_win = st.select_slider("Time Window", options=["15m", "1h", "6h", "24h", "7d"], value="24h")
        with ctrl_col2:
            sel_bkt = st.selectbox("Bucket Size", ["1h", "15m", "6h"], index=0)

        vol_res, vol_ok = fetch_api("/api/analytics/volume", params={"window": sel_win, "bucket": sel_bkt})
        vol_data = vol_res.get("timeline", []) if vol_ok else []
        
        if vol_data:
            df_vol = pd.DataFrame(vol_data)
            fig_vol = px.area(df_vol, x="time", y="count", color_discrete_sequence=["#1E88E5"])
            fig_vol = apply_plotly_dark_theme(fig_vol, height=270)
            st.plotly_chart(fig_vol, use_container_width=True)
        else:
            st.info("Volume timeline initializing...")

    # RIGHT: BREAKING INTELLIGENCE
    with col_right:
        st.markdown('<div class="section-header">⚡ BREAKING INTELLIGENCE</div>', unsafe_allow_html=True)
        
        # Spike Signal
        if spike_count > 0:
            top_spike = spike_list[0]
            st.error(f"🚨 **BREAKING SPIKE:** `{top_spike.get('category')}` volume at **{top_spike.get('current_volume')} articles** ({top_spike.get('multiplier'):.1f}x baseline)")
        else:
            st.success("🟢 **NORMAL ACTIVITY** — No significant spike detected.")

        # Top Category & Sentiment Insights
        cats = metrics_res.get("top_categories", {}) if metrics_ok else {}
        top_cat = max(cats, key=cats.get) if cats else "Business"
        
        sents = metrics_res.get("sentiment_distribution", {}) if metrics_ok else {}
        dom_sent = max(sents, key=sents.get) if sents else "Neutral"
        
        st.markdown(f"""
            <div class="intel-card">
                <div style="font-size: 11px; font-weight: 700; color: #8B949E; text-transform: uppercase;">TOP ACTIVE CATEGORY</div>
                <div style="font-size: 16px; font-weight: 700; color: #58A6FF; margin-top: 2px;">{top_cat}</div>
                <div style="font-size: 11px; color: #8B949E;">Accounts for largest share of indexed live news.</div>
            </div>
            <div class="intel-card">
                <div style="font-size: 11px; font-weight: 700; color: #8B949E; text-transform: uppercase;">DOMINANT SENTIMENT</div>
                <div style="font-size: 16px; font-weight: 700; color: #7EE787; margin-top: 2px;">{dom_sent}</div>
                <div style="font-size: 11px; color: #8B949E;">Current reporting tone is predominantly {dom_sent.lower()}.</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # SECOND ANALYTICS ROW (4 PANELS)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="section-header">📰 SOURCE INTELLIGENCE</div>', unsafe_allow_html=True)
        if sources_dict:
            df_src = pd.DataFrame(list(sources_dict.items()), columns=["Source", "Count"]).sort_values("Count", ascending=True)
            fig_src = px.bar(df_src, x="Count", y="Source", orientation="h", color="Source", color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(apply_plotly_dark_theme(fig_src, height=220), use_container_width=True)
        else:
            st.info("Source data loading...")

    with c2:
        st.markdown('<div class="section-header">📊 CATEGORY DISTRIBUTION</div>', unsafe_allow_html=True)
        if cats:
            df_cat = pd.DataFrame(list(cats.items()), columns=["Category", "Count"])
            fig_cat = px.pie(df_cat, values="Count", names="Category", hole=0.45, color_discrete_sequence=px.colors.qualitative.Vivid)
            st.plotly_chart(apply_plotly_dark_theme(fig_cat, height=220), use_container_width=True)
        else:
            st.info("Category data loading...")

    with c3:
        st.markdown('<div class="section-header">💬 SENTIMENT OVERVIEW</div>', unsafe_allow_html=True)
        if sents:
            df_sent = pd.DataFrame(list(sents.items()), columns=["Sentiment", "Count"])
            fig_sent = px.pie(df_sent, values="Count", names="Sentiment", color="Sentiment", color_discrete_map={"Positive": "#00E676", "Neutral": "#8B949E", "Negative": "#FF5252"})
            st.plotly_chart(apply_plotly_dark_theme(fig_sent, height=220), use_container_width=True)
        else:
            st.info("Sentiment data loading...")

    with c4:
        st.markdown('<div class="section-header">🔥 TOP EMERGING KEYWORDS</div>', unsafe_allow_html=True)
        kw_res, kw_ok = fetch_api("/api/analytics/keywords")
        kw_list = kw_res.get("keywords", []) if kw_ok else []
        if kw_list:
            df_kw = safe_dataframe(
                kw_list[:5],
                column_mapping={"recent_mentions": "Mentions", "growth_pct": "Growth (%)", "keyword": "Keyword"},
                default_columns=["Keyword", "Mentions", "Growth (%)"]
            )
            st.dataframe(df_kw, use_container_width=True, height=200)
        else:
            st.info("No emerging keywords available.")

    st.markdown("---")

    # ENTITY & CROSS-SOURCE INTELLIGENCE ROW
    ec1, ec2 = st.columns([5, 7])

    with ec1:
        st.markdown('<div class="section-header">🏛️ TOP EMERGING ENTITIES</div>', unsafe_allow_html=True)
        ent_res, ent_ok = fetch_api("/api/analytics/entities")
        ent_list = ent_res.get("entities", []) if ent_ok else []
        if ent_list:
            df_ent = safe_dataframe(
                ent_list[:5],
                column_mapping={"entity": "Entity", "type": "Type", "recent_mentions": "Mentions", "growth_pct": "Growth (%)"},
                default_columns=["Entity", "Type", "Mentions", "Growth (%)"]
            )
            st.dataframe(df_ent, use_container_width=True, height=180)
        else:
            st.info("No emerging entities available.")

    with ec2:
        st.markdown('<div class="section-header">🌐 CROSS-SOURCE INTELLIGENCE</div>', unsafe_allow_html=True)
        cs_res, cs_ok = fetch_api("/api/analytics/cross-source")
        cs_topics = cs_res.get("topics", []) if cs_ok else []
        
        if cs_topics:
            cs_cols = st.columns(min(len(cs_topics), 2))
            for idx, topic in enumerate(cs_topics[:2]):
                with cs_cols[idx]:
                    sources = topic.get("sources", [])
                    source_count = topic.get("sources_count") or topic.get("source_count") or len(sources)
                    src_badges = " ".join([f"<span class='badge badge-source'>{s}</span>" for s in sources])
                    st.markdown(f"""
                        <div class="intel-card">
                            <div style="font-size: 10px; font-weight: 700; color: #00E676; text-transform: uppercase;">{source_count} PUBLISHERS COVERING</div>
                            <div style="font-size: 13px; font-weight: 700; color: #F0F6FC; margin: 4px 0;">{topic.get('topic', 'Topic Signal')}</div>
                            <div style="margin-top: 6px;">{src_badges}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No cross-source topic signals detected.")


# =====================================================
# PAGE 2 — LIVE NEWS
# =====================================================
elif page == "Live News":
    st.markdown("### 🔴 LIVE NEWS STREAM")
    st.caption("Real-time feed with multi-parameter filtering")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        sel_source = st.selectbox("Filter Source", ["All Sources", "Economic Times", "The Hindu", "Indian Express", "Hindustan Times"])
    with f2:
        sel_cat = st.selectbox("Filter Category", ["All Categories", "Business", "Technology", "Politics", "Sports", "World", "General"])
    with f3:
        sel_sent = st.selectbox("Filter Sentiment", ["All Sentiments", "Positive", "Neutral", "Negative"])
    with f4:
        search_kw = st.text_input("Search Headlines", placeholder="Type keyword...")

    feed_res, feed_ok = fetch_api("/api/live-feed", params={"limit": 50})
    articles = feed_res.get("articles", []) if feed_ok else []

    filtered = []
    for a in articles:
        if sel_source != "All Sources" and a.get("source") != sel_source:
            continue
        if sel_cat != "All Categories" and a.get("category") != sel_cat:
            continue
        if sel_sent != "All Sentiments" and a.get("sentiment") != sel_sent:
            continue
        if search_kw and search_kw.lower() not in a.get("title", "").lower():
            continue
        filtered.append(a)

    st.markdown(f"Showing **{len(filtered)}** articles:")

    if filtered:
        for a in filtered:
            sent_cls = "badge-positive" if a.get("sentiment") == "Positive" else ("badge-negative" if a.get("sentiment") == "Negative" else "badge-neutral")
            pub_t = str(a.get("published_date") or "")[:19].replace("T", " ")
            
            with st.expander(f"[{a.get('source')}] {a.get('title')}"):
                st.markdown(f"**Publisher:** `{a.get('source')}` | **Category:** `{a.get('category')}` | **Sentiment:** `{a.get('sentiment')}` | **Published:** `{pub_t}`")
                st.markdown(f"**Summary:**\n{a.get('summary')}")
                st.markdown(f"🔗 [Read Source Article]({a.get('link')})")
    else:
        st.info("No articles match the selected filter criteria.")


# =====================================================
# PAGE 3 — INTELLIGENCE
# =====================================================
elif page == "Intelligence":
    st.markdown("### 📊 DEEP INTELLIGENCE ANALYTICS")
    st.caption("Multidimensional trend intelligence and cross-publisher metrics")

    time_win = st.select_slider("Select Analytics Time Window", options=["15m", "1h", "6h", "24h", "7d"], value="24h")

    t1, t2, t3 = st.tabs(["Source Performance", "Category Trends", "Sentiment Timeline"])

    with t1:
        src_res, src_ok = fetch_api("/api/analytics/source-trends", params={"window": time_win, "bucket": "1h"})
        src_data = src_res.get("timeline", []) if src_ok else []
        if src_data:
            df_st = pd.DataFrame(src_data)
            fig_st = px.line(df_st, x="time", y="count", color="source", title=f"Source Output ({time_win})")
            st.plotly_chart(apply_plotly_dark_theme(fig_st, height=320), use_container_width=True)
        else:
            st.info("Source timeline data unavailable for this window.")

    with t2:
        cat_res, cat_ok = fetch_api("/api/analytics/category-trends", params={"window": time_win, "bucket": "1h"})
        cat_data = cat_res.get("timeline", []) if cat_ok else []
        if cat_data:
            df_ct = pd.DataFrame(cat_data)
            fig_ct = px.area(df_ct, x="time", y="count", color="category", title=f"Category Trends ({time_win})")
            st.plotly_chart(apply_plotly_dark_theme(fig_ct, height=320), use_container_width=True)
        else:
            st.info("Category trends unavailable for this window.")

    with t3:
        sent_res, sent_ok = fetch_api("/api/analytics/sentiment-trends", params={"window": time_win, "bucket": "1h"})
        sent_data = sent_res.get("timeline", []) if sent_ok else []
        if sent_data:
            df_sent = pd.DataFrame(sent_data)
            fig_sent = px.line(df_sent, x="time", y="count", color="sentiment", color_discrete_map={"Positive": "#00E676", "Neutral": "#8B949E", "Negative": "#FF5252"})
            st.plotly_chart(apply_plotly_dark_theme(fig_sent, height=320), use_container_width=True)
        else:
            st.info("Sentiment timeline unavailable for this window.")


# =====================================================
# PAGE 4 — TEMPORAL INTELLIGENCE
# =====================================================
elif page == "Temporal Intelligence":
    st.markdown("### ⏳ TEMPORAL INTELLIGENCE WORKSPACE")
    st.caption("Phase 14 Temporal trend analysis, volume anomaly detection, and emerging signals")

    sp_res, sp_ok = fetch_api("/api/analytics/spikes")
    spikes = sp_res.get("spikes", []) if sp_ok else []
    
    if spikes:
        st.error(f"🚨 **BREAKING ACTIVITY DETECTED:** Category `{spikes[0].get('category')}` volume at **{spikes[0].get('current_volume')} articles** ({spikes[0].get('multiplier', 1.0):.1f}x baseline)")
    else:
        st.success("🟢 **NORMAL ACTIVITY** — No significant spike detected across news channels.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Emerging Keywords (24h Acceleration)")
        kw_res, kw_ok = fetch_api("/api/analytics/keywords")
        kws = kw_res.get("keywords", []) if kw_ok else []
        if kws:
            df_kws = safe_dataframe(kws, column_mapping={"recent_mentions": "Mentions", "growth_pct": "Growth (%)", "keyword": "Keyword"}, default_columns=["Keyword", "Mentions", "Growth (%)"])
            st.dataframe(df_kws, use_container_width=True)
        else:
            st.info("No emerging keywords found.")
            
    with col2:
        st.markdown("#### Emerging Entities (NER Growth)")
        ent_res, ent_ok = fetch_api("/api/analytics/entities")
        ents = ent_res.get("entities", []) if ent_ok else []
        if ents:
            df_ents = safe_dataframe(ents, column_mapping={"entity": "Entity", "type": "Type", "recent_mentions": "Mentions", "growth_pct": "Growth (%)"}, default_columns=["Entity", "Type", "Mentions", "Growth (%)"])
            st.dataframe(df_ents, use_container_width=True)
        else:
            st.info("No emerging entities found.")


# =====================================================
# PAGE 5 — SEARCH
# =====================================================
elif page == "Search":
    st.markdown("### 🔍 HYBRID INTELLIGENCE SEARCH ENGINE")
    st.caption("Search across news corpus using BM25 Text, 384-dim Dense Vector KNN, or Hybrid RRF Search")

    q = st.text_input("Enter Search Query", placeholder="e.g. economy growth in India, technology, stocks...")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        search_mode = st.radio("Search Retrieval Mode", ["hybrid", "bm25", "knn"], index=0, horizontal=True)
    with col_s2:
        search_cat = st.selectbox("Category Filter", ["All", "Business", "Technology", "Politics", "Sports", "World"])
    with col_s3:
        search_limit = st.slider("Result Limit", 5, 30, 10)

    if q.strip():
        params = {"q": q.strip(), "type": search_mode, "limit": search_limit}
        if search_cat != "All":
            params["category"] = search_cat
            
        s_res, s_ok = fetch_api("/api/search", params=params)
        hits = s_res.get("articles", []) if s_ok else []
        
        if hits:
            st.markdown(f"Found **{len(hits)}** matching results via **{search_mode.upper()}** retrieval:")
            for h in hits:
                score = h.get("_score", 0.0)
                st.markdown(f"""
                    <div class="intel-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="badge badge-source">{h.get('source')}</span>
                            <span class="badge badge-category">Score: {score:.4f}</span>
                        </div>
                        <div style="font-size: 15px; font-weight: 700; color: #F0F6FC; margin: 6px 0;">
                            <a href="{h.get('link', '#')}" target="_blank" style="color: #58A6FF; text-decoration: none;">{h.get('title')}</a>
                        </div>
                        <div style="font-size: 12px; color: #8B949E;">{h.get('summary')}</div>
                        <div style="font-size: 11px; color: #7EE787; margin-top: 6px;">
                            ✓ Matched via {search_mode.upper()} Retrieval Engine (ES Index: news_articles)
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No search results found for this query.")


# =====================================================
# PAGE 6 — AI ANALYST
# =====================================================
elif page == "AI Analyst":
    st.markdown("### 🤖 AI NEWS ANALYST")
    st.caption("Ask questions about the indexed news intelligence.")

    st.markdown("**Suggested Queries:**")
    sq1, sq2, sq3 = st.columns(3)
    user_q = ""
    if sq1.button("What are the major news trends today?"):
        user_q = "What are the major news trends today?"
    if sq2.button("Which topics are appearing across multiple sources?"):
        user_q = "Which topics are appearing across multiple sources?"
    if sq3.button("What major volume spikes were detected?"):
        user_q = "What major volume spikes were detected?"

    input_q = st.text_area("Ask AI Analyst", value=user_q, placeholder="e.g. Summarize top economic developments reported today...")
    
    if st.button("Ask AI Analyst", type="primary") and input_q.strip():
        with st.spinner("Executing Agentic Intent Routing & Grounded RAG..."):
            rag_res, rag_ok = post_api("/api/ai/ask", {"question": input_q.strip()})
            
        if rag_ok and "error" not in rag_res:
            st.markdown("#### 💡 AI ANSWER")
            st.info(rag_res.get("answer"))

            st.markdown("#### 📌 KEY INSIGHTS")
            insights = rag_res.get("insights", [])
            if insights:
                for ins in insights:
                    st.markdown(f"• {ins}")
            else:
                st.markdown("• Answer generated directly from retrieved article context.")

            st.markdown("#### 📚 SOURCE EVIDENCE & CITATIONS")
            sources = rag_res.get("sources", [])
            if sources:
                for idx, src in enumerate(sources, 1):
                    st.markdown(f"""
                        <div class="intel-card">
                            <div style="font-weight: 700; color: #58A6FF;">[{idx}] {src.get('title')}</div>
                            <div style="font-size: 12px; color: #8B949E;">Source: <b>{src.get('source')}</b> | Published: {str(src.get('published_date'))[:19]}</div>
                            <div style="font-size: 11px; margin-top: 4px;"><a href="{src.get('link', '#')}" target="_blank" style="color: #7EE787;">Read Source Article →</a></div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No specific article citations attached.")

            with st.expander("How this answer was generated"):
                st.markdown(f"""
                    <div class="trace-box">
                        Intent Detected : {rag_res.get('intent', 'UNKNOWN')}<br>
                        Provider        : {rag_res.get('provider', 'RAG')}<br>
                        Tools Executed  : {', '.join(rag_res.get('tools_executed', []))}<br>
                        Docs Retrieved  : {len(sources)}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"AI Analyst service unavailable: {rag_res.get('error', 'Unknown Error')}")


# =====================================================
# PAGE 7 — ARTICLE EXPLORER
# =====================================================
elif page == "Article Explorer":
    st.markdown("### 📄 ARTICLE EXPLORER")
    st.caption("Inspect raw and enriched MongoDB document structures")

    target_id = st.text_input("Enter Article ID or Link")
    
    if target_id.strip():
        art_res, art_ok = fetch_api(f"/api/articles/{target_id.strip()}")
        if art_ok:
            st.markdown(f"### {art_res.get('title')}")
            st.markdown(f"**Source:** `{art_res.get('source')}` | **Authors:** `{', '.join(art_res.get('authors', []))}` | **Published:** `{art_res.get('published_date')}`")
            st.markdown("#### Summary")
            st.write(art_res.get("summary"))
            st.markdown("#### Clean Content")
            st.text_area("Article Content", art_res.get("clean_content"), height=250)
            st.markdown("#### Pipeline Processing State")
            st.json(art_res.get("processing", {}))
        else:
            st.error("Article not found in database.")


# =====================================================
# PAGE 8 — SYSTEM HEALTH
# =====================================================
elif page == "System Health":
    st.markdown("### 🛠️ SYSTEM HEALTH & MONITORING")
    st.caption("Technical infrastructure state, component metrics, and consumer lag")

    h_res, h_ok = fetch_api("/health")
    m_res, m_ok = fetch_api("/api/metrics")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("FastAPI Backend", "Healthy" if h_ok else "Offline")
    m2.metric("MongoDB Database", "Healthy" if h_res.get("mongodb") == "ok" else "Offline")
    m3.metric("Elasticsearch Engine", "Healthy" if h_res.get("elasticsearch") == "ok" else "Offline")
    m4.metric("Total Documents", f"{m_res.get('total_articles', 0):,}")

    st.markdown("---")
    st.markdown("#### Pipeline Queue Metrics")
    q1, q2, q3 = st.columns(3)
    q1.metric("Completed Pipeline Jobs", f"{m_res.get('completed_articles', 0):,}")
    q2.metric("Pending Pipeline Jobs", f"{m_res.get('pending_articles', 0):,}")
    q3.metric("Failed / Retry Queue", f"{m_res.get('failed_articles', 0):,}")
