from pymongo import MongoClient

db = MongoClient("mongodb://127.0.0.1:27017")["news_db"]
col = db["realtime_articles"]

total = col.count_documents({})
realtime_c = col.count_documents({"ingestion_type": "realtime"})
historical_c = col.count_documents({"ingestion_type": "historical"})
no_ingestion_type = col.count_documents({"ingestion_type": {"$exists": False}})
completed = col.count_documents({"processing.status": "COMPLETED"})
pending = col.count_documents({"processing.status": "PENDING"})

quarantine = 0
if "quarantine_articles" in db.list_collection_names():
    quarantine = db["quarantine_articles"].count_documents({})

ingestion_state = 0
if "ingestion_state" in db.list_collection_names():
    ingestion_state = db["ingestion_state"].count_documents({})

print("=" * 50)
print("MONGODB ARTICLE STATS")
print("=" * 50)
print(f"Total articles         : {total:,}")
print(f"  ingestion_type=realtime  : {realtime_c:,}")
print(f"  ingestion_type=historical: {historical_c:,}")
print(f"  ingestion_type=<none>    : {no_ingestion_type:,}")
print(f"NLP COMPLETED          : {completed:,}")
print(f"PENDING (queue)        : {pending:,}")
print(f"Quarantined            : {quarantine:,}")
print(f"Backfill state docs    : {ingestion_state:,}")
print()
print("SOURCE DISTRIBUTION:")
pipeline = [{"$group": {"_id": "$source.name", "count": {"$sum": 1}}}]
for r in sorted(col.aggregate(pipeline), key=lambda x: -(x["count"] or 0)):
    print(f"  {r['_id'] or 'Unknown'}: {r['count']:,}")
