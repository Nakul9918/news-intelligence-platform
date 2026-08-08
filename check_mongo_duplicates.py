from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["news_db"]
coll = db["realtime_articles"]

total = coll.count_documents({})
print("Total documents:", total)

pipeline = [
    {"$group": {"_id": "$article_id", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
]

dups = list(coll.aggregate(pipeline))
print("Duplicate article_id groups count:", len(dups))
if dups:
    print("Sample duplicate article_ids:", dups[:5])

# Check indexes
indexes = list(coll.list_indexes())
print("Existing indexes:", [idx["name"] for idx in indexes])
