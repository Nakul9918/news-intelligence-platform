# 💡 Master Product Insights Catalog — News Intelligence Platform

**Document Version**: 25.0  
**Date**: August 9, 2026  
**Scope**: Mathematical & Data Justification Catalog for All 16 Platform Intelligence Features

---

## 1. Insight Classification Matrix

| Insight # | Insight Name | Mathematical / Data Justification | Grade |
| :---: | :--- | :--- | :---: |
| **01** | **Realtime News Stream** | Backed by `created_at` timestamp index & direct live RSS stream. | **A (HIGH VALUE + DATA READY)** |
| **02** | **Top Current Stories (Coverage Score)** | Ranked by Multi-factor formula: $0.35 \times \text{Recency} + 0.35 \times \text{SourceCount} + 0.30 \times \text{Volume}$. | **A (HIGH VALUE + DATA READY)** |
| **03** | **News Volume Trend** | Grouped by `created_at` (Hourly/Daily buckets) via MongoDB aggregation. | **A (HIGH VALUE + DATA READY)** |
| **04** | **Source Intelligence** | Grouped by `source.name` comparing volume, tone, and category focus. | **A (HIGH VALUE + DATA READY)** |
| **05** | **Cross-Source Topic Overlap** | Calculated via 384-dim dense vector cosine similarity ($> 0.82$) in 48-hr window. | **A (HIGH VALUE + DATA READY)** |
| **06** | **Category Intelligence** | Grouped by Zero-Shot / BART `category.label` (12 default categories). | **A (HIGH VALUE + DATA READY)** |
| **07** | **Sentiment Split (Model-Generated)** | Grouped by FinBERT `sentiment.label` (Positive, Neutral, Negative). | **A (HIGH VALUE + DATA READY)** |
| **08** | **Emerging Keywords** | Calculated by KeyBERT frequency growth %: $\frac{\text{Recent Mentions} - \text{Baseline}}{\text{Baseline}} \times 100$. | **A (HIGH VALUE + DATA READY)** |
| **09** | **Named Entity Explorer** | Calculated via spaCy `entities` array frequency & category type (PER, ORG, GPE). | **A (HIGH VALUE + DATA READY)** |
| **10** | **Developing Story Timelines** | Chronological tracing of articles matching story topic over time. | **A (HIGH VALUE + DATA READY)** |
| **11** | **Spike & Anomaly Detection** | Z-score volume spike detection: $Z = \frac{V_{\text{current}} - \mu}{\sigma} > 2.0$. | **B (USEFUL + NEEDS LOGIC ENHANCEMENT)** |
| **12** | **Emerging Topics Growth** | Topic velocity growth comparing 24-hr window to 7-day baseline. | **B (USEFUL + NEEDS LOGIC ENHANCEMENT)** |
| **13** | **Current Affairs Summaries** | Aggregate timeline & developing story synthesis over Today/This Week. | **A (HIGH VALUE + DATA READY)** |
| **14** | **Date-Wise News Time Machine** | Filtered by `published_datetime` date range queries on MongoDB. | **A (HIGH VALUE + DATA READY)** |
| **15** | **Universal Hybrid Search** | Reciprocal Rank Fusion (RRF) combining BM25 keyword score + 384-dim KNN score. | **A (HIGH VALUE + DATA READY)** |
| **16** | **Article Intelligence Modal** | Full document payload inspection (Summary, Sentiment, NER, Embeddings, Quality Score). | **A (HIGH VALUE + DATA READY)** |

---

## 2. Exhaustive Insight Specifications

### INSIGHT 01: REALTIME NEWS STREAM
- **Business Question**: "What news is arriving right now?"
- **Why Users Need It**: Provides immediate situational awareness of incoming breaking news across all 4 Indian publishers.
- **Data Source**: MongoDB `news_db.realtime_articles` (`ingestion_type: "realtime"`)
- **Required Fields**: `title`, `link`, `source.name`, `published_date`, `created_at`, `sentiment.label`, `category.label`
- **Calculation**: Direct query sorted by `created_at DESC` with limit $N$.
- **Realtime / Batch**: Realtime stream.
- **API Endpoint**: `GET /api/live-feed`
- **UI Representation**: Scrollable high-density news feed cards with sentiment badges.
- **Limitations**: Reliant on publisher RSS refresh frequency (~5-15 mins).

---

