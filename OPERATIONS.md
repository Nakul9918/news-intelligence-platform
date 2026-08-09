# News Intelligence Platform — Operational Guide & CLI Reference

**Version:** 3.0 (Production)  
**Last Updated:** August 9, 2026  

---

## 1. Quick Start & Service Control

### Start All Services Automatically
```powershell
.\start_project.ps1
```

### Stop All Services Gracefully
```powershell
.\stop_project.ps1
```

---

## 2. Running Individual Services

### Streamlit Command Center UI (Port 8501)
```powershell
python run_dashboard.py
```
> 🌐 Access in browser: [http://localhost:8501](http://localhost:8501)

### FastAPI Backend Server (Port 8000)
```powershell
python run_api.py
```
> 🌐 Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 3. Historical News Backfill Controller

Run controlled historical news ingestion with rate-limiting, Data Quality validation, and checkpoint resume:

```powershell
python historical/backfill_manager.py --source economic_times --from 2025-08-01 --to 2026-08-09 --rate-limit 15 --batch-size 500
```

### Options:
- `--source`: Target news source (`economic_times`, `the_hindu`, `indian_express`, `hindustan_times`, `all`).
- `--from`: Start date (`YYYY-MM-DD`).
- `--to`: End date (`YYYY-MM-DD`).
- `--rate-limit`: Max articles inserted per second.
- `--batch-size`: Max articles per processing cycle.

---

## 4. Master Automated Test Suite

Run the full automated test suite covering Unit, Collectors, MongoDB, Data Quality, Extractor, NLP, Elasticsearch, API, RAG, and End-to-End Regression:

```powershell
python run_all_tests.py
```
*Or via PowerShell:*
```powershell
.\run_all_tests.ps1
```

---

## 5. Troubleshooting & Health Verification

### Check Port Availability
```powershell
python -c "import socket; print([(p, socket.socket().connect_ex(('localhost', p)) == 0) for p in [27017, 9092, 9200, 8000, 8501]])"
```

### Check MongoDB Collection Statistics
```powershell
python check_mongo.py
```
