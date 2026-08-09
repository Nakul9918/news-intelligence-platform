# 🛡️ Project Health Report — News Intelligence Platform

**Document Version**: 25.0 (Production Architecture Audit)  
**Date**: August 9, 2026  
**Scope**: Complete System Audit, Infrastructure Diagnostics, Data Integrity, and Component Health  
**Project Path**: `d:\project\news-intelligence-platform\project`

---

## 1. Executive Overview

The **News Intelligence Platform** is a defensible, enterprise-grade real-time and historical news intelligence system. It ingests news continuously from major Indian publishers, evaluates quality through a 10-point quality gate, enriches content via a 6-stage NLP pipeline (Summary, Sentiment, Category, Keywords, NER, 384-dim Dense Vector Embeddings), indexes documents for hybrid BM25 + Vector KNN search, and exposes analytical intelligence through FastAPI endpoints and Streamlit Command Center UI.

---

## 2. Infrastructure Verification & Health

| Service | Target Port | Status | Protocol / Connection | Fallback Mode |
| :--- | :--- | :--- | :--- | :--- |
| **MongoDB** | `localhost:27017` | **HEALTHY** | PyMongo / Direct TCP | Primary Database Layer |
| **Kafka** | `localhost:9092` | **FALLBACK ACTIVE** | kafka-python | Direct MongoDB Upsert Fallback (`news_db.realtime_articles`) |
| **Elasticsearch** | `localhost:9200` | **FALLBACK ACTIVE** | elasticsearch-py 8.x | MongoDB Vector KNN + Keyword Regex Fallback Engine |
| **FastAPI Server** | `localhost:8000` | **HEALTHY** | HTTP / REST | Mongo Direct Query Fallback Layer in UI |
| **Streamlit Dashboard**| `localhost:8501` | **HEALTHY** | HTTP / Web | In-Process Execution with `ttl=15` Caching |

---

## 3. Empirical Database Audit Statistics (`news_db.realtime_articles`)

*Metrics gathered via direct MongoDB aggregation queries on August 9, 2026:*

### A. Corpus Volume & Ingestion Breakdown
- **Total Platform Corpus**: **21,713 articles**
- **Real-Time Live Stream Articles**: **10,644 articles** (`ingestion_type: "realtime"`)
- **Historical Sitemap Articles**: **1,069 articles** (`ingestion_type: "historical"`)
- **Bootstrap Historical Articles**: **10,000 articles**

### B. Source Distribution Across Publishers
- **Economic Times**: **14,760 articles** (67.9%)
- **Hindustan Times**: **4,081 articles** (18.8%)
- **Indian Express**: **1,778 articles** (8.2%)
- **The Hindu**: **656 articles** (3.0%)
- **Unknown / Unassigned**: **438 articles** (2.0%)

### C. Pipeline Processing Status
- **NLP Completed**: **455 articles** (`processing.status: "COMPLETED"`)
- **Pending Pipeline Queue**: **11,257 articles** (`processing.status: "PENDING"`)
- **Quarantined Articles**: **10 articles** (Stored in `news_db.quarantine_articles`)
- **Failed Ingestions**: **1 article** (`processing.status: "FAILED"`)

### D. Document Field Completeness
- **Dense Vector Embeddings (384-dim)**: **20,438 documents** (94.1% complete — Vector KNN Ready)
- **Clean Content**: **1,303 documents**
- **Sentiment Labels**: **861 documents**
- **Keywords**: **643 documents**
- **Named Entities**: **454 documents**
- **Category Labels**: **407 documents**
- **Summaries**: **184 documents**

