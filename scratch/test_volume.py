from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from collections import defaultdict

client = MongoClient("mongodb://127.0.0.1:27017")
coll = client["news_db"]["realtime_articles"]

now = datetime.now(timezone.utc)
start_24h = now - timedelta(hours=24)

pipeline = [
    {"$match": {"created_at": {"$gte": start_24h}}},
    {
        "$group": {
            "_id": {"$hour": "$created_at"},
            "count": {"$sum": 1}
        }
    }
]

res = list(coll.aggregate(pipeline))
hour_counts = {r["_id"]: r["count"] for r in res if isinstance(r.get("_id"), int)}

print("Raw last 24h hour counts:", hour_counts)

if sum(hour_counts.values()) < 20:
    pipeline_all = [
        {"$sort": {"created_at": -1}},
        {"$limit": 2000},
        {
            "$group": {
                "_id": {"$hour": "$created_at"},
                "count": {"$sum": 1}
            }
        }
    ]
    res_all = list(coll.aggregate(pipeline_all))
    hour_counts = {r["_id"]: r["count"] for r in res_all if isinstance(r.get("_id"), int)}
    print("Sampled 2000 hour counts:", hour_counts)

timeline_items = []
for i in range(24):
    h_dt = now - timedelta(hours=23 - i)
    hr_label = h_dt.strftime("%H:00")
    hr_num = h_dt.hour
    timeline_items.append({
        "timestamp": hr_label,
        "count": hour_counts.get(hr_num, 0)
    })

print("Generated 24-Hour Timeline:")
for t in timeline_items:
    print(f"  {t['timestamp']} -> {t['count']} articles")
