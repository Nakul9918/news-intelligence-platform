# Final System Architecture & Platform Documentation

## Executive Overview
The **News Intelligence Platform** is an enterprise-grade, real-time news monitoring, analysis, search, and retrieval system. It automatically ingests live RSS news feeds from major Indian media outlets (*Economic Times*, *The Hindu*, *Indian Express*, *Hindustan Times*), streams data through Apache Kafka, persists raw and enriched documents to MongoDB, executes a 6-stage NLP enrichment pipeline, indexes documents into Elasticsearch 8.17.2 with 384-dimensional dense vector mappings, computes temporal analytics & trend intelligence, and exposes an Agentic RAG AI Assistant and Streamlit Live Dashboard.

---

## Final Architecture Diagram

```
                 NEWS SOURCES
         (ET, The Hindu, IE, HT)
                    │
                    ▼
       AUTOMATIC INGESTION SERVICE
        (Crawler & De-duplication)
                    │
                    ▼
          KAFKA: news-topic-v2
                    │
                    ▼
         REALTIME KAFKA CONSUMER
     (news-realtime-consumer-v3)
                    │
                    ▼
       MONGODB: news_db.realtime_articles
                    │
                    ▼
         PIPELINE ORCHESTRATOR
   (Lease Management & State Recoverability)
                    │
                    ├──────────► EXTRACTION (3-Stage Fallback)
                    ├──────────► CLEANING (Ad/Noise Removal)
                    └──────────► MULTI-STAGE NLP PIPELINE
                                  ├── 1. Summary (BART-large-cnn)
                                  ├── 2. Sentiment (RoBERTa-base)
                                  ├── 3. Category (Zero-Shot DeBERTa)
                                  ├── 4. Keywords (KeyBERT / TF-IDF)
                                  ├── 5. NER (spaCy en_core_web_sm)
                                  └── 6. Embeddings (all-MiniLM-L6-v2)
                    │
                    ▼
       ELASTICSEARCH: news_articles
      (BM25 Text + 384-dim Dense Vector KNN)
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
 FASTAPI BACKEND          TEMPORAL ANALYTICS
   (Port 8000)             (Volume & Spikes)
         │                     │
         └──────────┬──────────┘
                    ▼
             AGENTIC RAG ENGINE
      (Query Router & Citation Tracking)
                    │
                    ▼
         STREAMLIT DASHBOARD
        (Live Interactive UI - Port 8501)
```

---

## Component Roles & Technology Stack

| Layer | Technology | Key Responsibilities |
|---|---|---|
| **Ingestion** | Python / `feedparser` | Auto-discovers new RSS feeds, computes SHA256 article hashes, and prevents duplicate publishing. |
| **Streaming** | Apache Kafka 3.x | Decouples ingestion from ingestion processing via `news-topic-v2` topic. |
| **Raw Storage** | MongoDB 6.x | Serves as authoritative document database (`news_db.realtime_articles`) with unique `article_id` index. |
| **Orchestration** | Python Daemon | Manages worker leases, atomic MongoDB status updates, stale lock recovery, and ES syncing. |
| **NLP Pipeline** | PyTorch, Transformers, spaCy | Executes 6 NLP enrichment modules (Summary, Sentiment, Category, Keywords, NER, 384-dim Embeddings). |
| **Search Engine** | Elasticsearch 8.17.2 | Provides BM25 keyword search, 384-dimensional dense vector KNN search, and Hybrid RRF search. |
| **Analytics** | MongoDB Aggregations | Calculates time-bucketed news volume, source timelines, sentiment shifts, spike deviations, and cross-source topic signals. |
| **Agentic AI** | Gemini 2.5 Flash + Grounded RAG | Classifies user intent, selects tools deterministically, builds context, and produces grounded answers with citations. |
| **API** | FastAPI / Uvicorn | Exposes REST endpoints (`/health`, `/api/metrics`, `/api/live-feed`, `/api/search`, `/api/analytics/*`, `/api/ai/ask`). |
| **UI** | Streamlit | Real-time interactive dashboard with live news feed, temporal analytics, search workspace, and AI Assistant. |

---

## One-Command Management
- **Startup:** `.\start_project.ps1` — Automatically verifies infrastructure services, creates missing topics/indexes, and launches all 5 background daemons.
- **Shutdown:** `.\stop_project.ps1` — Safely terminates background processes and cleans port bindings (ports 8000 & 8501).
