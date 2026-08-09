# News Intelligence Platform — System Architecture Specification

**Version:** 3.0 (Company-Grade Real-Time + Historical)  
**Last Updated:** August 9, 2026  

---

## 1. Executive Architecture Overview

The **News Intelligence Platform** is a decoupled, multi-stage real-time and historical news ingestion, processing, intelligence, and search platform. It processes streams from trusted publishers (Economic Times, The Hindu, Indian Express, Hindustan Times), applies data quality validation, extracts content via a 3-tier fallback engine, runs a 6-stage NLP pipeline (Summary, Sentiment, Category, Keywords, NER, 384-dim Dense Embeddings), indexes enriched docs into Elasticsearch, and exposes APIs and an auto-refreshing Streamlit Command Center UI.

```
+-----------------------------------------------------------------------------------------+
|                                    NEWS SOURCES                                         |
|            Economic Times | The Hindu | Indian Express | Hindustan Times                |
+-----------------------------------------------------------------------------------------+
                    |                                           |
                    | (Realtime Feed)                           | (Historical Backfill)
                    v                                           v
+---------------------------------------+   +---------------------------------------+
|        REALTIME INGESTION SERVICE     |   |      HISTORICAL BACKFILL MANAGER       |
|    Deduplication -> SHA256 article_id  |   | Rate Limited -> Resumable Checkpoint  |
+---------------------------------------+   +---------------------------------------+
                    |                                           |
                    +--------------------+----------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------------+
|                                   DATA QUALITY GATE                                     |
|               Score 0-100 -> Invalid/Short -> Quarantine Collection                     |
+-----------------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------------+
|                                  KAFKA / MONGO BUS                                      |
|             Topic: news-topic-v2 | Collection: news_db.realtime_articles             |
+-----------------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------------+
|                                REALTIME NLP ORCHESTRATOR                                |
|    Fetch PENDING -> 3-Tier Extractor -> Clean -> BART Summary -> FinBERT Sentiment ->   |
|    Zero-Shot Category -> KeyBERT -> SpaCy NER -> 384-Dim Embeddings -> Model Caching   |
+-----------------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------------+
|                              ELASTICSEARCH HYBRID INDEX                                 |
|            Index: news_articles | BM25 Text Search + 384-Dim KNN Vector               |
+-----------------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------------+
|                                    FASTAPI BACKEND                                      |
|     Host: http://localhost:8000 | Search, Analytics, Time Machine, RAG Endpoints     |
+-----------------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------------+
|                              STREAMLIT COMMAND CENTER UI                                |
|                 Auto-refresh UI | Telemetry | Search | RAG | Port 8501                 |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Core Service Components

1. **Ingestion & Data Quality Gate (`ingestion_service.py`, `qc/quality_gate.py`)**
   - SHA256 URL hashing prevents duplicate document insertion.
   - Quality score (0–100) evaluation routes invalid or low-quality articles to `news_db.quarantine_articles`.

2. **Historical Backfill Manager (`historical/backfill_manager.py`)**
   - Controlled historical import with CLI options (`--source`, `--from`, `--to`, `--rate-limit`, `--resume`).
   - Checkpointing via `news_db.ingestion_state`.
   - Realtime pipeline priority throttling (auto-pauses historical workers if pending realtime queue > 200).

3. **Multi-Stage Content Extractor & Cleaner (`historical_crawlers/extractor.py`, `nlp/content_cleaner.py`)**
   - 3-stage fallback: `newspaper3k` -> `trafilatura` -> `BeautifulSoup4`.
   - Strips boilerplate, navigation menus, ads, and invalid HTML formatting.

4. **NLP Processing & Model Singleton Caching (`nlp/`)**
   - Abstractive Summarization (BART-large-cnn)
   - Sentiment Analysis (FinBERT / Twitter-RoBERTa)
   - Zero-Shot Category Classification (MNLI)
   - Keyword Extraction (KeyBERT / TF-IDF)
   - Named Entity Recognition (SpaCy en_core_web_sm)
   - Dense Vector Embeddings (SentenceTransformers `all-MiniLM-L6-v2`, 384 dimensions)
   - Global model caching prevents PyTorch re-initialization overhead.

5. **Elasticsearch Indexer & Hybrid Search (`elasticsearch_indexer/indexer.py`)**
   - Combines BM25 term relevance with cosine-similarity KNN vector search.

6. **FastAPI Backend & Intelligence Engines (`api/routes.py`, `api/intelligence_engine.py`)**
   - Endpoints for Top News, News Time Machine, Cross-Source Comparison, Event Timelines, Current Affairs, and Agentic RAG.

7. **Streamlit Command Center (`dashboard.py`)**
   - Dark theme, high-density UI with real-time telemetry monitors, search controls, and live stream views.
