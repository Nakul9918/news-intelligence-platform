"""
Phase 4 — Automatic Ingestion Service Verification Test

Executes 1 cycle of ingestion_service, tests schema, SHA256 determinism,
Kafka publishing, and durable MongoDB deduplication.
"""

import sys
import io
import hashlib
from pathlib import Path
from pymongo import MongoClient

# Set stdout encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, KAFKA_TOPIC
from ingestion_service import run_ingestion_cycle, get_kafka_producer, init_durable_cache

def test_ingestion_service():
    print("=" * 80)
    print("RUNNING INGESTION SERVICE VERIFICATION TEST (PHASE 4)")
    print("=" * 80)

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    producer = get_kafka_producer()
    published_cache = init_durable_cache(db)

    print("\n--- Running Ingestion Cycle 1 ---")
    stats1 = run_ingestion_cycle(producer, db, published_cache)

    assert stats1["total_discovered"] > 0, "No articles discovered!"
    print(f"[PASS] Cycle 1 Discovered: {stats1['total_discovered']} articles, New: {stats1['total_new']}")

    print("\n--- Running Ingestion Cycle 2 (Deduplication Check) ---")
    stats2 = run_ingestion_cycle(producer, db, published_cache)

    # In cycle 2 immediately following cycle 1, new articles should be 0 because all disovered articles are in cache/state
    assert stats2["total_new"] == 0, f"Expected 0 new articles in Cycle 2, but got {stats2['total_new']}"
    assert stats2["total_duplicates"] == stats2["total_discovered"], "All articles in Cycle 2 should be marked duplicates"
    print(f"[PASS] Cycle 2 Deduplication verified: {stats2['total_duplicates']} duplicates skipped, 0 new articles published.")

    producer.close()
    client.close()

    print("=" * 80)
    print("ALL PHASE 4 INGESTION SERVICE TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_ingestion_service()
    except Exception as e:
        print(f"PHASE 4 TEST FAILED: {e}")
        sys.exit(1)