### INSIGHT 02: TOP CURRENT STORIES (HIGH COVERAGE RANKING)
- **Business Question**: "What are the most significant stories right now?"
- **Why Users Need It**: Filters noise to highlight stories dominating publisher attention.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `title`, `source.name`, `created_at`, `data_quality.score`
- **Calculation Formula**:
  $$\text{CoverageScore} = 0.35 \times e^{-\lambda t} + 0.35 \times \frac{\text{UniqueSources}}{4} + 0.30 \times \min\left(1.0, \frac{\text{ArticleCount}}{10}\right)$$
- **Realtime / Batch**: Realtime computed query.
- **API Endpoint**: `GET /api/news/top10`
- **UI Representation**: Ranked leadercards (#1 to #10) with multi-source coverage tags.
- **Limitations**: Ranking reflects media coverage volume, not subjective real-world importance.

---

### INSIGHT 03: NEWS VOLUME TREND ANALYTICS
- **Business Question**: "How much news is being produced over time?"
- **Why Users Need It**: Visualizes news publishing velocity and detects macro activity surges.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `created_at`, `published_date`
- **Calculation**: MongoDB Aggregation `$bucket` or `$group` by hour/day.
- **Realtime / Batch**: Batch / Cached aggregation (TTL 15s).
- **API Endpoint**: `GET /api/analytics/volume`
- **UI Representation**: High-density time-series bar/area chart.

---

### INSIGHT 04: SOURCE INTELLIGENCE & 4-NEWSPAPER COMPARISON
- **Business Question**: "How do the 4 major publishers cover the same topic differently?"
- **Why Users Need It**: Exposes publisher focus, volume split, and editorial tone differences.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `source.name`, `title`, `category.label`, `sentiment.label`, `keywords`
- **Calculation**: Group by `source.name` where `topic_query` matches. Calculate total volume, tone split (% positive, neutral, negative), and top 3 keywords per publisher.
- **API Endpoint**: `GET /api/news/compare-publishers`
- **UI Representation**: 4-column side-by-side publisher comparison grid (Economic Times, The Hindu, Indian Express, Hindustan Times).
- **Limitations**: Tone is model-generated (FinBERT), not human subjective critique.

---

### INSIGHT 05: CROSS-SOURCE TOPIC OVERLAP
- **Business Question**: "Which specific events are being reported by multiple independent newspapers?"
- **Why Users Need It**: Validates story credibility through multi-publisher verification.
- **Data Source**: MongoDB + Elasticsearch 384-dim Dense Vector Index
- **Required Fields**: `article_id`, `title`, `source.name`, `embedding`
- **Calculation**: Cosine similarity $S = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|} \ge 0.82$ within 48-hour window across distinct `source.name`.
- **API Endpoint**: `GET /api/analytics/cross-source`
- **UI Representation**: Cross-publisher story cluster cards with source badges.

---

### INSIGHT 06: CATEGORY INTELLIGENCE
- **Business Question**: "What categories dominate current news coverage?"
- **Why Users Need It**: Categorizes news into 12 domain verticals (Politics, Business, Tech, Sports, etc.).
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `category.label`, `category.confidence`
- **Calculation**: Group by `category.label`, count articles, and compute percentage share.
- **API Endpoint**: `GET /api/analytics/categories`
- **UI Representation**: Categorical pie chart and domain breakdown table.

---

### INSIGHT 07: SENTIMENT INTELLIGENCE (MODEL-GENERATED)
- **Business Question**: "What is the overall tone distribution across topics and sources?"
- **Why Users Need It**: Tracks sentiment shifts in market, economy, or political coverage over time.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `sentiment.label` (Positive, Neutral, Negative), `sentiment.score`
- **Calculation**: Count articles per sentiment label; compute positive/negative ratio.
- **API Endpoint**: `GET /api/analytics/sentiment`
- **UI Representation**: 3-bar sentiment distribution chart with disclaimer ("Model-Generated").

---

### INSIGHT 08: EMERGING KEYWORDS
- **Business Question**: "What specific keywords are spiking in frequency right now?"
- **Why Users Need It**: Discovers emerging topics before they become mainstream headlines.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `keywords`, `created_at`
- **Calculation Formula**:
  $$\text{GrowthPct} = \frac{\text{Mentions}_{\text{24h}} - \text{Mentions}_{\text{baseline}}}{\max(1, \text{Mentions}_{\text{baseline}})} \times 100$$
- **API Endpoint**: `GET /api/analytics/keywords`
- **UI Representation**: Data table showing `keyword`, `recent_mentions`, and `growth_pct`.

---

