# News Intelligence Command Center — Frontend Product Specification

**Version**: 20.0 (Company-Grade Real-Time Command Center UI)  
**Target Platform**: Streamlit + Plotly + FastAPI Backend  
**Theme Tokens**: Dark Mode (`#0B0F17` background, `#121824` cards, `#06B6D4` cyan accent)

---

## 1. Information Architecture (12 Workspaces)

The main navigation bar is structured into 12 dedicated Command Center workspaces:

1. **`01. EXECUTIVE OVERVIEW`**: Executive Command Center overview featuring 9 real metric counter cards, infrastructure status dots, 24-hour volume trend, publisher distribution, and mathematical metric explainability expanders.
2. **`02. LIVE NEWS FEED`**: Real-time arriving news stream with auto-refresh, source filtering, category filtering, sentiment filtering, and relative timestamp badges.
3. **`03. TOP CURRENT STORIES`**: Transparent weighted scoring ranking for top news stories with article drill-down expanders.
4. **`04. TIME MACHINE`**: Period explorer (`Today`, `Yesterday`, `7 Days`, `30 Days`, `Month`, `Custom Date Range`) displaying period volume, source split, top categories, sentiment distribution, and article list.
5. **`05. SOURCE INTELLIGENCE`**: Side-by-side 4-newspaper comparison (*Economic Times*, *The Hindu*, *Indian Express*, *Hindustan Times*) with word-boundary token matching, data-derived focus themes, and zero lifestyle noise.
6. **`06. TRENDS & TEMPORAL`**: Volume time-series, spike detection alerts with baseline explainability (`Spike Multiplier = Current 1h / Baseline 24h Avg`), and emerging keyword growth %.
7. **`07. TOPIC & KEYWORD`**: Universal search engine with strategy toggle (`Hybrid BM25 + Vector RRF`, `BM25 Keyword`, `Dense Vector KNN`), search term highlights, and frequency metrics.
8. **`08. ENTITY INTELLIGENCE`**: Deep entity tracking for People (`PER`), Organizations (`ORG`), and Locations (`LOC`) with article counts and mention frequencies.
9. **`09. EVENT INTELLIGENCE`**: Developing story clustering and chronological story evolution timelines ("What Happened Next?").
10. **`10. CURRENT AFFAIRS`**: Categorized major current affairs stories grouped by `Politics`, `Business`, `Technology`, `World`, `Sports`, `Crime`, `Science` for `Today`, `This Week`, `This Month`.
11. **`11. SEARCH + AI ASSISTANT`**: Agentic RAG natural language Q&A with sample prompt chips, grounded source evidence cards, direct article links, and tool trace observability.
12. **`12. PLATFORM HEALTH`**: Telemetry command center displaying Kafka offsets & consumer lag, MongoDB storage stats, ES 384d vector index health, NLP pipeline stage flow, and latency metrics.

---

## 2. Explainability & Data Contract Principles

Every major insight features an **Explainability Expander** (`Why am I seeing this?`):
- **No Random Fallbacks**: If a search or comparison returns 0 hits, display an explicit message instead of random articles.
- **Defensive Type Safety**: All numeric fields use `fmt_num()`, all strings use `clean_display_text()`, and all dictionary lookups use `first_present()`.
