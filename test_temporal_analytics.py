"""
Phase 14 — Temporal Analytics Integration Test
"""

import sys
import io
import time
import requests
from pathlib import Path

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

API_URL = "http://127.0.0.1:8000"

def test_temporal_analytics():
    print("=" * 80)
    print("RUNNING TEMPORAL ANALYTICS INTEGRATION TEST (PHASE 14)")
    print("=" * 80)

    # 1. API Health Check
    print("\n--- Step 1: API Health Check ---")
    resp = requests.get(f"{API_URL}/health", timeout=5)
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print(f"[PASS] API Health Check OK: {resp.json()}")

    # 2. Volume Analytics Endpoint
    print("\n--- Step 2: Temporal Volume Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/volume?window=24h&bucket=1h", timeout=5)
    assert resp.status_code == 200, f"Volume endpoint failed: {resp.status_code}"
    vol = resp.json()
    assert "data" in vol, "data field missing from volume analytics!"
    assert "total_count" in vol, "total_count field missing from volume analytics!"
    print(f"[PASS] Temporal Volume Endpoint OK (Window: 24h, Bucket: 1h, Total Articles: {vol['total_count']})")

    # 3. Source Trends Endpoint
    print("\n--- Step 3: Source Trends Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/source-trends?window=24h&bucket=1h", timeout=5)
    assert resp.status_code == 200, f"Source trends failed: {resp.status_code}"
    src_tr = resp.json()
    assert "sources" in src_tr, "sources array missing!"
    assert "data" in src_tr, "data array missing!"
    print(f"[PASS] Source Trends Endpoint OK (Tracked Sources: {src_tr['sources']})")

    # 4. Category Trends Endpoint
    print("\n--- Step 4: Category Trends Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/category-trends?window=24h&bucket=1h", timeout=5)
    assert resp.status_code == 200, f"Category trends failed: {resp.status_code}"
    cat_tr = resp.json()
    assert "categories" in cat_tr, "categories array missing!"
    print(f"[PASS] Category Trends Endpoint OK (Tracked Categories: {cat_tr['categories']})")

    # 5. Sentiment Trends Endpoint
    print("\n--- Step 5: Sentiment Trends Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/sentiment-trends?window=24h&bucket=1h", timeout=5)
    assert resp.status_code == 200, f"Sentiment trends failed: {resp.status_code}"
    sent_tr = resp.json()
    assert "data" in sent_tr, "data array missing!"
    print(f"[PASS] Sentiment Trends Endpoint OK (Data Points: {len(sent_tr['data'])})")

    # 6. Spike Detection Endpoint
    print("\n--- Step 6: Spike Detection Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/spikes?window=24h&multiplier=2.0", timeout=5)
    assert resp.status_code == 200, f"Spike detection failed: {resp.status_code}"
    spikes = resp.json()
    assert "overall" in spikes, "overall spike object missing!"
    print(f"[PASS] Spike Detection Endpoint OK (Status: {spikes['overall']['status']}, Current Vol: {spikes['overall']['current_volume']}, Baseline: {spikes['overall']['baseline_volume']})")

    # 7. Emerging Keywords Endpoint
    print("\n--- Step 7: Emerging Keywords Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/keywords?limit=10", timeout=5)
    assert resp.status_code == 200, f"Keywords endpoint failed: {resp.status_code}"
    kw = resp.json()
    assert "keywords" in kw, "keywords array missing!"
    print(f"[PASS] Emerging Keywords Endpoint OK (Retrieved {len(kw['keywords'])} trending keywords)")

    # 8. Emerging Entities Endpoint
    print("\n--- Step 8: Emerging Entities Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/entities?limit=10", timeout=5)
    assert resp.status_code == 200, f"Entities endpoint failed: {resp.status_code}"
    ent = resp.json()
    assert "entities" in ent, "entities array missing!"
    print(f"[PASS] Emerging Entities Endpoint OK (Retrieved {len(ent['entities'])} trending entities)")

    # 9. Cross-Source Activity Signals Endpoint
    print("\n--- Step 9: Cross-Source Activity Signals Endpoint ---")
    resp = requests.get(f"{API_URL}/api/analytics/cross-source?min_sources=2", timeout=5)
    assert resp.status_code == 200, f"Cross-source activity failed: {resp.status_code}"
    cs = resp.json()
    assert "topics" in cs, "topics array missing!"
    print(f"[PASS] Cross-Source Activity Endpoint OK (Identified {len(cs['topics'])} cross-source topics)")

    # 10. Verify Existing Phase 13 Endpoints (Non-Breaking Check)
    print("\n--- Step 10: Phase 13 Non-Breaking Backward Compatibility Check ---")
    resp = requests.get(f"{API_URL}/api/metrics", timeout=5)
    assert resp.status_code == 200, f"Phase 13 metrics failed: {resp.status_code}"
    resp = requests.get(f"{API_URL}/api/live-feed", timeout=5)
    assert resp.status_code == 200, f"Phase 13 live feed failed: {resp.status_code}"
    resp = requests.get(f"{API_URL}/api/search?q=india&type=bm25", timeout=5)
    assert resp.status_code == 200, f"Phase 13 search failed: {resp.status_code}"
    print("[PASS] All Phase 13 Endpoints Remain 100% Functional!")

    print("\n" + "=" * 80)
    print("ALL PHASE 14 TEMPORAL ANALYTICS TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    test_temporal_analytics()
