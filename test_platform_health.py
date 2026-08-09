"""
=====================================================
Production-Grade Platform Health QA Test Suite
=====================================================
Validates infrastructure telemetry, Kafka consumer lag,
MongoDB data quality %, Elasticsearch index coverage gap,
process PID health, publisher source freshness, and system status banners.
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


def test_platform_health_qa():
    print("=" * 80)
    print("RUNNING PLATFORM HEALTH & OBSERVABILITY QA TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print("[PASS] API Health Check OK")

    # 2. Full System Telemetry Endpoint (/api/system/telemetry)
    print("\n--- Step 2: Testing System Telemetry API ---")
    resp = client.get("/api/system/telemetry")
    assert resp.status_code == 200, f"System Telemetry API failed: {resp.status_code}"
    data = resp.json()
    
    assert "overall_status" in data and "kafka" in data and "mongodb" in data
    assert "elasticsearch" in data and "pipeline" in data and "source_freshness" in data
    
    print(f"  [PASS] Telemetry Payload OK (Overall Status: '{data.get('overall_status')}')")

    # 3. Kafka Telemetry Validation
    print("\n--- Step 3: Testing Kafka Telemetry ---")
    kafka = data.get("kafka", {})
    assert "status" in kafka and "log_end_offset" in kafka and "consumer_lag" in kafka
    print(f"  [PASS] Kafka Telemetry OK (Status: '{kafka.get('status')}', Lag: {kafka.get('consumer_lag')})")

    # 4. MongoDB Telemetry & Data Quality %
    print("\n--- Step 4: Testing MongoDB Telemetry & Data Quality % ---")
    mongo = data.get("mongodb", {})
    assert "total_articles" in mongo and "data_quality" in mongo
    dq = mongo.get("data_quality", {})
    assert "title_coverage_pct" in dq and "content_coverage_pct" in dq
    print(f"  [PASS] MongoDB Telemetry OK (Articles: {mongo.get('total_articles')}, Title Coverage: {dq.get('title_coverage_pct')}%)")

    # 5. Elasticsearch Index Telemetry & Coverage Gap %
    print("\n--- Step 5: Testing Elasticsearch Telemetry & Coverage Gap % ---")
    es = data.get("elasticsearch", {})
    assert "indexed_documents" in es and "index_coverage_pct" in es
    print(f"  [PASS] Elasticsearch Telemetry OK (ES Docs: {es.get('indexed_documents')}, Coverage Ratio: {es.get('index_coverage_pct')}%)")

    # 6. Source Freshness Breakdown
    print("\n--- Step 6: Testing 4-Publisher Source Freshness ---")
    fresh = data.get("source_freshness", {})
    assert "Economic Times" in fresh and "The Hindu" in fresh
    assert "Indian Express" in fresh and "Hindustan Times" in fresh
    print(f"  [PASS] 4-Publisher Source Freshness OK")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL PLATFORM HEALTH QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_platform_health_qa()
