from pymongo import MongoClient
from newspaper import Article

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

# ET Collection
collection = db["historical_urls_et"]

# Test only 5 articles first
articles = collection.find(
    {
        "content": {"$exists": False}
    }
).limit(5)

for doc in articles:

    try:

        url = doc["link"]

        article = Article(url)

        article.download()
        article.parse()

        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "title": article.title,
                    "content": article.text
                }
            }
        )

        print("Updated:", article.title)

    except Exception as e:

        print("Error:", e)