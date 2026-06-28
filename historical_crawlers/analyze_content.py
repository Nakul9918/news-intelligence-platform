from pymongo import MongoClient

# Connect MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

# Collections
collections = [
    "historical_urls_et",
    "historical_urls_thehindu",
    "historical_urls_indianexpress"
]

# Show one article from each collection
for collection in collections:

    print("\n" + "=" * 80)
    print(collection)
    print("=" * 80)

    article = db[collection].find_one(
        {
            "content": {
                "$exists": True
            }
        }
    )

    if article:

        print(article["content"][:3000])