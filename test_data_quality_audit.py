"""
Phase 16B — MongoDB & Elasticsearch Data Quality Audit Script
"""

import sys
import io
import time
from pathlib import Path
from pymongo import MongoClient
from elasticsearch import Elasticsearch

if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME
ELASTICSEARCH_URL = getattr(sys.modules['config'], 'ELASTICSEARCH_HOST', 'http://localhost:9200')

def audit_data_quality():
    print("=" * 80)
    print("PHASE 16B — DATA QUALITY AUDIT")
    print("=" * 80)

    # 1. MongoDB Quality Audit
    print("\n--- 1. MongoDB Audit (news_db.realtime_articles) ---")
    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    coll = m_client[DATABASE_NAME][REALTIME_COLLECTION_NAME]

    total_docs = coll.count_documents({})
    bootstrap_docs = coll.count_documents({"is_bootstrap": True})
    realtime_docs = coll.count_documents({"is_bootstrap": {"$ne": True}})
    
    completed_docs = coll.count_documents({"status": "COMPLETED"})
    pending_docs = coll.count_documents({"status": "PENDING"})
    processing_docs = coll.count_documents({"status": "PROCESSING"})
    failed_docs = coll.count_documents({"status": "FAILED"})

    missing_aid = coll.count_documents({"$or": [{"article_id": None}, {"article_id": ""}]})
    
    # Check duplicate article_id
    pipeline = [
        {"$group": {"_id": "$article_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicate_aids = len(list(coll.aggregate(pipeline)))

    missing_title = coll.count_documents({"$or": [{"title": None}, {"title": ""}]})
    missing_content = coll.count_documents({"$or": [{"content": None}, {"content": ""}]})
    missing_clean = coll.count_documents({"$or": [{"clean_content": None}, {"clean_content": ""}]})
    missing_category = coll.count_documents({"category": None})
    missing_sentiment = coll.count_documents({"sentiment": None})
    missing_summary = coll.count_documents({"summary": None})
    missing_embedding = coll.count_documents({"embedding": None})
    missing_source = coll.count_documents({"source": None})
    invalid_dates = coll.count_documents({"published_date": None})

    print(f"Total Documents       : {total_docs}")
    print(f"Bootstrap Documents   : {bootstrap_docs}")
    print(f"Realtime Documents    : {realtime_docs}")
    print(f"Status Completed      : {completed_docs}")
    print(f"Status Pending        : {pending_docs}")
    print(f"Status Processing     : {processing_docs}")
    print(f"Status Failed         : {failed_docs}")
    print(f"Missing article_id    : {missing_aid}")
    print(f"Duplicate article_id  : {duplicate_aids}")
    print(f"Missing title         : {missing_title}")
    print(f"Missing content       : {missing_content}")
    print(f"Missing clean_content : {missing_clean}")
    print(f"Missing category      : {missing_category}")
    print(f"Missing sentiment     : {missing_sentiment}")
    print(f"Missing summary       : {missing_summary}")
    print(f"Missing embedding     : {missing_embedding}")
    print(f"Missing source        : {missing_source}")
    print(f"Invalid dates         : {invalid_dates}")

    # 2. Elasticsearch Quality Audit
    print("\n--- 2. Elasticsearch Audit (news_articles) ---")
    es = Elasticsearch(ELASTICSEARCH_URL)
    es_count = 0
    missing_es = 0
    duplicate_es_ids = 0
    invalid_vectors = 0
    wrong_dim_vectors = 0

    if es.ping():
        es_res = es.count(index="news_articles")
        es_count = es_res.get("count", 0)
        missing_es = max(0, completed_docs - es_count)

        # Check sample ES doc vector dimension
        sample = es.search(index="news_articles", body={"query": {"match_all": {}}, "size": 1})
        hits = sample.get("hits", {}).get("hits", [])
        if hits:
            sample_src = hits[0].get("_source", {})
            vec = sample_src.get("embedding", [])
            if not isinstance(vec, list) or len(vec) == 0:
                invalid_vectors += 1
            elif len(vec) != 384:
                wrong_dim_vectors += 1

        print(f"Elasticsearch Total Count : {es_count}")
        print(f"Missing ES Documents      : {missing_es}")
        print(f"Duplicate ES IDs          : {duplicate_es_ids}")
        print(f"Invalid Vectors           : {invalid_vectors}")
        print(f"Wrong Vector Dimensions   : {wrong_dim_vectors} (Expected: 384)")
    else:
        print("Elasticsearch service not reachable!")

    m_client.close()

    return {
        "mongo_total": total_docs,
        "completed": completed_docs,
        "es_count": es_count,
        "duplicate_aids": duplicate_aids,
        "missing_aid": missing_aid
    }

if __name__ == "__main__":
    audit_data_quality()
