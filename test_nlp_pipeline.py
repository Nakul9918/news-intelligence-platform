"""
Phase 9 — Multi-Stage NLP Pipeline Verification Test
"""

import sys
import io
import time
from pathlib import Path
from pymongo import MongoClient

# Set stdout encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME
from realtime_pipeline.realtime_nlp_pipeline import process_article

SOURCES = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]

def test_nlp_enrichment():
    print("=" * 80)
    print("RUNNING MULTI-STAGE NLP PIPELINE VERIFICATION TEST (PHASE 9)")
    print("=" * 80)

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    coll = db[REALTIME_COLLECTION_NAME]

    sample_articles = []
    
    for src in SOURCES:
        docs = list(coll.find({
            "$or": [
                {"source.name": src},
                {"source": src}
            ],
            "clean_content": {"$exists": True, "$ne": ""}
        }).limit(2))
        
        if not docs:
            # Fallback: pick any doc for this source
            docs = list(coll.find({
                "$or": [
                    {"source.name": src},
                    {"source": src}
                ]
            }).limit(2))
            
        sample_articles.extend(docs)

    print(f"Total Sample Articles Selected: {len(sample_articles)}")
    assert len(sample_articles) > 0, "No sample articles found in MongoDB for testing!"

    stats = {
        "tested": 0,
        "passed": 0,
        "summary": 0,
        "sentiment": 0,
        "category": 0,
        "keywords": 0,
        "ner": 0,
        "embedding": 0,
        "embedding_dim": None,
        "timings": {
            "summary": [], "sentiment": [], "category": [], "keyword": [], "ner": [], "embedding": [], "total": []
        }
    }

    for art in sample_articles:
        art_id = art["_id"]
        title = art.get("title", "")[:50]
        src_name = art.get("source", {}).get("name") if isinstance(art.get("source"), dict) else str(art.get("source"))
        print(f"\n--- Testing Article [{src_name}]: {title} ---")
        
        stats["tested"] += 1
        success = process_article(art_id, coll)
        assert success, f"Pipeline execution failed for article {art_id}"

        # Fetch enriched document from MongoDB
        updated = coll.find_one({"_id": art_id})
        
        # 1. Summary Check
        summary = updated.get("summary")
        if summary:
            stats["summary"] += 1
            print(f"  [PASS] Summary: {str(summary)[:60]}...")
            
        # 2. Sentiment Check
        sentiment = updated.get("sentiment")
        if sentiment and isinstance(sentiment, dict) and sentiment.get("label"):
            stats["sentiment"] += 1
            print(f"  [PASS] Sentiment: {sentiment.get('label')} (score: {sentiment.get('score', 0.0)})")

        # 3. Category Check
        category = updated.get("category")
        if category and isinstance(category, dict) and category.get("label"):
            stats["category"] += 1
            print(f"  [PASS] Category: {category.get('label')}")

        # 4. Keywords Check
        keywords = updated.get("keywords")
        if isinstance(keywords, list):
            stats["keywords"] += 1
            print(f"  [PASS] Keywords Count: {len(keywords)}")

        # 5. Entities Check
        entities = updated.get("entities")
        if isinstance(entities, list):
            stats["ner"] += 1
            print(f"  [PASS] Entities Count: {len(entities)}")

        # 6. Embedding Check
        embedding = updated.get("embedding")
        if isinstance(embedding, list) and len(embedding) > 0:
            stats["embedding"] += 1
            stats["embedding_dim"] = len(embedding)
            # Verify numeric
            assert all(isinstance(v, (int, float)) for v in embedding[:10]), "Embedding items must be numeric!"
            print(f"  [PASS] Embedding Vector: Dim {len(embedding)}, numeric type verified.")

        # Timings
        proc = updated.get("processing", {})
        stats["timings"]["summary"].append(proc.get("summary_time", 0.0))
        stats["timings"]["sentiment"].append(proc.get("sentiment_time", 0.0))
        stats["timings"]["category"].append(proc.get("category_time", 0.0))
        stats["timings"]["keyword"].append(proc.get("keyword_time", 0.0))
        stats["timings"]["ner"].append(proc.get("ner_time", 0.0))
        stats["timings"]["embedding"].append(proc.get("embedding_time", 0.0))
        stats["timings"]["total"].append(proc.get("total_time", 0.0))

        # Verification of status
        assert proc.get("status") == "COMPLETED", f"Expected COMPLETED status, got {proc.get('status')}"
        stats["passed"] += 1

    # Idempotency Rerun Test
    print("\n--- Testing Idempotent Pipeline Rerun ---")
    idemp_art = sample_articles[0]
    idemp_success = process_article(idemp_art["_id"], coll)
    assert idemp_success, "Idempotent rerun failed!"
    print("[PASS] Idempotent rerun completed without errors.")

    print("\n" + "=" * 80)
    print("PHASE 9 PERFORMANCE & TIMING SUMMARY")
    print("=" * 80)
    def avg(lst): return sum(lst) / len(lst) if lst else 0.0
    print(f"Articles Tested      : {stats['tested']}")
    print(f"Average Summary Time : {avg(stats['timings']['summary']):.4f}s")
    print(f"Average Sentiment Time: {avg(stats['timings']['sentiment']):.4f}s")
    print(f"Average Category Time : {avg(stats['timings']['category']):.4f}s")
    print(f"Average Keyword Time  : {avg(stats['timings']['keyword']):.4f}s")
    print(f"Average NER Time      : {avg(stats['timings']['ner']):.4f}s")
    print(f"Average Embedding Time: {avg(stats['timings']['embedding']):.4f}s")
    print(f"Average Total Time    : {avg(stats['timings']['total']):.4f}s")
    print(f"Embedding Dimension   : {stats['embedding_dim']}")
    print("=" * 80)
    print("ALL PHASE 9 NLP ENRICHMENT TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    client.close()

if __name__ == "__main__":
    try:
        test_nlp_enrichment()
    except Exception as e:
        print(f"PHASE 9 TEST FAILED: {e}")
        sys.exit(1)
