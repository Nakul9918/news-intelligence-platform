# Event Intelligence & Story Evolution Specification

## 1. Business & Product Purpose
The **Event Intelligence & Story Evolution** workspace transforms news tracking into a real-time newsroom developing story tracker. It detects developing stories, groups related coverage across multiple publishers into distinct event clusters, generates descriptive human-readable titles, tracks the chronological timeline of developments, calculates lifecycle statuses and confidence scores, and links every update back to supporting article evidence.

---

## 2. Core Questions Answered
1. **"WHAT happened?"** (Descriptive, human-readable story titles generated from semantic story clusters)
2. **"WHEN did it start & HOW did it develop?"** (Chronological "What Happened Next?" Storyline Evolution Timeline)
3. **"HOW MANY updates occurred & WHICH sources covered it?"** (Update count & 4-Newspaper Coverage Ratio: `4 / 4 major sources`)
4. **"WHAT IS THE STORY STATUS & CONFIDENCE?"** (`BREAKING`, `DEVELOPING`, `ACTIVE`, `STABILIZING`, `QUIET` + High/Medium/Low confidence)
5. **"WHO & WHERE are involved?"** (Clickable People, Organization, and Location entities connected to Workspace 08)
6. **"WHAT ARE THE KEYWORDS & TOPICS?"** (Associated Keywords connected to Workspace 07)
7. **"WHAT IS THE LATEST DEVELOPMENT?"** (Live Latest Update Banner)
8. **"WHICH ARTICLES support each development?"** (Supporting Article Evidence Drawer)

---

## 3. Architecture & Data Flow

```
Real-time News Stream / MongoDB / Elasticsearch
    ↓
Multi-Signal Semantic Clustering Engine (Title phrase n-grams + Entity co-occurrence + Temporal proximity < 72h)
    ↓
Event Detector & Lifecycle Manager
    ├── Descriptive Event Title Generator (Extracts core headline theme)
    ├── Status Calculator (BREAKING | DEVELOPING | ACTIVE | STABILIZING | QUIET)
    ├── Confidence Estimator (HIGH ≥ 85% | MEDIUM 65-84% | LOW < 65%)
    ├── Chronological Storyline Evolution Builder (Stage 1 Initial Report → Stage 2 Confirmation → Stage 3 Update)
    └── 4-Newspaper Coverage Analyzer (ET, The Hindu, IE, HT timeline per portal)
    ↓
FastAPI Backend (/api/news/developing & /api/events/investigate)
    ↓
Streamlit Dashboard Workspace 09 (Real-Time Developing Story Tracker)
```

---

## 4. API Endpoints Contract

1. `GET /api/news/developing?status={all|breaking|developing|active|quiet}&window={24h|7d|30d}&q={search_term}`
   - Returns developing story clusters with descriptive titles, lifecycle statuses, confidence scores, update counts, and latest headline teasers.

2. `GET /api/events/investigate?event_id={event_id}&topic={topic}`
   - Returns full story profile including latest development banner, chronological timeline, 4-newspaper comparison, associated entities/keywords, activity chart, and supporting article evidence.

---

## 5. UI/UX Workflow & Components

1. **Top Metrics Overview Bar**: Total Active Stories, Developing Stories Count, Breaking Alerts Count, Updates Today.
2. **Hero Story Search & Filter Toolbar**: Search box + Status Selector (`BREAKING`, `DEVELOPING`, `ACTIVE`, `STABILIZING`, `QUIET`), Time Window (`24H`, `7D`, `30D`), Source Filter, Category Filter, and Sort Order (`Most Recent`, `Most Updates`, `Highest Confidence`).
3. **Interactive Event Cards**: Visually distinct status badges (`🔴 BREAKING`, `🟧 DEVELOPING`, `🟦 ACTIVE`, `🟩 QUIET`), descriptive story title, update count, 4-source ratio, key entities/keywords, activity trend %, and `[VIEW STORY]` button.
4. **Event Detail Investigation Drawer (`[VIEW STORY]`)**:
   - **Latest Development Banner**: Highlights the single most recent update headline, source, timestamp, and summary.
   - **Chronological Story Evolution Timeline**: Step-by-step evolution (`10:15 Initial Report` $\rightarrow$ `11:02 Multi-Source Confirmation` $\rightarrow$ `14:15 New Development`).
   - **Story Activity Chart**: Time-series update volume chart.
   - **4-Newspaper Source Coverage Comparison**: Publisher timeline breakdown.
   - **Event Entities & Keywords**: Clickable People, Organizations, Locations (navigating to Workspace 08) and Keywords (navigating to Workspace 07).
   - **Supporting Article Evidence**: Rich cards with `[VIEW INTELLIGENCE]` drawer.
