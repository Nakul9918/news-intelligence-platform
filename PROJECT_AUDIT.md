# News Intelligence Platform — Comprehensive Project Audit

**Project Root:** `d:\project\news-intelligence-platform\project`  
**Date:** August 8, 2026  
**Status:** Audit Completed (Phase A)

---

## 1. Current Architecture & System Overview

The **Real-Time News Intelligence Platform** is designed to continuously ingest articles from trusted Indian & global news sources, stream them through Apache Kafka, store them in MongoDB, extract full body content, clean the text, perform multi-stage NLP (Summary, Sentiment, Category, Keywords, NER, Sentence Embeddings), index the enriched data in Elasticsearch, and expose it via a FastAPI backend to an auto-updating Streamlit / Web Dashboard.

```
+-----------------------------------------------------------------------------------------+
|                                    NEWS SOURCES                                         |
|                 Economic Times | The Hindu | Indian Express | Hindustan Times           |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                REALTIME INGESTION SERVICE                               |
|              Periodic Feed/Sitemap Polling -> Deduplication -> Article ID                |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                     APACHE KAFKA                                        |
|                          Topic: news-topic-v2 (Partition 1)                             |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                  REALTIME CONSUMER                                      |
|                  Consumes Kafka Messages -> Writes raw doc to MongoDB                   |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                  MONGODB DATABASE                                       |
|                  DB: news_db | Collection: realtime_articles (10,112 docs)         |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                REALTIME NLP WORKER                                      |
|  Fetch PENDING -> Extract Content -> Clean -> Summary -> Sentiment -> Category ->      |
|  Keywords -> NER -> Embeddings -> Update MongoDB -> Index in Elasticsearch             |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                    ELASTICSEARCH                                        |
|                     Host: http://localhost:9200 | Index: news_articles              |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                    FASTAPI BACKEND                                      |
|                   Host: http://localhost:8000 | Endpoints: /search, /stats           |
+-----------------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                REAL-TIME DASHBOARD                                      |
|                       Streamlit / SSE Auto-updating UI (Port 8501)                      |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Working Components

1. **Kafka Cluster & Topic Integration:**
   - Kafka broker operating on `localhost:9092`.
   - Topic `news-topic-v2` verified working with partition count 1 and end offset ~125,335.
   - Message serialization and producer connectivity using `kafka-python 2.2.15` confirmed functional.

2. **MongoDB Database Layer:**
   - Mongo URI: `mongodb://localhost:27017`
   - Database: `news_db`, Collection: `realtime_articles`.
   - Currently holds **10,112** documents.

3. **News Source Collectors (Sitemaps & RSS):**
   - **Economic Times Loader** (`bootstrap/realtime_bootstrap/et_loader.py`): Working (over 10,000 articles collected).
   - **Hindustan Times Loader** (`bootstrap/realtime_bootstrap/hindustantimes_loader.py`): Working (3,741 historical articles collected).
   - **Indian Express Loader** (`bootstrap/realtime_bootstrap/indianexpress_loader.py`): Working.
   - **The Hindu Loader** (`bootstrap/realtime_bootstrap/thehindu_loader.py`): Sitemap collector works (23 articles matching Aug 1–7 from the recent news sitemap). Realtime RSS feeds available.

4. **Multi-Stage Article Extractor (`historical_crawlers/extractor.py`):**
   - 3-tier fallback strategy: Newspaper3k -> Trafilatura -> BeautifulSoup4.
   - Handles paywalls, invalid content filtering, and cleans whitespace.

