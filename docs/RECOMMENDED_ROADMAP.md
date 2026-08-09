# 🎯 Prioritized Technical Roadmap — News Intelligence Platform

**Document Version**: 25.0  
**Date**: August 9, 2026  
**Scope**: Prioritized Technical Execution Roadmap (P0 → P3) & UI Handoff Criteria

---

## 1. Priority Tiers & Execution Sequence

```
P0 (System-Breaking & Critical Hardening)
   ↓
P1 (Core Architecture, Pipeline & Data Quality)
   ↓
P2 (Advanced Analytics & Staged Historical Backfill)
   ↓
P3 (UI Rebuild & Frontend Team Handoff)
```

---

## 2. Exhaustive Task Breakdown

### 🔴 P0: SYSTEM-BREAKING & CRITICAL HARDENING (COMPLETED)
- [x] **P0-1**: Fix Streamlit DataFrame `KeyError: ['mentions', 'growth']` contract mismatch in [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py).
- [x] **P0-2**: Implement `safe_regex()` escaping across MongoDB search queries to eliminate `Location51091` regex metacharacter crashes.
- [x] **P0-3**: Optimize API client caching TTL from `ttl=1` to `ttl=15` in [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py) to resolve dashboard latency.
- [x] **P0-4**: Fix background process termination on Windows by building `start_daemons.py` and `stop_daemons.py`.
- [x] **P0-5**: Harden Kafka producer and Elasticsearch indexer with direct MongoDB fallback layers when ports 9092 or 9200 are down.

---

### 🟠 P1: CORE ARCHITECTURE, PIPELINE & DATA QUALITY (COMPLETED / ACTIVE)
- [x] **P1-1**: Verify 10-point Quality Gate scoring in [qc/quality_gate.py](file:///d:/project/news-intelligence-platform/project/qc/quality_gate.py) ensuring invalid/short articles are routed to `quarantine_articles`.
- [x] **P1-2**: Verify 6-stage NLP enrichment pipeline (Summary, Sentiment, Category, Keywords, NER, 384-dim Vector Embeddings).
- [x] **P1-3**: Verify Reciprocal Rank Fusion (RRF) Hybrid Search combining BM25 keyword search + 384-dim Dense Vector KNN search.
- [x] **P1-4**: Fix historical backfill sitemap sub-index parsing for **The Hindu**, **Indian Express**, and **Hindustan Times**.
- [x] **P1-5**: Silence third-party logger stdout noise (`newspaper3k`, `trafilatura`, `urllib3`) in [historical_crawlers/extractor.py](file:///d:/project/news-intelligence-platform/project/historical_crawlers/extractor.py).

---

### 🟡 P2: ADVANCED ANALYTICS & STAGED HISTORICAL BACKFILL (ACTIVE)
- [x] **P2-1**: Implement 4-Newspaper Topic Comparison Engine ([api/intelligence_helpers.py](file:///d:/project/news-intelligence-platform/project/api/intelligence_helpers.py)).
- [x] **P2-2**: Implement Story Evolution Timeline ("What Happened Next?") algorithm.
- [x] **P2-3**: Implement Grounded Agentic AI RAG Engine ([ai/rag_engine.py](file:///d:/project/news-intelligence-platform/project/ai/rag_engine.py)).
- [ ] **P2-4**: Execute Stage 2 Historical Backfill (January 2026 – June 2026 ~50,000 articles).
- [ ] **P2-5**: Enable automatic background NLP worker batching with memory garbage collection cycles (`gc.collect()`).

---

### 🔵 P3: UI REBUILD & FRONTEND TEAM HANDOFF (NEXT PHASE)
- [ ] **P3-1**: Deliver [docs/FRONTEND_PRODUCT_SPEC.md](file:///d:/project/news-intelligence-platform/project/docs/FRONTEND_PRODUCT_SPEC.md) to dedicated UI/UX development team.
- [ ] **P3-2**: Rebuild Streamlit dashboard or Next.js frontend following the 16 structural workspace specifications.
- [ ] **P3-3**: Implement high-density data visualizations, metric badges, and interactive drill-down modals.
- [ ] **P3-4**: Perform end-to-end user experience testing across desktop and mobile viewports.

---

## 3. UI Handoff Criteria Checklist

The backend architecture and documentation suite are ready for UI development when:
- [x] All 13 master test suites in `run_all_tests.py` pass with 100% success.
- [x] All 6 edge-case test suites in `test_edge_cases.py` pass with 100% success.
- [x] All 6 master documentation deliverables are authored and stored in `docs/`.
- [x] Zero Python exceptions occur on arbitrary search inputs, emojis, or non-matching queries.
- [x] Every API endpoint consumes real database queries and returns typed JSON responses.
