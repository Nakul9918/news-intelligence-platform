# Topic & Keyword Intelligence Specification

## 1. Business & Product Purpose
The **Topic & Keyword Intelligence** workspace transforms news search into an enterprise-grade topic investigation module. It allows users to search any keyword, phrase, person, organization, location, or event across live and historical news articles, providing multi-dimensional insights on coverage volume, source distribution, model sentiment, topic timelines, entity mentions, and cross-source comparisons.

---

## 2. Core Questions Answered
1. **"What is being said about this topic?"** (Summary metrics, top headlines, and summaries)
2. **"How much coverage does it have?"** (Total article count & topic trend direction)
3. **"Which sources are covering it?"** (Multi-publisher ratio: `4 / 4 sources` and volume share)
4. **"How are different sources describing it?"** (4-Newspaper Source Comparison: *Economic Times*, *The Hindu*, *Indian Express*, *Hindustan Times*)
5. **"What are the related topics & keywords?"** (Clickable related keyword pills & co-occurrence topics)
6. **"Which people, organizations, and locations are mentioned?"** (NER Entity Breakdown for `PER`, `ORG`, `LOC`)
7. **"What is the model sentiment?"** (Model-generated sentiment breakdown: Positive %, Neutral %, Negative %)
8. **"How has the topic changed over time?"** (Topic Volume Timeline bucketing)
9. **"Which articles support the result?"** (Full article cards & evidence lineage drawer)

---

## 3. Architecture & Search Pipeline Integrations

```
Search Query ("RBI rate" / "crime" / "AI regulation")
    ↓
Search Modes: HYBRID (BM25 + Dense Vector KNN RRF) | BM25 | VECTOR
    ↓
FastAPI Endpoints (/api/topic/investigate & /api/search)
    ├── Filter Engine (Date Range, Source, Category, Sentiment, Sort)
    ├── Topic Analytics Aggregator (Volume, Trend Direction, Spike Threshold μ + 2σ)
    ├── Source Comparison Engine (ET, The Hindu, IE, HT coverage differences)
    ├── Entity & Keyword Extractor (Co-occurring NER & Keywords)
    └── Article Evidence Provider (Full metadata, stored summary, original URL links)
    ↓
Streamlit Dashboard Workspace 07 (Topic Investigation Workspace)
```

---

## 4. API Endpoints Contract

1. `GET /api/topic/investigate?q={query}&window={window}`
   - Returns complete topic summary, category breakdown, sentiment distribution, source comparison, timeline, entities, related keywords, and spike status.

2. `GET /api/search?q={query}&type={hybrid|bm25|knn}&limit=20&source={source}&category={category}&sentiment={sentiment}&sort_by={relevance|newest|oldest}`
   - Returns filtered article search results with relevance scores.

---

## 5. UI/UX Workflow & Components

1. **Hero Search Bar**: Supports single words, phrases, people, orgs, locations, or topics with quick example chips (`RBI rate`, `crime`, `stock market`, `AI regulation`, `Mumbai`, `elections`, `Virat Kohli`).
2. **Search Mode Selector & Details Drawer**: Toggle between `Hybrid (BM25 + Vector RRF)`, `BM25 Keyword`, and `Dense Vector KNN`.
3. **Multi-Faceted Search Filters**: Date Range, Source Filter, Category Filter, Sentiment Filter, Sorting.
4. **Topic Summary Card**: Overview metrics, Trend direction badge (`RISING`, `STABLE`, `DECLINING`), Multi-publisher coverage ratio, Top categories.
5. **Interactive Clickable Keywords & Related Topics**: Clickable pills that trigger instant re-search upon click.
6. **4-Newspaper Source Comparison**: Side-by-side comparison across *Economic Times*, *The Hindu*, *Indian Express*, and *Hindustan Times*.
7. **Topic Volume Timeline Chart**: Bucketed time-series volume distribution for the active topic query.
8. **Entity Intelligence Breakdown**: Top People (`PER`), Organizations (`ORG`), and Locations (`LOC`) with mention counts.
9. **Topic Spike Intelligence**: Anomaly alert if query volume exceeds $\mu + 2\sigma$.
10. **Article Cards & Evidence Drawer**: Rich cards with `[VIEW INTELLIGENCE]` drawer for full article lineage & cross-source related stories.
