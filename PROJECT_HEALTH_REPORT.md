# News Intelligence Platform — Comprehensive Project Health Audit Report

**Project Root:** `d:\project\news-intelligence-platform\project`  
**Date:** August 9, 2026  
**Status:** Audit Completed (Task 1)  

---

## Executive Summary

A comprehensive, company-grade audit of the **News Intelligence Platform** was conducted across code structure, active runtime infrastructure, data pipeline stages, security, API endpoints, Streamlit dashboard, AI/RAG engine, and test suites.

While individual python scripts, MongoDB persistence (20,440 documents), and Streamlit UI exist, the production runtime evaluation revealed critical service outages (Kafka and Elasticsearch offline), duplicate backend/API directories, missing Data Quality (DQ) quarantine gates, auto-commit Kafka offset risks, and lack of unified test orchestration.

---

## Infrastructure Runtime Status

| Component | Port / URI | Actual Status | Findings & Impact |
| :--- | :--- | :---: | :--- |
| **MongoDB** | `localhost:27017` | 🟢 **ACTIVE** | `news_db.realtime_articles` contains 20,440 documents. Indexed on `article_id`. |
| **Streamlit Dashboard** | `localhost:8501` | 🟢 **ACTIVE** | Dashboard active via `run_dashboard.py`. |
| **Apache Kafka** | `localhost:9092` | 🔴 **OFFLINE** | Port 9092 down. Producers/consumers fall back to direct DB or fail. |
| **Elasticsearch** | `http://localhost:9200` | 🔴 **OFFLINE** | Port 9200 down. Hybrid & vector KNN search degraded to MongoDB fallback. |
| **FastAPI Backend** | `http://localhost:8000` | 🔴 **OFFLINE** | API server not running or crashed due to import/ES module dependency timeout. |

---

## Detailed Audit Findings Across 26 Key Categories

### 1. Duplicate Code
- **API & Backend Duplication:** `backend/` (`app.py`, `routes/`) and `api/` (`main.py`, `routes.py`) contain duplicate route definitions and database helpers.
- **Elasticsearch Indexer Duplication:** `realtime_pipeline/elasticsearch_indexer.py` vs `elasticsearch_indexer/indexer.py`.
- **Config Duplication:** `config.py` vs `api/config.py` vs `backend/config.py`.

### 2. Dead Code & 3. Unused Files
- Obsolete historical crawler backups in `archive/` and `historical_crawlers/*_old.py`.
- `qc` directory contains empty 9-byte placeholder file.
- `query` directory contains empty 9-byte placeholder file.

### 4. Broken Imports & 5. Circular Imports
- `streaming/realtime_consumer.py` attempts direct import of `config` without python package execution (`python -m streaming.realtime_consumer`), throwing `ModuleNotFoundError`.
- `realtime_pipeline/realtime_nlp_pipeline.py` relies on hardcoded imports from `nlp.*` which fail when launched outside root working directory.

### 6. Incorrect Paths & 7. Hardcoded Configuration
- Hardcoded URLs `http://127.0.0.1:8000` and `http://127.0.0.1:9200` in multiple scripts instead of reading exclusively from `config.py` or `.env`.
- Database collection names referenced hardcoded in `api/config.py` as strings rather than imported tokens.

### 8. Missing Dependencies & 9. Incorrect Environment Variables
- `requirements.txt` vs `requirements_current.txt` vs `requirements_windows.txt` mismatch. Some optional dependencies (`streamlit-autorefresh`, `sentence-transformers`) are missing standard pin constraints.
- `.env` lacks AI API key placeholders (`GEMINI_API_KEY`, `OPENAI_API_KEY`) and Kafka SSL configurations.

### 10. Race Conditions & 11. Retry Problems
- `pipeline_orchestrator.py` claims MongoDB documents by setting `processing.status = "PROCESSING"`, but stale lease timeout lacks atomic lease renewal when NLP takes > 60 seconds for heavy BART summarization.
- No max retry exponential backoff for failed extraction attempts; failed URLs can stall queue loops.

### 12. Data Corruption Possibilities & 13. Inconsistent Schemas
- Ingestion loaders store RSS feeds with empty `content: ""` and `clean_content: ""` without forcing extraction before pipeline completion.
- Date fields stored in mixed formats: ISO-8601 strings (`2026-08-08T11:41:28`), RSS RFC-822 strings (`Sat, 08 Aug 2026 14:44:12 +0530`), and BSON datetimes.

### 14. Inconsistent Status Fields & 15. Inconsistent Article IDs
- Pipeline stages use overlapping status labels: `"PENDING"`, `"ingestion"`, `"collector"`, `"extractor"`, `"cleaning"`, `"category"`, `"completed"`.
- SHA256 article ID calculation differs slightly between sitemap collector (`url` normalizer) and RSS crawler.

### 16. Elasticsearch Mapping Problems & 17. MongoDB Indexing Problems
- `news_articles` index mapping in ES lacks fallback handling for null/empty 384-dimensional dense vectors.
- MongoDB `news_db.realtime_articles` lacks compound index on `(processing.status, published_datetime)` for efficient orchestrator polling.

### 18. Kafka Consumer Problems
- `ENABLE_AUTO_COMMIT = True` in `config.py`. Consumers auto-commit offset before article extraction and Mongo persistence complete. If consumer crashes during NLP, the message is permanently lost!

### 19. Dashboard/API Synchronization Problems & 20. Real-Time Refresh Problems
- Streamlit dashboard calls API endpoints directly, but when API (8000) is offline, dashboard renders empty fallback boxes rather than directly polling Mongo or auto-reconnecting gracefully.

