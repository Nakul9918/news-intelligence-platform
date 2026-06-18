from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles"]

articles = collection.find(
    {
        "content": {"$exists": True},
        "summary": {"$exists": False}
    }
)

for article in articles:

    content = article["content"]

    # Temporary summary
    summary = content[:300]

    collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "summary": summary
            }
        }
    )

    print("Summary added:", article["title"])
