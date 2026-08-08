from pymongo import MongoClient
from realtime_pipeline.realtime_nlp_pipeline import process_article
# MongoDB Connection
client = MongoClient("mongodb://localhost:27017")

db = client["news_db"]

collection = db["historical_urls_et"]


# Get one unprocessed article
article = collection.find_one(
    {
        "processed": {"$exists": False}
    }
)

if article is None:
    print("No unprocessed articles found.")
    exit()

print("=" * 60)
print("Processing Article")
print("=" * 60)

print("ID:", article["_id"])
print("Title:", article.get("title"))

# Run NLP Pipeline
process_article(
    article["_id"],
    collection
)

print("\nDone.")