### INSIGHT 09: NAMED ENTITY EXPLORER
- **Business Question**: "Which people, organizations, and locations are most mentioned?"
- **Why Users Need It**: Provides entity-centric intelligence for tracking companies, politicians, and countries.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `entities.entity`, `entities.label` (PER, ORG, GPE)
- **Calculation**: Group by `entities.entity` and `entities.label`, count frequency, and trace co-occurring keywords.
- **API Endpoint**: `GET /api/analytics/entities`
- **UI Representation**: Entity breakdown table with entity type badges.

---

### INSIGHT 10: DEVELOPING STORY TIMELINES ("WHAT HAPPENED NEXT?")
- **Business Question**: "How has a specific developing story evolved over time?"
- **Why Users Need It**: Traces chronological progression of ongoing news stories (e.g. elections, market policy).
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `title`, `summary.text`, `published_date`, `source.name`
- **Calculation**: Filter by topic string, sort by `created_at ASC`, assign stage labels (`INITIAL REPORT`, `UPDATE 1`, `LATEST UPDATE`).
- **API Endpoint**: `GET /api/news/timeline`
- **UI Representation**: Vertical chronological timeline step cards.

---

### INSIGHT 11: SPIKE & ANOMALY DETECTION
- **Business Question**: "Is news volume for a topic experiencing an unusual spike?"
- **Why Users Need It**: Alerts users to breaking crises or major unexpected events.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `created_at`, `category.label`
- **Calculation**: Calculate hourly volume mean $\mu$ and std dev $\sigma$ over 7-day window. Flag spike if $V_{\text{current}} > \mu + 2\sigma$.
- **API Endpoint**: `GET /api/analytics/spikes`
- **UI Representation**: Alert callout banner with baseline volume vs current volume metrics.

---

### INSIGHT 12: EMERGING TOPICS GROWTH
- **Business Question**: "Which topics are accelerating fastest in news coverage?"
- **Why Users Need It**: Identifies momentum trends across sectors.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `keywords`, `category.label`, `created_at`
- **Calculation**: Compare 24-hour keyword volume velocity vs preceding 7-day average velocity.
- **API Endpoint**: `GET /api/analytics/keywords`
- **UI Representation**: Trending topic velocity rank list.

---

### INSIGHT 13: CURRENT AFFAIRS SUMMARIES
- **Business Question**: "What are the key current affairs highlights for Today / This Week / This Month?"
- **Why Users Need It**: Executive summary generator for periodic news digests.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `title`, `summary.text`, `published_date`, `data_quality.score`
- **Calculation**: Query high-quality articles ($DQ \ge 70$) within selected window; synthesize top summaries.
- **API Endpoint**: `GET /api/news/developing` & `GET /api/news/top`
- **UI Representation**: Executive briefing cards.

---

### INSIGHT 14: DATE-WISE NEWS TIME MACHINE
- **Business Question**: "What happened in Indian news on a specific date or date range in the past?"
- **Why Users Need It**: Enables historical news exploration for research and audit.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: `published_datetime`, `created_at`, `title`, `summary`, `source.name`
- **Calculation**: Query MongoDB using date range filter `{$gte: start_dt, $lt: end_dt}`.
- **API Endpoint**: `GET /api/intelligence/time-machine`
- **UI Representation**: Date selector control panel + historical article digest.

---

### INSIGHT 15: UNIVERSAL HYBRID SEARCH (BM25 + VECTOR KNN RRF)
- **Business Question**: "Find relevant news by keyword, entity, or semantic intent."
- **Why Users Need It**: Combines exact keyword matching (BM25) with deep conceptual search (Dense Vector).
- **Data Source**: Elasticsearch `news_articles` index + MongoDB fallback
- **Required Fields**: `title`, `clean_content`, `embedding` (384-dim)
- **Calculation**: Reciprocal Rank Fusion: $\text{RRF}(doc) = \frac{1}{60 + r_{BM25}} + \frac{1}{60 + r_{KNN}}$.
- **API Endpoint**: `GET /api/search`
- **UI Representation**: Search input box with retrieval strategy dropdown (Hybrid, BM25, Dense Vector KNN).

---

### INSIGHT 16: ARTICLE INTELLIGENCE MODAL INSPECTOR
- **Business Question**: "What are all details, metrics, and quality scores for a specific article?"
- **Why Users Need It**: Provides complete auditability for any individual document.
- **Data Source**: MongoDB `news_db.realtime_articles`
- **Required Fields**: All document fields (`article_id`, `title`, `content`, `summary`, `sentiment`, `category`, `keywords`, `entities`, `data_quality`)
- **Calculation**: Direct single-document retrieval by `article_id`.
- **API Endpoint**: `GET /api/articles/{article_id}`
- **UI Representation**: Inspector modal with full text, quality score gauge, and NLP metadata tags.
