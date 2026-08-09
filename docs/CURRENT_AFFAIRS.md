# Current Affairs Command Center Specification

## 1. Business & Product Purpose
The **Current Affairs Command Center** serves as an executive daily news intelligence briefing module. It synthesizes real-time coverage across four major newspapers (*Economic Times*, *The Hindu*, *Indian Express*, *Hindustan Times*), ranks top stories by cross-source coverage and update frequency, highlights critical developments with grounded context ("What Happened & Why It Matters"), compares portal coverage timelines, tracks timeframe deltas ("What Changed Today?"), and provides grounded AI briefings.

---

## 2. Core Questions Answered
1. **"What happened today / in the selected timeframe?"** (Top Stories & Latest Developments Feed)
2. **"What are the top ranked current affairs stories?"** (Rank cards `#01` to `#05` with 4-source ratio and update count)
3. **"What happened & why does it matter?"** (Grounded Highlights)
4. **"Which stories are developing right now?"** (Integration with Event Intelligence)
5. **"What changed compared to the previous timeframe?"** (Delta metrics: new stories, top growing category, emerging keywords)
6. **"How are the four news portals covering the news?"** (4-Newspaper Coverage Breakdown Matrix)
7. **"What does the daily AI briefing summarize?"** (Grounded AI Briefing text with citations)

---

## 3. Architecture & Data Flow

```
Real-time News Stream / MongoDB / Elasticsearch
    ↓
Current Affairs Intelligence Engine (Timeframe filtering + Event Cluster Integration + 4-Portal Matrix)
    ├── KPI Metrics Calculator (Top Stories, Updates Today, Sources Ratio, Active Categories)
    ├── Ranked Top Stories Generator (#01 - #05 with status, update count, source ratio)
    ├── Grounded Highlights Generator ("What Happened & Why It Matters")
    ├── Timeframe Delta Analyzer ("What Changed Today?")
    ├── 4-Newspaper Coverage Matrix (ET, The Hindu, IE, HT breakdown)
    └── Grounded AI Briefing Synthesizer
    ↓
FastAPI Backend (/api/news/current-affairs)
    ↓
Streamlit Dashboard Workspace 10 (Daily News Intelligence Briefing Workspace)
```

---

## 4. API Endpoints Contract

1. `GET /api/news/current-affairs?timeframe={Today|Yesterday|Last 24 Hours|Last 3 Days|Last 7 Days|This Month}`
   - Returns complete briefing metrics, top ranked story clusters, grounded highlights, 4-newspaper coverage matrix, cross-source stories, latest developments feed, trending entities/keywords, what changed comparison, and AI briefing.

---

## 5. UI/UX Workflow & Components

1. **Header & Live Pipeline Health Status**: Telemetry indicator (`● LIVE PIPELINE — STREAMING`).
2. **Time Range Control Toolbar**: `TODAY`, `YESTERDAY`, `LAST 24 HOURS`, `LAST 3 DAYS`, `LAST 7 DAYS`, `THIS MONTH`, `CUSTOM RANGE`.
3. **Top Metrics Strip**: Top Stories Count, Updates Today, Developing Stories Count, Active Sources Ratio, Active Categories Count.
4. **🔥 Top Current-Affairs Stories**: Rank cards (`#01` to `#05`) with status badge, title, 4-source ratio, update count, timestamps, top entities/keywords, and `[VIEW STORY]` / `[ASK AI]` buttons.
5. **⭐ Current-Affairs Highlights ("What Happened & Why It Matters")**: Cards breaking down story impact grounded in stored summaries.
6. **🔴 Developing Now**: Integrates directly with Workspace 09 Event Intelligence.
7. **⚡ What Changed Today?**: Metrics comparing selected timeframe against previous baseline.
8. **🌐 Four-Source News Coverage**: Publisher comparison matrix for *Economic Times*, *The Hindu*, *Indian Express*, and *Hindustan Times*.
9. **📌 Category Intelligence & Latest Developments Feed**: Category breakdowns + real-time newest news feed.
10. **🤖 Daily AI Intelligence Briefing & 👁️ What To Watch**: Interactive AI briefing text with grounded citations and high-activity topic alerts.
11. **📅 Date-Wise News Explorer & Monthly Overview**: Date selector and monthly intelligence breakdown.