5. **NLP Suite (`nlp/` directory):**
   - [nlp/content_cleaner.py](file:///d:/project/news-intelligence-platform/project/nlp/content_cleaner.py): Robust text cleaning and boilerplate removal.
   - [nlp/summarizer.py](file:///d:/project/news-intelligence-platform/project/nlp/summarizer.py): BART/T5 abstractive summarizer.
   - [nlp/sentiment.py](file:///d:/project/news-intelligence-platform/project/nlp/sentiment.py): FinBERT / VADER / Transformer sentiment analyzer.
   - [nlp/category_classifier.py](file:///d:/project/news-intelligence-platform/project/nlp/category_classifier.py): Zero-shot / BART category classification.
   - [nlp/keyword_extractor.py](file:///d:/project/news-intelligence-platform/project/nlp/keyword_extractor.py): KeyBERT & TF-IDF keyword extraction.
   - [nlp/ner.py](file:///d:/project/news-intelligence-platform/project/nlp/ner.py): SpaCy & Transformer Named Entity Recognition.
   - [nlp/embeddings.py](file:///d:/project/news-intelligence-platform/project/nlp/embeddings.py): SentenceTransformers embedding generation.

---

## 3. Broken / Partial Components

1. **Missing Content & Titles in Harvested Articles:**
   - Many MongoDB articles collected via RSS/sitemaps currently have `title: ""`, `content: ""`, `clean_content: ""`.
   - *Fix:* Downstream extractor must retrieve full article text from `article["link"]` using [historical_crawlers/extractor.py](file:///d:/project/news-intelligence-platform/project/historical_crawlers/extractor.py) before triggering NLP enrichment.

2. **Realtime Consumer Import Error:**
   - Running `python .\streaming\realtime_consumer.py` yields `ModuleNotFoundError: No module named 'config'`.
   - *Fix:* Standardize package execution (`python -m streaming.realtime_consumer`) or adjust absolute imports referencing root `config.py`.

3. **Missing Elasticsearch Indexer:**
   - [realtime_pipeline/elasticsearch_indexer.py](file:///d:/project/news-intelligence-platform/project/realtime_pipeline/elasticsearch_indexer.py) is currently empty (0 bytes).
   - [realtime_pipeline/realtime_nlp_pipeline.py](file:///d:/project/news-intelligence-platform/project/realtime_pipeline/realtime_nlp_pipeline.py) does not index articles to Elasticsearch after NLP completion.
   - *Fix:* Implement full Elasticsearch mapping, indexing, and bulk refresh logic into [realtime_pipeline/elasticsearch_indexer.py](file:///d:/project/news-intelligence-platform/project/realtime_pipeline/elasticsearch_indexer.py).

4. **Manual Orchestration Requirement:**
   - System currently requires manually starting producers, consumers, and NLP processors in separate terminal windows.
   - *Fix:* Build an automated daemon/service structure and automated startup/shutdown scripts (`start_project.ps1`, `stop_project.ps1`).

5. **Static Dashboard without Auto-Update:**
   - [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py) is currently a minimal 38-line Streamlit script targeting the wrong collection (`articles` instead of `realtime_articles`) without auto-refresh, sentiment analytics, or temporal trends.
   - *Fix:* Build a feature-complete, auto-refreshing UI connected to MongoDB/Elasticsearch/FastAPI.

---

## 4. Duplicate & Overlapping Components Assessment

| Directory / File | Status | Audit Finding & Action |
| :--- | :--- | :--- |
| `bootstrap/realtime_bootstrap/` | **ACTIVE** | Main source loaders (ET, HT, IE, The Hindu) & producer. Preserve and refactor into permanent ingestion service. |
| `crawler/rss_crawler.py` | **ACTIVE** | Light RSS feed parser for live updates. Integrate into continuous ingestion daemon. |
| `streaming/realtime_consumer.py` | **ACTIVE** | Main Kafka consumer. Fix import bugs and bind to worker pool. |
| `realtime_pipeline/realtime_nlp_pipeline.py` | **ACTIVE** | Core pipeline execution. Add Elasticsearch indexing hook. |
| `historical_crawlers/extractor.py` | **ACTIVE** | Master extraction utility. Reused by NLP worker. |
| `nlp/` | **ACTIVE** | Contains all core NLP algorithms. Preserve completely. |
| `backend/` | **ACTIVE** | FastAPI app and routes. Update `search_service.py` to route search queries to Elasticsearch. |
| `bootstrap/common_collector.py` | **ACTIVE** | Reused sitemap parser. Preserve. |
| `pipeline.py` / `pipeline_v2.py` | **OVERLAPPING** | Legacy pipeline wrappers. Keep intact until `realtime_nlp_pipeline.py` is fully verified. |
| `historical_crawlers/*_old.py` | **OBSOLETE** | Old backup scripts (e.g. `historical_content_extractor_old.py`). Flagged for eventual removal in Phase R. |

---

## 5. Recommended Final Architecture & File Mapping

```
d:\project\news-intelligence-platform\project\
├── config.py                            # Primary configuration parameters
├── start_project.ps1 / stop_project.ps1  # Master automated startup/shutdown scripts
├── ingestion_service.py                 # Continuous 60s background news collector & Kafka producer
├── streaming/
│   ├── producer.py                      # Kafka producer wrapper
│   └── realtime_consumer.py             # Kafka -> MongoDB ingestion consumer
├── realtime_pipeline/
│   ├── realtime_nlp_pipeline.py         # Content Extraction -> NLP -> Mongo Status Update
│   └── elasticsearch_indexer.py         # MongoDB COMPLETED -> Elasticsearch indexer
├── nlp/                                 # Modular NLP engines (Cleaner, Summary, Sentiment, Category, Keywords, NER, Embeddings)
├── backend/                             # FastAPI service (Routes: /search, /stats, /latest)
├── dashboard.py                         # Streamlit live intelligence dashboard with auto-polling
├── PROJECT_AUDIT.md                     # System architecture audit document
└── PROJECT_PROGRESS.md                  # Phase tracking and verification progress
```

---

## 6. Verification & Preservation Directives

- **Files to Preserve:** All active collectors, `config.py`, `historical_crawlers/extractor.py`, `nlp/*`, `backend/*`, `streaming/*`, `realtime_pipeline/*`.
- **Safety Rule:** No files will be deleted until Phase R (Cleanup), following explicit reference verification.
