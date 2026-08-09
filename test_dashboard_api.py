"""
Phase 13 — Dashboard & API Integration Test
"""

import sys
import requests
from pathlib import Path
from fastapi.testclient import TestClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from api.main import app

def test_api_and_dashboard():
    print("=" * 80)
    print("RUNNING DASHBOARD & FASTAPI BACKEND INTEGRATION TEST (PHASE 13)")
    print("=" * 80)

    # Initialize TestClient for in-process route testing
    client = TestClient(app)

    # 1. API Health Check
    print("\n--- Step 1: API Health Check ---")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    health = resp.json()
    print(f"[PASS] API Health Check OK: {health}")

    # 2. Metrics Endpoint Check
    print("\n--- Step 2: Dashboard Metrics Endpoint ---")
    resp = client.get("/api/metrics")
    assert resp.status_code == 200, f"Metrics endpoint failed: {resp.status_code}"
    metrics = resp.json()
    assert "total_articles" in metrics, "total_articles field missing!"
    assert "top_sources" in metrics, "top_sources field missing!"
    assert "top_categories" in metrics, "top_categories field missing!"
    assert "sentiment_distribution" in metrics, "sentiment_distribution field missing!"
    print(f"[PASS] Metrics Endpoint OK (Total Articles: {metrics['total_articles']}, Completed: {metrics.get('completed_articles', 0)})")

    # 3. Live Feed Endpoint Check
    print("\n--- Step 3: Live Feed Endpoint ---")
    resp = client.get("/api/live-feed?limit=10")
    assert resp.status_code == 200, f"Live feed endpoint failed: {resp.status_code}"
    feed = resp.json()
    assert "articles" in feed, "articles array missing from feed!"
    print(f"[PASS] Live Feed Endpoint OK (Retrieved {len(feed['articles'])} articles)")

    # 4. Search Endpoint Check
    print("\n--- Step 4: Search Endpoints Check ---")
    resp = client.get("/search?q=market")
    assert resp.status_code == 200, f"Search endpoint failed: {resp.status_code}"
    search_res = resp.json()
    print(f"[PASS] Search Endpoint OK (Matches: {len(search_res.get('articles', []))})")

    # 5. Top News Endpoint Check
    print("\n--- Step 5: Top News Endpoint Check ---")
    resp = client.get("/api/news/top?timeframe=month&limit=5")
    assert resp.status_code == 200, f"Top news endpoint failed: {resp.status_code}"
    top_news = resp.json()
    assert isinstance(top_news, list), "Top news should return a list"
    print(f"[PASS] Top News Endpoint OK (Retrieved {len(top_news)} items)")

    print("\n" + "=" * 80)
    print("[SUCCESS] DASHBOARD & API INTEGRATION TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    test_api_and_dashboard()
