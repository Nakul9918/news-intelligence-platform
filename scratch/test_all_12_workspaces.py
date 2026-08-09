"""
===========================================================
Automated Regression Test Suite — 12 Command Center Workspaces
===========================================================
Validates endpoints powering all 12 navigation areas:
1. /health & /api/metrics (Executive Overview)
2. /api/feed/realtime (Live News Feed)
3. /api/news/top10 (Top Current Stories)
4. /api/news/explorer (Time Machine)
5. /api/news/compare-publishers (Source Intelligence)
6. /api/analytics/volume & /api/analytics/spikes (Trends & Temporal)
7. /api/search & /api/news/keyword-intelligence (Topic & Keyword)
8. /api/analytics/entities (Entity Intelligence)
9. /api/news/developing & /api/news/timeline (Event Intelligence)
10. /api/news/current-affairs (Current Affairs)
11. /api/ai/ask (Search + AI Assistant RAG)
12. /api/system/telemetry (Platform Health)
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

ENDPOINTS = [
    ("01. Executive Overview Metrics", "/api/metrics", None),
    ("02. Live News Feed Stream", "/api/feed/realtime", {"limit": 10}),
    ("03. Top Current Stories Ranking", "/api/news/top10", {"limit": 10}),
    ("04. Time Machine Date Explorer", "/api/news/explorer", {"start_date": "2026-08-01", "end_date": "2026-08-09"}),
    ("05. Source Intelligence 4-Newspaper", "/api/news/compare-publishers", {"topic": "India economy"}),
    ("06. Trends Volume Analytics", "/api/analytics/volume", {"window": "24h"}),
    ("06. Trends Spike Alerts", "/api/analytics/spikes", None),
    ("07. Topic Search (Hybrid RRF)", "/api/search", {"q": "war", "type": "hybrid"}),
    ("08. Entity Intelligence", "/api/analytics/entities", None),
    ("09. Event Intelligence Developing", "/api/news/developing", None),
    ("09. Event Intelligence Timeline", "/api/news/timeline", {"topic": "Market"}),
    ("10. Current Affairs Categorized", "/api/news/current-affairs", {"timeframe": "Today"}),
    ("11. AI Assistant RAG Q&A", "/api/ai/ask", None), # Tested via POST below
    ("12. Platform Infrastructure Telemetry", "/api/system/telemetry", None),
]

print("======================================================================")
print("  REGRESSION TEST SUITE — 12 COMMAND CENTER WORKSPACE ENDPOINTS       ")
print("======================================================================\n")

passed = 0
failed = 0

for label, path, params in ENDPOINTS:
    t0 = time.time()
    try:
        if path == "/api/ai/ask":
            res = requests.post(f"{BASE_URL}{path}", json={"question": "What are the top 10 news stories today?"}, timeout=15)
        else:
            res = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
        
        elapsed_ms = (time.time() - t0) * 1000
        if res.status_code == 200:
            print(f"  [PASS] {label:<40} | Code: 200 OK | Time: {elapsed_ms:.1f}ms")
            passed += 1
        else:
            print(f"  [FAIL] {label:<40} | Code: {res.status_code} | Time: {elapsed_ms:.1f}ms")
            failed += 1
    except Exception as e:
        print(f"  [EXCEPT] {label:<38} | Error: {e}")
        failed += 1

print("\n======================================================================")
print(f"REGRESSION TEST RESULT: {passed} PASSED, {failed} FAILED")
print("======================================================================")
