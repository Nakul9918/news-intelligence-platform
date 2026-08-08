"""
Phase 13 — Dashboard & API Integration Test
"""

import sys
import io
import time
import requests
from pathlib import Path
from pymongo import MongoClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME

API_URL = "http://localhost:8000"

def test_api_and_dashboard():
    print("=" * 80)
    print("RUNNING DASHBOARD & FASTAPI BACKEND INTEGRATION TEST (PHASE 13)")
    print("=" * 80)

    # 1. API Health Check
    print("\n--- Step 1: API Health Check ---")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
        health = resp.json()
        print(f"[PASS] API Health Check OK: {health}")
    except Exception as e:
        print(f"[FAIL] API server not reachable at {API_URL}: {e}")
        raise e

    # 2. Metrics Endpoint Check
    print("\n--- Step 2: Dashboard Metrics Endpoint ---")
    resp = requests.get(f"{API_URL}/api/metrics", timeout=5)
    assert resp.status_code == 200, f"Metrics endpoint failed: {resp.status_code}"
    metrics = resp.json()
    assert "total_articles" in metrics, "total_articles field missing!"
    assert "top_sources" in metrics, "top_sources field missing!"
    assert "top_categories" in metrics, "top_categories field missing!"
    assert "sentiment_distribution" in metrics, "sentiment_distribution field missing!"
    print(f"[PASS] Metrics Endpoint OK (Total Articles: {metrics['total_articles']}, Completed: {metrics['completed_articles']})")

    # 3. Live Feed Endpoint Check
    print("\n--- Step 3: Live Feed Endpoint ---")
    resp = requests.get(f"{API_URL}/api/live-feed?limit=10", timeout=5)
    assert resp.status_code == 200, f"Live feed endpoint failed: {resp.status_code}"
    feed = resp.json()
    assert "articles" in feed, "articles array missing from feed!"
    print(f"[PASS] Live Feed Endpoint OK (Retrieved {len(feed['articles'])} articles)")

    # 4. Search Endpoint Check (BM25 & Hybrid)
    print("\n--- Step 4: Search Endpoints Check ---")
    for search_type in ["hybrid", "bm25", "knn"]:
        resp = requests.get(f"{API_URL}/api/search?q=india&type={search_type}&limit=5", timeout=10)
        assert resp.status_code == 200, f"Search ({search_type}) failed: {resp.status_code}"
        search_res = resp.json()
        assert "articles" in search_res, f"Search articles array missing for type {search_type}!"
        print(f"[PASS] {search_type.upper()} Search Endpoint OK (Returned {len(search_res['articles'])} hits)")

    # 5. Article Detail Endpoint Check
    print("\n--- Step 5: Article Detail Endpoint Check ---")
    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    doc = m_client[DATABASE_NAME][REALTIME_COLLECTION_NAME].find_one({})
    m_client.close()

    if doc:
        art_id = doc.get("article_id") or str(doc.get("_id"))
        resp = requests.get(f"{API_URL}/api/articles/{art_id}", timeout=5)
        assert resp.status_code == 200, f"Article detail endpoint failed: {resp.status_code}"
        art_detail = resp.json()
        assert "title" in art_detail, "Title missing from article detail!"
        print(f"[PASS] Article Detail Endpoint OK (Inspected Article: '{art_detail['title'][:30]}...')")
    else:
        print("[SKIP] No article found in MongoDB to test detail endpoint")

    print("\n" + "=" * 80)
    print("ALL PHASE 13 API & DASHBOARD BACKEND INTEGRATION TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    test_api_and_dashboard()
