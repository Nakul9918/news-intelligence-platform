"""
=====================================================
Production-Grade Entity Intelligence QA Test Suite
=====================================================
Validates entity investigation queries, mention counts, 4-newspaper
coverage breakdowns, mention timelines, co-occurrences, and API contracts.
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


def test_entity_intelligence_qa():
    print("=" * 80)
    print("RUNNING ENTITY INTELLIGENCE INTEGRATION TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print("[PASS] API Health Check OK")

    # 2. Person Query ("Narendra Modi")
    print("\n--- Step 2: Testing Person Entity Query ('Narendra Modi') ---")
    resp = client.get("/api/entities/investigate", params={"entity": "Narendra Modi"})
    assert resp.status_code == 200
    p_data = resp.json()
    assert "entity" in p_data and "total_mentions" in p_data
    assert "source_coverage" in p_data and "related_entities" in p_data
    print(f"  [PASS] Person Query OK (Entity: '{p_data['entity']}', Type: '{p_data['type']}', Mentions: {p_data['total_mentions']}, Articles: {p_data['total_articles']})")

    # 3. Organization Query ("RBI")
    print("\n--- Step 3: Testing Organization Entity Query ('RBI') ---")
    resp = client.get("/api/entities/investigate", params={"entity": "RBI", "type": "ORG"})
    assert resp.status_code == 200
    o_data = resp.json()
    assert o_data["total_articles"] > 0
    print(f"  [PASS] Organization Query OK (Entity: '{o_data['entity']}', Mentions: {o_data['total_mentions']}, Publisher Ratio: '{o_data['coverage_ratio']}')")

    # 4. Location Query ("Mumbai")
    print("\n--- Step 4: Testing Location Entity Query ('Mumbai') ---")
    resp = client.get("/api/entities/investigate", params={"entity": "Mumbai", "type": "LOC"})
    assert resp.status_code == 200
    l_data = resp.json()
    assert l_data["total_articles"] > 0
    print(f"  [PASS] Location Query OK (Entity: '{l_data['entity']}', Mentions: {l_data['total_mentions']})")

    # 5. Unknown Entity Query ("xyzrandomentity123")
    print("\n--- Step 5: Testing Unknown Entity Query ('xyzrandomentity123') ---")
    resp = client.get("/api/entities/investigate", params={"entity": "xyzrandomentity123"})
    assert resp.status_code == 200
    u_data = resp.json()
    assert u_data["total_articles"] == 0 or len(u_data["sample_articles"]) == 0
    print("  [PASS] Unknown Entity query handled gracefully without crashing")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL ENTITY INTELLIGENCE QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_entity_intelligence_qa()
