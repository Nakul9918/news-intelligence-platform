# News Intelligence Platform — Testing & Quality Assurance Specification

**Version:** 3.0 (Production)  
**Last Updated:** August 9, 2026  

---

## 1. Test Suite Overview

The test architecture consists of 11 distinct test modules coordinated by `run_all_tests.py` and `run_all_tests.ps1`.

| Test Module | Coverage Scope | Command |
| :--- | :--- | :--- |
| **1. Config & Package Imports** | Verifies `config.py` tokens, `.env` settings, and module imports. | `python -c "import config..."` |
| **2. Data Quality Gate & Quarantine** | Tests 0–100 scoring, rule checks, and quarantine routing in `qc/quality_gate.py`. | `python -c "from qc.quality_gate..."` |
| **3. News Collectors Test** | Verifies RSS/sitemap parsing across ET, The Hindu, IE, and HT. | `python test_collectors.py` |
| **4. MongoDB Persistence & Schema** | Tests unique `article_id` SHA256 keying and idempotent upserts. | `python test_consumer_mongo.py` |
| **5. Extraction & Cleaning** | Tests 3-stage fallback extractor (`newspaper3k` -> `trafilatura` -> `BS4`). | `python test_extraction_cleaning.py` |
| **6. NLP Suite & 384-Dim Embeddings** | Tests BART summarization, FinBERT sentiment, Zero-Shot, KeyBERT, NER, and vector embeddings. | `python test_nlp_pipeline.py` |
| **7. Historical Intelligence Engine** | Tests Top News, Time Machine, Cross-Source Comparison, and Current Affairs logic. | `python -c "from api.intelligence_engine..."` |
| **8. FastAPI REST Endpoints** | Tests `/health`, `/search`, `/api/metrics`, and analytics endpoints. | `python test_dashboard_api.py` |
| **9. Temporal Analytics Engine** | Tests volume trend aggregations and time window metrics. | `python test_temporal_analytics.py` |
| **10. Agentic AI & RAG Grounding** | Tests RAG intent routing, context assembly, and hallucination prevention. | `python test_agentic_rag.py` |
| **11. End-to-End System Pipeline** | Executes complete pipeline flow from ingestion to index. | `python test_end_to_end_flow.py` |

---

## 2. Test Execution Command

Run the entire master regression suite:

```powershell
python run_all_tests.py
```
