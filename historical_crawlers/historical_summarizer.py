from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_urls_et"]

articles = collection.find(
    {
        "content": {"$exists": True},
        "summary": {"$exists": False}
    }
).limit(20)

for article in articles:

    content = article["content"]

    summary = content[:500]

    collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "summary": summary
            }
        }
    )

    print("Summary added:", article["title"])