### 21. AI/RAG Grounding Problems
- `ai/rag_engine.py` context builder must strictly enforce `"Insufficient evidence"` responses when retrieved documents do not contain answers for out-of-domain queries.

### 22. Security Problems
- Raw exception messages returned in API response bodies.
- Lack of strict input sanitization on search queries in vector RAG routing.

### 23. Logging Problems & 24. Shutdown Problems
- Unstructured `print()` statements in crawler daemons instead of standard `logging` with level filters.
- PowerShell script `stop_project.ps1` leaves background Python processes open if PIDs are not cleanly captured.

### 25. Memory Problems & 26. Performance Bottlenecks
- NLP modules (`summarizer.py`, `category_classifier.py`, `ner.py`) re-initialize PyTorch / Transformer model pipelines on worker init without global singleton caching, consuming high VRAM/RAM.

---

## Issue Classification

### 🚨 Critical Issues
1. **Kafka (9092) & Elasticsearch (9200) Offline:** Downstream search & streaming pipelines are unavailable.
2. **Kafka Auto-Commit Data Loss Risk:** `ENABLE_AUTO_COMMIT = True` risks unacknowledged data loss on consumer crashes.
3. **Missing Data Quality (DQ) Quarantine Layer:** Invalid/empty articles bypass validation and enter NLP pipeline.
4. **FastAPI Backend Offline / Route Duplication:** Port 8000 down and route code split across `backend/` and `api/`.

### ⚠️ High Issues
1. **Unextracted Article Bodies:** Thousands of Mongo articles stored with `content: ""` and `clean_content: ""` in database.
2. **NLP Model Re-loading Bottleneck:** Transformer pipelines loaded without singleton caching.
3. **Inconsistent Processing Statuses & Schema Fields:** Status string mismatches across orchestrator and analytics.
4. **Stale Lease & Race Condition in Orchestrator:** Document locks timeout without heartbeats during heavy NLP tasks.

### 🟡 Medium Issues
1. **Missing Unified Test Suite:** Unit, integration, and E2E tests scattered across workspace without single runner (`run_all_tests.ps1`).
2. **API/Dashboard Fallback:** Dashboard breaks when FastAPI server is offline.
3. **Scattered Config Files:** `config.py`, `api/config.py`, and `backend/config.py` duplicate constants.

### 2. Low Issues
1. **Obsolete Backup Files:** Unused old scripts in `archive/` and `historical_crawlers/`.
2. **Unstructured `print()` Statements:** Incomplete structured logging in background daemons.

---

## Component Health Summary

| Component | Status | Verification Notes |
| :--- | :---: | :--- |
| **MongoDB Persistence** | 🟢 WORKING | 20,440 docs stored, `article_id` index present. |
| **Streamlit UI (`dashboard.py`)** | 🟢 WORKING | Multi-tab UI functional, Dark Theme styled. |
| **News Crawlers (ET, HT, IE, Hindu)** | 🟢 WORKING | Live feed loaders tested and ingesting RSS/Sitemaps. |
| **NLP Algorithms (`nlp/`)** | 🟢 WORKING | Summarizer, Sentiment, Category, Keywords, NER, Embeddings functional. |
| **FastAPI Routes (`api/`)** | 🟡 PARTIAL | Endpoints exist but server offline due to ES startup dependency. |
| **Elasticsearch Indexer** | 🟡 PARTIAL | Code exists in `elasticsearch_indexer/`, service offline. |
| **Kafka Pipeline** | 🟡 PARTIAL | Code exists in `streaming/`, broker offline. |
| **Data Quality Gate (`qc/`)** | 🔴 MISSING | Directory empty. Needs complete validation & quarantine system. |
| **Unified Test Suite (`run_all_tests.ps1`)** | 🔴 MISSING | Lacks master automated test runner script. |

---

## Recommended Fix Order

1. **Phase A: Infrastructure & Configuration Hardening**
   - Centralize configuration in `config.py` and `.env`.
   - Standardize imports across `streaming/`, `realtime_pipeline/`, `api/`.
   - Ensure local Kafka (9092), MongoDB (27017), Elasticsearch (9200), and FastAPI (8000) services start reliably via `start_project.ps1`.

2. **Phase B: Kafka & Data Quality Hardening**
   - Fix Kafka consumer commit behavior (`ENABLE_AUTO_COMMIT = False`, manual commits post-MongoDB upsert).
   - Implement Data Quality (DQ) layer in `qc/quality_gate.py` with quality scoring and quarantine collection (`quarantine_articles`).

3. **Phase C: Extraction, Cleaning & NLP Model Caching**
   - Enforce 3-stage content extraction before NLP processing.
   - Implement model singleton loader in `nlp/` to prevent re-initialization overhead.
   - Standardize processing status workflow: `PENDING` -> `EXTRACTED` -> `ENRICHED` -> `INDEXED`.

4. **Phase D: Elasticsearch & Search Service Alignment**
   - Ensure dense vector KNN (384-dim) and BM25 hybrid search are bound cleanly in FastAPI `api/routes.py`.
   - Consolidate duplicate backend routes into unified `api/` package.

5. **Phase E: Temporal Analytics, News Comparison & RAG Hardening**
   - Verify temporal intelligence endpoints, cross-source comparison logic, and RAG grounding ("Insufficient evidence" handling).

6. **Phase F: Test Suite & End-to-End Acceptance**
   - Create `run_all_tests.ps1` covering Unit, DQ, Kafka, Mongo, ES, API, Dashboard, RAG, and E2E end-to-end regression.
   - Run complete end-to-end acceptance verification and generate final report suite.
