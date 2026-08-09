"""
=====================================================
QA Integration Test: Related Keywords Extraction & API
=====================================================
Verifies that INTERACTIVE RELATED KEYWORDS:
1. Extract non-empty keywords with article counts for any topic.
2. Formats response adhering to data contract schema.
3. Handles zero data, noise, and unknown queries gracefully.
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


def test_related_keywords_qa():
    print("=" * 80)
    print("RUNNING QA INTEGRATION TEST SUITE FOR INTERACTIVE RELATED KEYWORDS")
    print("=" * 80)

    client = TestClient(app)

    queries = ["crime", "RBI", "AI", "Mumbai", "technology", "sports", "Indian economy", "elections"]

    for q in queries:
        resp = client.get("/api/topic/investigate", params={"q": q})
        assert resp.status_code == 200, f"Failed topic investigation for '{q}': {resp.status_code}"
        data = resp.json()
        
        rel_kws = data.get("related_keywords", [])
        print(f"\n[QUERY: '{q}'] Matches: {data.get('total_articles', 0)}")
        print(f"  Related Keywords ({len(rel_kws)} items):")
        
        assert isinstance(rel_kws, list), f"related_keywords must be a list for query '{q}'"
        if data.get("total_articles", 0) > 0:
            assert len(rel_kws) > 0, f"Expected non-empty related_keywords for query '{q}' with {data.get('total_articles')} articles"
            
            for item in rel_kws[:5]:
                assert "keyword" in item and "count" in item, f"Missing 'keyword' or 'count' key in item: {item}"
                print(f"    - '{item['keyword']}': {item['count']} articles")

    # Test unknown query zero-data state
    print("\n--- Testing Unknown Query Handling ('xyzrandom123456') ---")
    resp = client.get("/api/topic/investigate", params={"q": "xyzrandom123456"})
    assert resp.status_code == 200
    u_data = resp.json()
    assert u_data["related_keywords"] == []
    print("  [PASS] Unknown query returns empty list [] cleanly without error")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL RELATED KEYWORDS QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_related_keywords_qa()