### E. Data Integrity & Deduplication Verification
- **Duplicate `article_id` Count**: **0** (0% duplicate IDs)
- **Duplicate `link` URL Count**: **0** (0% duplicate URLs)
- **Schema Violations / Null Fields**: Cleaned via `safe_str` and defensive schemas in [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py) and [api/routes.py](file:///d:/project/news-intelligence-platform/project/api/routes.py).

---

## 4. Complete Component Classification & Dependency Map

| Component / File | Purpose | Depends On | Used By | Status |
| :--- | :--- | :--- | :--- | :--- |
| [config.py](file:///d:/project/news-intelligence-platform/project/config.py) | Central environment config, ports, DB names | PyMongo, OS | All platform modules | **WORKING** |
| [ingestion_service.py](file:///d:/project/news-intelligence-platform/project/ingestion_service.py) | Multi-source live RSS crawler & Mongo fallback | feedparser, Kafka, PyMongo | Daemons / background | **WORKING** |
| [qc/quality_gate.py](file:///d:/project/news-intelligence-platform/project/qc/quality_gate.py) | 10-point article quality scoring (0–100) | re, urllib.parse | Ingestion & Backfill | **WORKING** |
| [pipeline_orchestrator.py](file:///d:/project/news-intelligence-platform/project/pipeline_orchestrator.py) | Asynchronous worker claiming PENDING queue | PyMongo, NLP suite | Background daemons | **WORKING** |
| [nlp/models.py](file:///d:/project/news-intelligence-platform/project/nlp/models.py) | Global model caching singleton (PyTorch/Transformers) | PyTorch, Transformers | NLP processors | **WORKING** |
| [nlp/embeddings.py](file:///d:/project/news-intelligence-platform/project/nlp/embeddings.py) | 384-dim dense vector embedding generator | SentenceTransformers | NLP pipeline & ES | **WORKING** |
| [elasticsearch_indexer/indexer.py](file:///d:/project/news-intelligence-platform/project/elasticsearch_indexer/indexer.py) | BM25 + Vector KNN hybrid Elasticsearch indexer | elasticsearch-py | Orchestrator, API | **WORKING (with Mongo fallback)** |
| [historical/backfill_manager.py](file:///d:/project/news-intelligence-platform/project/historical/backfill_manager.py) | Sitemap historical backfill controller | requests, BeautifulSoup, PyMongo | CLI / Backfill tasks | **WORKING** |
| [api/routes.py](file:///d:/project/news-intelligence-platform/project/api/routes.py) | FastAPI REST endpoints (/health, /dashboard, /search, /api/ai/ask) | FastAPI, Pydantic, PyMongo | Streamlit UI | **WORKING** |
| [api/intelligence_helpers.py](file:///d:/project/news-intelligence-platform/project/api/intelligence_helpers.py) | Mathematical intelligence algorithms & timeline engines | PyMongo, Counter, re | API & Dashboard | **WORKING** |
| [ai/rag_engine.py](file:///d:/project/news-intelligence-platform/project/ai/rag_engine.py) | Grounded Agentic RAG engine with evidence citations | HuggingFace, PyMongo | FastAPI (`/api/ai/ask`) | **WORKING** |
| [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py) | Streamlit Command Center UI (8 Workspaces) | Streamlit, Plotly, requests | End Users | **WORKING** |
| [start_daemons.py](file:///d:/project/news-intelligence-platform/project/start_daemons.py) | Master Windows background daemon launcher | subprocess, psutil | PowerShell scripts | **WORKING** |
| [stop_daemons.py](file:///d:/project/news-intelligence-platform/project/stop_daemons.py) | Master Windows background daemon shutdown | psutil | PowerShell scripts | **WORKING** |
| `historical_crawlers/historical_analysis_worker.py` | Legacy standalone batch NLP processor | PyMongo, NLP | None (Replaced by `pipeline_orchestrator.py`) | **OBSOLETE** |

---

## 5. Summary Verification
- Master regression test suite ([run_all_tests.py](file:///d:/project/news-intelligence-platform/project/run_all_tests.py)): **13/13 SUITES PASSED (100%)**
- Edge case & fault tolerance suite ([test_edge_cases.py](file:///d:/project/news-intelligence-platform/project/test_edge_cases.py)): **6/6 SUITES PASSED (100%)**

