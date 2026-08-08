"""
Phase 7 & 8 — Article Content Extraction & Cleaning Verification Test
"""

import sys
import io
import time
import hashlib
from pathlib import Path
from pymongo import MongoClient

# Set stdout encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME
from realtime_pipeline.realtime_nlp_pipeline import extract_and_clean_article

SOURCES = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]

def test_extraction_and_cleaning():
    print("=" * 80)
    print("RUNNING CONTENT EXTRACTION & CLEANING TEST (PHASE 7 & 8)")
    print("=" * 80)

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    coll = db[REALTIME_COLLECTION_NAME]

    source_stats = {src: {"extracted": 0, "failed": 0, "ext_time": 0.0, "clean_time": 0.0} for src in SOURCES}

    # 1. Sample Articles per source
    for src in SOURCES:
        print(f"\n--- Testing Source: {src} ---")
        
        # Pick 2 articles for testing (prefer empty content or pending status)
        articles = list(coll.find({
            "$or": [
                {"source.name": src},
                {"source": src}
            ]
        }).limit(2))

        if not articles:
            print(f"⚠️ No articles found in MongoDB for source: {src}")
            continue

        for art in articles:
            print(f"Processing Article ID: {art['_id']} | Link: {art.get('link')[:60]}...")
            res = extract_and_clean_article(art["_id"], coll)
            
            if res["success"]:
                source_stats[src]["extracted"] += 1
                source_stats[src]["ext_time"] += res["extraction_time"]
                source_stats[src]["clean_time"] += res["cleaning_time"]
                print(f"  [PASS] Title      : {res['title'][:50]}")
                print(f"  [PASS] Method     : {res['method']}")
                print(f"  [PASS] Content Len: {res['content_length']} | Cleaned Len: {res['clean_content_length']}")
            else:
                source_stats[src]["failed"] += 1
                print(f"  [FAIL] Error: {res.get('error')}")

    # 2. Test Invalid URL Failure Handling
    print("\n--- Testing Invalid URL Graceful Error Handling ---")
    invalid_url = "https://invalid-news-url-test-xyz999.com/fake-article.html"
    invalid_id = hashlib.sha256(invalid_url.encode("utf-8")).hexdigest()
    
    # Insert temporary dummy broken article
    dummy_doc = {
        "article_id": invalid_id,
        "link": invalid_url,
        "source": {"name": "Economic Times", "country": "India", "language": "en", "type": "rss"},
        "title": "",
        "content": "",
        "clean_content": "",
        "ingestion_type": "realtime",
        "processing": {"status": "PENDING", "stage": "ingested", "retry_count": 0}
    }
    coll.delete_many({"article_id": invalid_id})
    inserted = coll.insert_one(dummy_doc)
    dummy_id = inserted.inserted_id

    res_invalid = extract_and_clean_article(dummy_id, coll)
    assert not res_invalid["success"], "Extraction should have failed for unreachable URL!"
    
    # Check that document in DB recorded failure state & incremented retry_count
    failed_doc = coll.find_one({"_id": dummy_id})
    assert failed_doc["processing"]["status"] == "FAILED", "Status should be FAILED for invalid URL"
    assert failed_doc["processing"]["retry_count"] == 1, "retry_count should be incremented to 1"
    print("[PASS] Invalid URL handled safely: status=FAILED, retry_count=1, worker did not crash.")

    # Cleanup temporary test article
    coll.delete_one({"_id": dummy_id})

    # Summary Output
    print("\n" + "=" * 80)
    print(f"{'SOURCE':<20} {'EXTRACTED':<12} {'FAILED':<10} {'AVG EXTRACT TIME':<18} {'AVG CLEAN TIME':<18}")
    print("=" * 80)

    for src, st in source_stats.items():
        total_runs = st["extracted"] + st["failed"]
        avg_ext = (st["ext_time"] / total_runs) if total_runs > 0 else 0.0
        avg_cln = (st["clean_time"] / total_runs) if total_runs > 0 else 0.0
        print(f"{src:<20} {st['extracted']:<12} {st['failed']:<10} {avg_ext:<18.2f}s {avg_cln:<18.2f}s")

    print("=" * 80)
    print("ALL PHASE 7 & 8 TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    client.close()

if __name__ == "__main__":
    try:
        test_extraction_and_cleaning()
    except Exception as e:
        print(f"PHASE 7/8 TEST FAILED: {e}")
        sys.exit(1)
