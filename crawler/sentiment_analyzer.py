from transformers import pipeline
from pymongo import MongoClient

sentiment_model = pipeline("sentiment-analysis")

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles"]

articles = collection.find(
    {
        "summary": {"$exists": True},
        "sentiment": {"$exists": False}
    }
)

for article in articles:

    result = sentiment_model(article["summary"])[0]

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
        article["title"],
        "->",
        result["label"],
        result["score"]
    )