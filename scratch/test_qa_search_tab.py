"""
===========================================================
QA Test Suite — Search & Discovery Workspace
===========================================================
Executes enterprise QA testing against /api/search endpoint
covering functional queries, edge cases, date filters, and
retrieval strategies.
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/search"

TEST_CASES = [
    # 1. Standard Keyword Queries
    {"name": "Standard Keyword Search ('economy')", "params": {"q": "economy", "type": "hybrid"}},
    {"name": "Multi-Word Entity Search ('Reserve Bank')", "params": {"q": "Reserve Bank", "type": "hybrid"}},
    {"name": "Sector Search ('stock market')", "params": {"q": "stock market", "type": "hybrid"}},
    
    # 2. Retrieval Strategies
    {"name": "BM25 Keyword Strategy", "params": {"q": "India", "type": "bm25"}},
    {"name": "Dense Vector KNN Strategy", "params": {"q": "India", "type": "knn"}},
    {"name": "Hybrid RRF Strategy", "params": {"q": "India", "type": "hybrid"}},
    
    # 3. Date Filters
    {"name": "Date Filter ('Last 7 Days')", "params": {"q": "news", "start_date": "2026-08-02", "end_date": "2026-08-09"}},
    
    # 4. Stress & Edge Cases
    {"name": "Regex Metacharacter Test ('[crime]')", "params": {"q": "[crime]", "type": "hybrid"}},
    {"name": "Special Character Stress ('!@#$%^&*()')", "params": {"q": "!@#$%^&*()", "type": "hybrid"}},
    {"name": "Non-matching Query ('xyz999nonexistent')", "params": {"q": "xyz999nonexistent", "type": "hybrid"}},
]

print("======================================================================")
print("       ENTERPRISE QA TEST SUITE — SEARCH & DISCOVERY WORKSPACE        ")
print("======================================================================\n")

passed = 0
failed = 0

for tc in TEST_CASES:
    name = tc["name"]
    params = tc["params"]
    t0 = time.time()
    try:
        res = requests.get(BASE_URL, params=params, timeout=10)
        elapsed_ms = (time.time() - t0) * 1000
        if res.status_code == 200:
            data = res.json()
            hits = data.get("articles") or data.get("results") or []
            print(f"  [PASS] {name:<42} | Code: 200 OK | Hits: {len(hits):<3} | Time: {elapsed_ms:.1f}ms")
            passed += 1
        else:
            print(f"  [FAIL] {name:<42} | Code: {res.status_code} | Time: {elapsed_ms:.1f}ms")
            failed += 1
    except Exception as e:
        print(f"  [EXCEPT] {name:<40} | Error: {e}")
        failed += 1

print("\n======================================================================")
print(f"QA TEST SUMMARY: {passed} PASSED, {failed} FAILED")
print("======================================================================")
