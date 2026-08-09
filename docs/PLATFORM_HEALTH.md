# Platform Health & Observability Center Specification

## 1. Business & Product Purpose
The **Platform Health & Observability Center** serves as the central SRE control room for the News Intelligence Platform. It provides real-time infrastructure, pipeline, data quality, and service observability across Kafka, MongoDB, Elasticsearch, FastAPI, Ingestion, Consumer, Orchestrator, Dashboard, and NLP stages.

---

## 2. Core Questions Answered
1. **"IS MY NEWS INTELLIGENCE PLATFORM ACTUALLY WORKING?"** (Overall System Status Banner: `OPERATIONAL`, `DEGRADED`, `CRITICAL`, `UNKNOWN`)
2. **"What is the health of each microservice & database?"** (Service Grid displaying live response latency ms and status)
3. **"How are news signals flowing through the pipeline?"** (Visual End-to-End Realtime Pipeline Map)
4. **"What is the Kafka streaming status & consumer lag?"** (Topic offsets, consumer lag count, and group status `news-realtime-consumer-v3`)
5. **"What is the MongoDB data quality & coverage %?"** (Title %, Content %, Category %, Sentiment %, Keywords %, Entities %, Embeddings %)
6. **"What is the Elasticsearch index coverage gap?"** (ES document count, MongoDB total count, Index Coverage Gap %, BM25 status, Dense Vector 384d status)
7. **"What is the freshness of the four news portals?"** (Latest article timestamp & freshness status per publisher for *Economic Times*, *The Hindu*, *Indian Express*, *Hindustan Times*)

---

## 3. Architecture & Data Flow

```
NEWS SOURCES (ET, The Hindu, IE, HT)
     ↓ (Source Freshness Telemetry)
INGESTION SERVICE (PID Check + Logs)
     ↓
KAFKA (Topic Offsets + Consumer Lag)
     ↓
REALTIME CONSUMER (Consumer Group v3)
     ↓
MONGODB (Data Quality Coverage % + Queue Telemetry)
     ↓
PIPELINE ORCHESTRATOR (Lease & Queue Monitor)
     ↓
NLP STAGES (Stage Flow Counts)
     ↓
ELASTICSEARCH (Index Coverage Gap % + Vector 384d Readiness)
     ↓
FASTAPI (Endpoint Latency Matrix)
     ↓
DASHBOARD (SRE Control Room Observability Workspace)
```

---

## 4. API Endpoints Contract

1. `GET /api/system/telemetry`
   - Returns complete telemetry payload: `overall_status`, `services` grid, `kafka` metrics, `mongodb` data quality %, `elasticsearch` coverage gap, `pipeline` stage flow, `source_freshness`, `api_latency`, and `active_alerts`.

---

## 5. UI/UX Workflow & Components

1. **Header & Auto-Refresh Controls**: Timestamp indicator + Auto-refresh toggle + `[REFRESH NOW]` button.
2. **Overall System Status Banner**: Large banner displaying real state (`● SYSTEM OPERATIONAL`, `⚠ SYSTEM DEGRADED`, `🔴 SYSTEM CRITICAL`, `⚪ STATUS UNKNOWN`). Eliminates contradictory UI states!
3. **Service Health Grid Cards**: Cards for MongoDB, Kafka, Elasticsearch, FastAPI, Ingestion, Consumer, Orchestrator, Dashboard with response latency ms and status badges.
4. **End-to-End Visual Realtime Pipeline Map**: Visual topology nodes representing dataset flow.
5. **Dedicated Kafka Streaming & Consumer Lag**: Log end offset, committed offset, consumer lag count, and consumer group health.
6. **MongoDB Data Quality & Coverage %**: Data quality breakdown bar gauges for Title %, Content %, NLP %, Embedding %.
7. **NLP Pipeline Stage Flow & Queue Telemetry**: Stage bar chart, pending queue, completed queue, failed queue, and stale lease detection.
8. **Elasticsearch Index & Coverage Gap**: ES count, MongoDB count, Index Coverage Gap %, BM25 status, 384d Vector status.
9. **Publisher Source Freshness Breakdown**: Last article timestamp & freshness tag for each newspaper.
10. **FastAPI Latency & Active Alerts Log**: Endpoint latency matrix & system alert logs (`INFO`, `WARNING`, `CRITICAL`).
