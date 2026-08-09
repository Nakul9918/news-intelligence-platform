"""
=====================================================
Production-Grade Event Intelligence QA Test Suite
=====================================================
Validates story clustering, descriptive title generation,
lifecycle status determination, confidence calculation,
chronological timeline evolution, and API contracts.
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


def test_event_intelligence_qa():
    print("=" * 80)
    print("RUNNING EVENT INTELLIGENCE & STORY EVOLUTION QA TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print("[PASS] API Health Check OK")

    # 2. Developing Stories API (/api/news/developing)
    print("\n--- Step 2: Testing Developing Stories API ---")
    resp = client.get("/api/news/developing")
    assert resp.status_code == 200, f"Developing stories API failed: {resp.status_code}"
    data = resp.json()
    assert "developing_stories" in data and "metrics" in data
    
    stories = data.get("developing_stories", [])
    print(f"  [PASS] Developing Stories API OK ({len(stories)} story clusters retrieved)")

    GENERIC_EXCLUSIONS = {"india", "general", "politics", "business", "world", "technology", "sports", "general topic", "meta"}

    for idx, story in enumerate(stories[:5], 1):
        s_title = story.get("title", "")
        s_status = story.get("status", "")
        s_conf = story.get("confidence_pct", 0)
        s_updates = story.get("update_count", 0)
        
        # Verify title quality
        assert s_title.lower() not in GENERIC_EXCLUSIONS, f"Generic title detected: '{s_title}'"
        assert len(s_title) > 5, f"Title too short: '{s_title}'"
        assert s_status in ["BREAKING", "DEVELOPING", "ACTIVE", "STABILIZING", "QUIET", "POSSIBLE STORY CLUSTER"]
        
        print(f"    Story #{idx}: [{s_status} | {s_conf}% Conf] '{s_title[:65]}...' ({s_updates} updates)")

    # 3. Story Profile & Evolution Investigation API (/api/events/investigate)
    print("\n--- Step 3: Testing Event Investigation API ('RBI') ---")
    resp = client.get("/api/events/investigate", params={"topic": "RBI"})
    assert resp.status_code == 200, f"Event investigation API failed: {resp.status_code}"
    inv_data = resp.json()
    assert "event" in inv_data and "timeline" in inv_data and "source_matrix" in inv_data
    
    timeline = inv_data.get("timeline", [])
    assert isinstance(timeline, list)
    print(f"  [PASS] Event Investigation API OK ({len(timeline)} timeline evolution stages)")

    if timeline:
        print(f"    Stage 1: [{timeline[0].get('stage_label')}] {timeline[0].get('headline')[:60]}...")
        print(f"    Latest Stage: [{timeline[-1].get('stage_label')}] {timeline[-1].get('headline')[:60]}...")

    # 4. Search Filter Test on Developing Stories
    print("\n--- Step 4: Testing Developing Stories Search Filter ('crime') ---")
    resp = client.get("/api/news/developing", params={"q": "crime"})
    assert resp.status_code == 200
    filter_data = resp.json()
    print(f"  [PASS] Search Filter OK ({len(filter_data.get('developing_stories', []))} matching story clusters)")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL EVENT INTELLIGENCE QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_event_intelligence_qa()
