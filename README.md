# Real-Time News Intelligence Platform

A company-grade, end-to-end system for collecting, processing, enriching, indexing, and analyzing news data from major media outlets in near real-time. Featuring a multi-stage NLP pipeline, hybrid vector & keyword search, temporal analytics engine, Agentic AI RAG grounding, and an interactive Streamlit Command Center.

---

##  Key Features & Architecture

### 1. Multi-Source Ingestion & Data Quality Gate
* **Automated News Crawling**: Supports continuous crawling from major news outlets (Economic Times, The Hindu, Indian Express, Hindustan Times).
* **Data Quality (DQ) Gate**: Scores incoming articles (0–100) based on title validity, URL structure, publication timestamps, and content body.
* **Quarantine Routing**: Low-quality or incomplete articles are safely routed to a quarantine database collection without breaking the real-time processing pipeline.

### 2. Multi-Task NLP Enrichment Engine
* **384-Dim Dense Vector Embeddings**: Powered by SentenceTransformers (`all-MiniLM-L6-v2`) for semantic similarity and RAG grounding.
* **Named Entity Recognition (NER)**: Extracts key entities (Persons, Organizations, Locations, Products).
* **Automated Categorization & Sentiment**: Classifies articles into 12 core categories (Politics, Business, Tech, Sports, etc.) and assigns sentiment polarity with confidence scores.

### 3. Dual Storage & Fallback Architecture
* **Primary Storage**: MongoDB for document persistence, metadata tracking, and ingestion state checkpoints.
* **Search Layer**: Elasticsearch for keyword & vector index queries, with seamless automatic fallback to MongoDB vector & keyword search when ES is offline.
* **Streaming Layer**: Kafka pipeline with auto-recovery and direct database persistence fallback.

### 4. FastAPI REST Services (`http://localhost:8000`)
* Full OpenAPI/Swagger endpoints for querying articles, entity intelligence, source coverage analytics, RAG Q&A, and system telemetry.

### 5. Streamlit Command Center (`http://localhost:8501`)
Includes 12 dedicated interactive workspaces:
* **Live Ingestion Feed**: Real-time ticker and newly arrived articles.
* **Temporal Analytics**: Time-series volume trends and category velocity.
* **4-Newspaper Coverage Comparison**: Cross-source bias and volume breakdown.
* **Entity Intelligence Workspace**: Entity graph co-occurrences and sentiment distribution.
* **Agentic AI & RAG Grounding**: Natural language query answering with source citations.
* **Historical Time Machine**: Archived news retrieval and trend comparison.
* **System Telemetry & Health**: Pipeline status, database counts, and component metrics.

---

## 🛠️ Technology Stack

* **Language**: Python 3.12
* **Backend API**: FastAPI, Uvicorn
* **Frontend UI**: Streamlit, Plotly, HTML/CSS Dark Theme
* **NLP & AI**: SentenceTransformers, PyTorch, Transformers, RAG Grounding Engine
* **Databases & Brokers**: MongoDB, Kafka, Elasticsearch
* **Data Quality & Testing**: Custom DQ Rules Engine, Master Automated Test Suite (13 Suites)

---

## 🚀 Quick Start

### Prerequisites
* Windows OS / Linux / macOS
* Python 3.12+ installed
* MongoDB running on `localhost:27017`

### 1. One-Command Startup
To run all infrastructure checks, launch background daemons (Ingestion, Consumer, Orchestrator, FastAPI API, Streamlit Dashboard), execute:

```powershell
.\start_project.ps1
```

Once launched:
* **Streamlit Command Center**: Navigate to `http://localhost:8501`
* **FastAPI Docs**: Navigate to `http://localhost:8000/docs`

### 2. Graceful Shutdown
To cleanly terminate all daemons and free reserved ports (`8000`, `8501`):

```powershell
.\stop_project.ps1
```

### 3. Running Automated Test Suite
Run the 13-suite automated regression test runner:

```powershell
python run_all_tests.py
```

---

## 📁 Repository Structure

```
news-intelligence-platform/
└── project/
    ├── ai/                         # Agentic AI & RAG grounding modules
    ├── api/                        # FastAPI REST API implementation & routes
    ├── cleaner/                    # Content extraction & text sanitization
    ├── consumer/                   # Kafka stream consumer modules
    ├── crawler/                    # Live news scrapers and RSS collectors
    ├── historical/                 # Backfill manager & archive storage
    ├── nlp/                        # Sentence Transformers, NER, sentiment, category models
    ├── qc/                         # Data Quality Gate & quarantine engine
    ├── realtime_pipeline/          # Real-time event orchestrator & pipeline lifecycle
    ├── streaming/                  # Kafka producer & consumer handlers
    ├── dashboard.py                # Streamlit News Intelligence Command Center UI
    ├── run_api.py                  # FastAPI server entrypoint (port 8000)
    ├── run_dashboard.py            # Streamlit launcher (port 8501)
    ├── run_all_tests.py            # Master Automated Test Suite (13 Suites)
    ├── check_infrastructure.py     # Infrastructure health check validator
    ├── start_project.ps1           # One-command startup script
    └── stop_project.ps1            # Graceful shutdown script
```

---

## 🧪 Testing & Verification

The platform is validated by a 13-suite automated test matrix verifying end-to-end integrity:
1. **Config & Package Imports**
2. **Data Quality Gate & Quarantine**
3. **News Collectors Test**
4. **MongoDB Idempotent Upsert & Schema**
5. **Extraction & Content Cleaning**
6. **NLP Suite & 384-Dim Embeddings**
7. **Historical Intelligence Engine**
8. **FastAPI REST Endpoints**
9. **Temporal Analytics Engine**
10. **Agentic AI & RAG Grounding**
11. **End-to-End System Pipeline**
12. **Historical Backfill System**
13. **Dashboard Offline Mode & Imports**

---

## 📄 License
Internal Production Release — All Rights Reserved.
