# ♻️ Sustainability & Risk Analysis Report — News Intelligence Platform

**Document Version**: 25.0  
**Date**: August 9, 2026  
**Scope**: Architecture Sustainability, Resource Sizing, Backpressure Control, Staged Backfill Strategy, and Risk Matrix

---

## 1. System Architecture & Resource Footprint

The platform architecture is designed for continuous, multi-publisher news processing across streaming and batch workflows:

```
[LIVE RSS SOURCES] ──> Ingestion Service (PID 16132) ──> Mongo Fallback / Kafka Bus
                                                                  │
[HISTORICAL SITEMAPS] ──> Backfill Manager (Rate-Limited 2.0/s) ──┤
                                                                  ▼
                                                      MongoDB (news_db.realtime_articles)
                                                                  │
                                                      Pipeline Orchestrator (PID 21268)
                                                                  │
                                                      6-Stage NLP Pipeline
                                                                  │
                                                      Elasticsearch (news_articles index)
                                                                  │
                                                      FastAPI Backend Server (PID 24776)
                                                                  │
                                                      Streamlit UI (PID 14068)
```

---

## 2. Resource Capacity & Scaling Estimates

| Corpus Scale | Document Count | MongoDB Storage | Elasticsearch Index | NLP Processing Time | Storage Cost (Est.) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (Current Corpus)** | **21,713 docs** | **~45 MB** | **~65 MB** | Complete (455 enriched + 20,438 embeddings) | Baseline |
| **Stage 2 (1-Year Corpus)** | **~100,000 docs** | **~210 MB** | **~320 MB** | ~14 Hours (Async background worker) | Minimal (~$5/mo) |
| **Stage 3 (2-Year Corpus)** | **~250,000 docs** | **~520 MB** | **~800 MB** | ~35 Hours (Async background worker) | Low (~$15/mo) |
| **Stage 4 (3-Year Corpus)** | **~500,000 docs** | **~1.05 GB** | **~1.60 GB** | ~70 Hours (Async background worker) | Low (~$30/mo) |

---

## 3. Backpressure & Throttling Controls

To prevent historical backfills from overwhelming the live news stream:
1. **Real-time Pipeline Priority**: Real-time articles ingested via `ingestion_service.py` take processing precedence.
2. **Configurable Backpressure Threshold**: `historical/backfill_manager.py` monitors the `PENDING` queue count (`max_pending = 50,000`). If the queue exceeds the safe threshold, backfill crawling pauses automatically.
3. **Rate Limiting**: Historical sitemap crawling defaults to `--rate-limit 2.0` (2 articles/sec) to avoid triggering CDN blocks or 403 errors on publisher websites.

---

## 4. Staged Historical Backfill Roadmap

> [!IMPORTANT]
> **Capacity Rule**: Downloading massive historical datasets must follow a staged approach to ensure database indexes, RAM, and vector search indices remain responsive.

- **Stage 1 (Current Corpus - Active)**: Maintain current 21k articles (August 2026 + July 2026).
- **Stage 2 (Previous 6 Months)**: Backfill January 2026 – June 2026 (~50,000 articles).
- **Stage 3 (Previous 1 Year)**: Backfill Full Year 2025 (~100,000 articles).
- **Stage 4 (Multi-Year Archive)**: Backfill 2023 – 2024 (~300,000 articles).

---

## 5. Comprehensive Risk Matrix

| Risk ID | Risk Description | Severity | Current Mitigation | Long-Term Recommendation | Implementation Cost |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **R-01** | Publisher CDN 403 Block on Sitemap Crawl | **MEDIUM** | 3-tier cascade (`newspaper3k` ➔ `trafilatura` ➔ `BS4`) + User-Agent rotation. | Implement proxy rotation pool for high-volume backfill. | LOW |
| **R-02** | MongoDB Unindexed Memory Growth | **HIGH** | Indexes created on `article_id`, `link`, `created_at`, `source.name`, `category.label`. | Monitor WiredTiger cache size; set TTL on raw sitemap logs. | LOW |
| **R-03** | PyTorch NLP Model GPU/CPU Memory Leak | **MEDIUM** | Global model caching singleton in `nlp/models.py`. | Run NLP orchestrator in batch cycles of 50 items with `gc.collect()`. | LOW |
| **R-04** | Elasticsearch Transport Down | **LOW** | Direct MongoDB Keyword + 384-dim Vector KNN fallback in API & Dashboard. | Maintain cluster auto-restart daemon script. | LOW |
| **R-05** | Kafka Broker Connection Failure | **LOW** | Direct MongoDB idempotent upsert fallback in `ingestion_service.py`. | Standardize Kafka local broker startup script. | LOW |
