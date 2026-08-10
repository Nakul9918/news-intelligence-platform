"""
MongoDB News Intelligence Platform Data Inspector
Run this script to show your mentor live database statistics and article structures.
"""

from pymongo import MongoClient
import os
import json
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "news_db")

print("=" * 80)
print("       MONGODB LIVE NEWS INTELLIGENCE DATABASE DEMO")
print("=" * 80)
print(f"Connecting to: {MONGO_URI}")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DATABASE_NAME]

colls = db.list_collection_names()
print(f"\n[+] Active Collections in '{DATABASE_NAME}': {colls}")

realtime_col = db["realtime_articles"]
total_docs = realtime_col.count_documents({})

print(f"\n[*] TOTAL INDEXED ARTICLES : {total_docs:,}")

print("\n--- PUBLISHER DISTRIBUTION ---")
pipeline = [{"$group": {"_id": "$source.name", "count": {"$sum": 1}}}]
for r in realtime_col.aggregate(pipeline):
    src_name = r['_id'] or 'Unknown'
    cnt = r['count']
    pct = (cnt / max(total_docs, 1)) * 100
    print(f"  * {src_name:<20} : {cnt:>6,} articles ({pct:5.1f}%)")

print("\n--- CATEGORY DISTRIBUTION ---")
cat_pipeline = [{"$group": {"_id": "$category.label", "count": {"$sum": 1}}}]
for r in realtime_col.aggregate(cat_pipeline):
    cat_name = r['_id'] or 'General'
    cnt = r['count']
    print(f"  * {cat_name:<20} : {cnt:>6,} articles")

print("\n--- SAMPLE LIVE DOCUMENT STRUCTURE ---")
sample_doc = realtime_col.find_one({}, {"_id": 0, "embedding": 0, "clean_content": 0})
if sample_doc:
    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        return str(o)
    print(json.dumps(sample_doc, indent=2, default=default_serializer))

print("\n=" * 80)
print("[SUCCESS] DEMO READY FOR MENTOR REVIEW!")
print("=" * 80)

client.close()
