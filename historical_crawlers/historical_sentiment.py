from pymongo import MongoClient
from transformers import pipeline

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_articles"]

sentiment_pipeline = pipeline(
    "sentiment-analysis"
)

articles = collection.find(
    {
        "summary": {"$exists": True},
        "sentiment": {"$exists": False}
    }
).limit(20)

for article in articles:

    result = sentiment_pipeline(
        article["summary"][:512]
    )[0]

    collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "sentiment": result["label"],
                "sentiment_score": result["score"]
            }
        }
    )

    print(
        "Sentiment added:",
        article["title"],
        result["label"]
    )