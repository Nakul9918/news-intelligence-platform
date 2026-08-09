# 🐛 Master Error & Bug Fix Report — News Intelligence Platform

**Document Version**: 25.0  
**Date**: August 9, 2026  
**Scope**: Resolved System Errors, Contract Mismatches, Exception Handling, and Defensive Schema Hardening

---

## 1. Resolved System Errors & Bug Fix Log

### ERROR 01: Pandas DataFrame `KeyError: ['mentions', 'growth']`
* **Component**: Dashboard / Analytics Endpoint (`/api/analytics/keywords`)
* **File**: [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py)
* **Symptom**: Unhandled Streamlit exception `KeyError: ['mentions', 'growth'] not in index` when rendering Emerging Keywords dataframe.
* **Root Cause**: The API endpoint returned key `"recent_mentions"`, whereas `dashboard.py` expected `"mentions"`.
* **Fix**: Updated dataframe column mapping in `dashboard.py` to `df[["keyword", "recent_mentions", "growth_pct"]]` and wrapped with defensive dictionary key checking using `first_present()`.
* **Regression Test**: Verified in `test_dashboard_api.py` and `run_all_tests.py`.

---

### ERROR 02: MongoDB Regex Syntax Error (`Location51091`)
* **Component**: Universal Search, Time Machine, and Story Timeline
* **Files**: [api/intelligence_helpers.py](file:///d:/project/news-intelligence-platform/project/api/intelligence_helpers.py), [api/routes.py](file:///d:/project/news-intelligence-platform/project/api/routes.py)
* **Symptom**: MongoDB raised `pymongo.errors.OperationFailure: Location51091 (missing terminating ] for character class)` when users entered special characters (e.g. `!@#$%^&*()`, `[crime]`, `Modi + BJP`).
* **Root Cause**: Search strings were interpolated directly into MongoDB `$regex` dictionary without regex metacharacter escaping.
* **Fix**: Implemented `safe_regex(text: str)` helper utilizing `re.escape()` across all query builders.
* **Regression Test**: Verified in `test_edge_cases.py` (Test 1, Test 3, Test 4, Test 5).

---

### ERROR 03: High Dashboard Refresh Latency (`ttl=1`)
* **Component**: Streamlit UI Data Layer
* **File**: [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py)
* **Symptom**: Dashboard felt slow and lagged during user typing or auto-refresh ticks.
* **Root Cause**: `fetch_api()` was decorated with `@st.cache_data(ttl=1)`, forcing full network roundtrips and MongoDB aggregation re-executes every 1 second.
* **Fix**: Updated `@st.cache_data(ttl=15)` in `dashboard.py`. Navigation and interaction became instantaneous while keeping data fresh every 15 seconds.
* **Regression Test**: Verified via manual interaction and `test_frontend_dashboard.py`.

---

### ERROR 04: UI Workspace Bleeding on Offline Telemetry
* **Component**: System / Pipeline Workspace
* **File**: [dashboard.py](file:///d:/project/news-intelligence-platform/project/dashboard.py)
* **Symptom**: AI Analyst text area and button bled into Workspace 6 when telemetry API returned offline status.
* **Root Cause**: `sys_ok = False` fell back to `render_unavailable_box()` without a scoped container, causing Streamlit component state leakage.
* **Fix**: Built an in-dashboard MongoDB Direct Fallback Telemetry Renderer inside `elif page == "6. SYSTEM / PIPELINE":`.
* **Regression Test**: Verified via `test_edge_cases.py`.

---

### ERROR 05: Kafka Producer Null Pointer Crash
* **Component**: Real-time Ingestion Service
* **File**: [ingestion_service.py](file:///d:/project/news-intelligence-platform/project/ingestion_service.py)
* **Symptom**: `AttributeError: 'NoneType' object has no attribute 'flush'` when Kafka broker port 9092 was down.
* **Root Cause**: Calls to `producer.flush()` and `producer.close()` assumed `producer` was initialized even when Kafka connection failed.
* **Fix**: Added explicit `if self.producer:` null checks around flush/close calls and implemented direct MongoDB upserts.
* **Regression Test**: Verified in `test_ingestion_service.py`.

---

### ERROR 06: Historical Backfill Infinite Throttling Loop
* **Component**: Historical Backfill Controller
* **File**: [historical/backfill_manager.py](file:///d:/project/news-intelligence-platform/project/historical/backfill_manager.py)
* **Symptom**: Backfill process paused infinitely printing `[THROTTLE] Realtime pipeline backpressure (10186 pending)`.
* **Root Cause**: Hardcoded backpressure threshold `max_pending=200` was triggered by pre-existing pending queue items.
* **Fix**: Raised default threshold in `check_realtime_backpressure` to `50000` items.
* **Regression Test**: Verified in `test_historical_backfill.py`.

---

### ERROR 07: Verbose Terminal Stdout Noise
* **Component**: Content Extractor
* **File**: `historical_crawlers/extractor.py`
* **Symptom**: Terminal output flooded with thousands of lines of extraction debug text, causing keyboard interrupts (`Ctrl+C`).
* **Root Cause**: Raw `print()` statements inside `extract_article()` and un-suppressed loggers from `newspaper3k` and `trafilatura`.
* **Fix**: Removed raw `print()` calls and added `logging.getLogger("newspaper").setLevel(logging.ERROR)`.
* **Regression Test**: Verified via `test_extraction_cleaning.py`.

---

## 2. Zero Unhandled Exceptions Policy

All API endpoints and UI render functions now adhere to strict fault-tolerant standards:
- **No bare `except:` blocks**: All exceptions log specific tracebacks or return structured error payloads.
- **Defensive Type Safety**: `first_present()` and `safe_str()` helpers convert `None`, missing keys, and unexpected list/dict variants to default values without raising `TypeError` or `AttributeError`.
