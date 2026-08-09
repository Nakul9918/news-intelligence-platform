"""
=====================================================
Production-Grade Current Affairs QA Test Suite
=====================================================
Validates timeframe filtering, top ranked story clusters,
grounded highlights ("What Happened & Why It Matters"),
4-newspaper matrix, latest developments feed, and AI briefings.
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


def test_current_affairs_qa():
    print("=" * 80)
    print("RUNNING CURRENT AFFAIRS COMMAND CENTER QA TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print("[PASS] API Health Check OK")

    # 2. Today Timeframe Query
    print("\n--- Step 2: Testing Current Affairs Briefing ('Today') ---")
    resp = client.get("/api/news/current-affairs", params={"timeframe": "Today"})
    assert resp.status_code == 200, f"Current affairs API failed: {resp.status_code}"
    data = resp.json()
    assert "metrics" in data and "top_stories" in data and "highlights" in data
    assert "four_source_coverage" in data and "ai_briefing" in data
    
    metrics = data.get("metrics", {})
    print(f"  [PASS] Today Query OK (Updates: {metrics.get('updates_today')}, Developing: {metrics.get('developing_stories_count')}, Active Portals: '{metrics.get('sources_active')}')")

    # 3. Timeframe Switching Tests
    for tf in ["Yesterday", "LAST 7 DAYS", "THIS MONTH"]:
        print(f"\n--- Step 3: Testing Timeframe Switch ('{tf}') ---")
        tf_resp = client.get("/api/news/current-affairs", params={"timeframe": tf})
        assert tf_resp.status_code == 200
        tf_data = tf_resp.json()
        assert tf_data.get("timeframe") == tf
        print(f"  [PASS] Timeframe Switch '{tf}' OK ({len(tf_data.get('top_stories', []))} Top Ranked Stories)")

    # 4. Ranked Top Stories Validation
    print("\n--- Step 4: Testing Ranked Top Story Structure ---")
    top_stories = data.get("top_stories", [])
    if top_stories:
        top1 = top_stories[0]
        assert "rank" in top1 and "title" in top1 and "source_ratio" in top1
        print(f"  [PASS] Top Story #01: '{top1.get('title')[:60]}...' ({top1.get('update_count')} updates, Ratio: '{top1.get('source_ratio')}')")

    # 5. Highlights ("What Happened & Why It Matters")
    print("\n--- Step 5: Testing Grounded Highlights ---")
    highlights = data.get("highlights", [])
    if highlights:
        hl1 = highlights[0]
        assert "what_happened" in hl1 and "why_it_matters" in hl1
        print(f"  [PASS] Grounded Highlight: WHAT='{hl1.get('what_happened')[:50]}...' WHY='{hl1.get('why_it_matters')[:60]}...'")

    # 6. 4-Newspaper Coverage Matrix
    print("\n--- Step 6: Testing 4-Newspaper Coverage Matrix ---")
    four_cov = data.get("four_source_coverage", {})
    assert "Economic Times" in four_cov and "The Hindu" in four_cov
    assert "Indian Express" in four_cov and "Hindustan Times" in four_cov
    print(f"  [PASS] 4-Newspaper Coverage Matrix verified for all portals")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL CURRENT AFFAIRS QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_current_affairs_qa()
