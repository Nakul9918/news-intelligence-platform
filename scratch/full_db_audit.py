"""
===========================================================
Full MongoDB & System Infrastructure Audit Script
===========================================================
Gathers exact empirical statistics from MongoDB news_db
for Phase 2 & Phase 3 of the Master Product Specification.
"""

import json
from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=3000)
db = client["news_db"]
coll = db["realtime_articles"]

# 1. Collection Totals
total = coll.count_documents({})
realtime_c = coll.count_documents({"ingestion_type": "realtime"})
historical_c = coll.count_documents({"ingestion_type": "historical"})
no_ing_type = coll.count_documents({"ingestion_type": {"$exists": False}})

# 2. Source Distribution
sources_pipe = [{"$group": {"_id": "$source.name", "count": {"$sum": 1}}}]
sources_res = {r["_id"] or "Unknown": r["count"] for r in coll.aggregate(sources_pipe)}

# 3. Processing Status Breakdown
status_pipe = [{"$group": {"_id": "$processing.status", "count": {"$sum": 1}}}]
status_res = {str(r["_id"]): r["count"] for r in coll.aggregate(status_pipe)}

# 4. Date Range
oldest_doc = coll.find({}, {"created_at": 1, "published_date": 1}).sort("created_at", 1).limit(1)
latest_doc = coll.find({}, {"created_at": 1, "published_date": 1}).sort("created_at", -1).limit(1)

oldest_list = list(oldest_doc)
latest_list = list(latest_doc)

oldest_ts = oldest_list[0].get("created_at") if oldest_list else "N/A"
latest_ts = latest_list[0].get("created_at") if latest_list else "N/A"

# 5. NLP Field Completeness
has_clean_content = coll.count_documents({"clean_content": {"$exists": True, "$ne": ""}})
has_summary = coll.count_documents({"summary.text": {"$exists": True, "$ne": ""}})
has_keywords = coll.count_documents({"keywords": {"$exists": True, "$not": {"$size": 0}}})
has_entities = coll.count_documents({"entities": {"$exists": True, "$not": {"$size": 0}}})
has_embeddings = coll.count_documents({"embedding": {"$exists": True, "$not": {"$size": 0}}})
has_sentiment = coll.count_documents({"sentiment.label": {"$exists": True, "$ne": ""}})
has_category = coll.count_documents({"category.label": {"$exists": True, "$ne": ""}})

# 6. Quarantine & Ingestion State
quarantine_c = db["quarantine_articles"].count_documents({}) if "quarantine_articles" in db.list_collection_names() else 0
ingestion_state_c = db["ingestion_state"].count_documents({}) if "ingestion_state" in db.list_collection_names() else 0

# 7. Check for Duplicates
duplicate_article_ids_pipe = [
    {"$group": {"_id": "$article_id", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]
dupes_id = list(coll.aggregate(duplicate_article_ids_pipe))

duplicate_links_pipe = [
    {"$group": {"_id": "$link", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]
dupes_link = list(coll.aggregate(duplicate_links_pipe))

audit_summary = {
    "total_articles": total,
    "realtime_articles": realtime_c,
    "historical_articles": historical_c,
    "unspecified_ingestion_type": no_ing_type,
    "source_distribution": sources_res,
    "processing_status_distribution": status_res,
    "date_range": {
        "oldest_created_at": str(oldest_ts),
        "latest_created_at": str(latest_ts)
    },
    "field_completeness": {
        "clean_content": has_clean_content,
        "summary": has_summary,
        "keywords": has_keywords,
        "entities": has_entities,
        "embedding": has_embeddings,
        "sentiment": has_sentiment,
        "category": has_category
    },
    "quarantine_count": quarantine_c,
    "ingestion_state_docs": ingestion_state_c,
    "duplicates": {
        "duplicate_article_ids": len(dupes_id),
        "duplicate_links": len(dupes_link)
    }
}

print(json.dumps(audit_summary, indent=2))
client.close()
