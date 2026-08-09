"""
=====================================================
Production-Grade Topic & Keyword Intelligence Test Suite
=====================================================
Validates topic investigation queries, keyword co-occurrence,
NER entity extraction, source comparisons, and API contracts.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from api.main import app


def test_topic_keyword_intelligence():
    print("=" * 80)
    print("RUNNING TOPIC & KEYWORD INTELLIGENCE INTEGRATION TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print("[PASS] API Health Check OK")

    # 2. Topic Investigation API (Phrase query: "RBI rate")
    print("\n--- Step 2: Testing Topic Investigation API ('RBI rate') ---")
    resp = client.get("/api/topic/investigate", params={"q": "RBI rate", "window": "24h"})
    assert resp.status_code == 200, f"Topic investigation failed: {resp.status_code}"
    t_data = resp.json()
    assert "query" in t_data and "total_articles" in t_data
    assert "source_comparison" in t_data and "sentiment_breakdown" in t_data
    print(f"  [PASS] Topic Investigation API OK (Query: '{t_data['query']}', Matches: {t_data['total_articles']}, Dominant Sentiment: '{t_data['dominant_sentiment']}')")

    # 3. Topic Investigation API (Person query: "Virat Kohli")
    print("\n--- Step 3: Testing Person Topic Query ('Virat Kohli') ---")
    resp = client.get("/api/topic/investigate", params={"q": "Virat Kohli"})
    assert resp.status_code == 200
    p_data = resp.json()
    assert "entities" in p_data
    print(f"  [PASS] Person Query OK (Matches: {p_data['total_articles']}, Publisher ratio: '{p_data['coverage_ratio']}')")

    # 4. Topic Investigation API (Location query: "Mumbai")
    print("\n--- Step 4: Testing Location Topic Query ('Mumbai') ---")
    resp = client.get("/api/topic/investigate", params={"q": "Mumbai"})
    assert resp.status_code == 200
    loc_data = resp.json()
    assert "top_categories" in loc_data
    print(f"  [PASS] Location Query OK (Matches: {loc_data['total_articles']})")

    # 5. Search API Endpoint with filters (/api/search)
    print("\n--- Step 5: Testing Search API with Filters ---")
    resp = client.get("/api/search", params={"q": "economy", "type": "hybrid", "limit": 10})
    assert resp.status_code == 200
    s_data = resp.json()
    assert "articles" in s_data
    print(f"  [PASS] Search API OK (Hits: {len(s_data['articles'])})")

    # 6. Unknown Query Handling ("xyzrandom123")
    print("\n--- Step 6: Testing Unknown Query Handling ('xyzrandom123') ---")
    resp = client.get("/api/topic/investigate", params={"q": "xyzrandom123"})
    assert resp.status_code == 200
    u_data = resp.json()
    assert u_data["total_articles"] == 0 or len(u_data["sample_articles"]) == 0
    print("  [PASS] Unknown Query handled gracefully without crashing")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL TOPIC & KEYWORD INTELLIGENCE QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_topic_keyword_intelligence()
