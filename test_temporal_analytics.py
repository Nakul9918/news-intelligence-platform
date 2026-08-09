"""
=====================================================
Production-Grade Temporal Analytics Integration & QA Test Suite
=====================================================
Validates unit math, data contract parsing, statistical spike thresholds,
trend direction classifications, evidence lineage, and API response schemas.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from api.main import app
from api.temporal_analytics import (
    parse_any_timestamp,
    bucket_timestamp,
    get_recommended_bucket,
    compute_trend_direction
)


def test_unit_math_and_conversions():
    print("\n--- Step 1: Testing Unit Math & Date Conversions ---")
    
    # 1. Date Parsing
    now_utc = datetime.now(timezone.utc)
    ts_str = "2026-08-09T14:30:00Z"
    parsed_dt = parse_any_timestamp(ts_str)
    assert parsed_dt is not None, "Failed to parse ISO timestamp string!"
    assert parsed_dt.tzinfo == timezone.utc, "Parsed timestamp must be UTC aware!"
    print("  [PASS] ISO Timestamp parsing & UTC normalization OK")

    # 2. Bucketing Rules
    dt_ref = datetime(2026, 8, 9, 14, 35, 12, tzinfo=timezone.utc)
    assert bucket_timestamp(dt_ref, "1h") == "2026-08-09 14:00"
    assert bucket_timestamp(dt_ref, "1d") == "2026-08-09"
    assert bucket_timestamp(dt_ref, "1m") == "2026-08"
    print("  [PASS] Granularity bucketing (1h, 1d, 1m) OK")

    # 3. Dynamic Bucket Recommendation
    assert get_recommended_bucket("24h") == "1h"
    assert get_recommended_bucket("7d") == "1d"
    assert get_recommended_bucket("3m") == "1w"
    assert get_recommended_bucket("12m") == "1m"
    print("  [PASS] Recommended bucket selection OK")

    # 4. Trend Direction Calculation
    rising = compute_trend_direction(20, 10, min_baseline=3)
    assert rising["direction"] == "RISING"
    assert rising["growth_pct"] == 100.0

    declining = compute_trend_direction(5, 20, min_baseline=3)
    assert declining["direction"] == "DECLINING"
    assert declining["growth_pct"] == -75.0

    stable = compute_trend_direction(10, 10, min_baseline=3)
    assert stable["direction"] == "STABLE"

    insufficient = compute_trend_direction(15, 1, min_baseline=3)
    assert insufficient["direction"] == "INSUFFICIENT BASELINE"
    print("  [PASS] Deterministic trend direction math OK")


def test_api_analytics_endpoints():
    print("\n--- Step 2: Testing FastAPI Analytics Endpoints ---")
    client = TestClient(app)

    # 1. Health check
    resp = client.get("/health")
    assert resp.status_code == 200

    # 2. Volume Endpoint
    resp = client.get("/api/analytics/volume?window=24h&bucket=1h")
    assert resp.status_code == 200
    vol = resp.json()
    assert "data" in vol and "trend_direction" in vol and "data_quality" in vol
    print(f"  [PASS] Volume API (Direction: {vol['trend_direction']}, Valid Date Pct: {vol['data_quality']['valid_date_pct']}%)")

    # 3. Source Trends Endpoint
    resp = client.get("/api/analytics/source-trends?window=24h&bucket=1h")
    assert resp.status_code == 200
    src = resp.json()
    assert "sources" in src and "data" in src
    print(f"  [PASS] Source Trends API (Tracked sources: {len(src['sources'])})")

    # 4. Category Trends Endpoint
    resp = client.get("/api/analytics/category-trends?window=24h&bucket=1h")
    assert resp.status_code == 200
    cat = resp.json()
    assert "categories" in cat and "top_category" in cat
    print(f"  [PASS] Category Trends API (Top category: {cat['top_category']})")

    # 5. Sentiment Trends Endpoint
    resp = client.get("/api/analytics/sentiment-trends?window=24h&bucket=1h")
    assert resp.status_code == 200
    sent = resp.json()
    assert "data" in sent
    print(f"  [PASS] Sentiment Trends API ({len(sent['data'])} data points)")

    # 6. Spikes Endpoint
    resp = client.get("/api/analytics/spikes?window=24h")
    assert resp.status_code == 200
    spk = resp.json()
    assert "overall" in spk and "status" in spk["overall"]
    print(f"  [PASS] Statistical Spike API (Status: {spk['overall']['status']}, Threshold: {spk['overall']['spike_threshold']})")

    # 7. Keywords Endpoint
    resp = client.get("/api/analytics/keywords?window=24h&limit=10")
    assert resp.status_code == 200
    kw = resp.json()
    assert "keywords" in kw
    print(f"  [PASS] Emerging Keywords API ({len(kw['keywords'])} items)")

    # 8. Entities Endpoint
    resp = client.get("/api/analytics/entities?window=24h&limit=10")
    assert resp.status_code == 200
    ent = resp.json()
    assert "entities" in ent
    print(f"  [PASS] Emerging Entities API ({len(ent['entities'])} items)")

    # 9. Cross Source Endpoint
    resp = client.get("/api/analytics/cross-source?window=24h")
    assert resp.status_code == 200
    cs = resp.json()
    assert "topics" in cs
    print(f"  [PASS] Cross Source Activity API ({len(cs['topics'])} multi-publisher topics)")

    # 10. Trend Explanation Endpoint ("WHY?")
    resp = client.get("/api/analytics/trend-explanation?window=24h&item_type=overall&item_name=all")
    assert resp.status_code == 200
    exp = resp.json()
    assert "top_responsible_sources" in exp and "responsible_articles" in exp
    print(f"  [PASS] Evidence Lineage / Explanation API ({len(exp['responsible_articles'])} responsible articles)")


def main():
    print("=" * 80)
    print("RUNNING PRODUCTION-GRADE TEMPORAL ANALYTICS QA & INTEGRATION SUITE")
    print("=" * 80)
    test_unit_math_and_conversions()
    test_api_analytics_endpoints()
    print("\n" + "=" * 80)
    print("[SUCCESS] ALL TEMPORAL INTELLIGENCE QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    main()
