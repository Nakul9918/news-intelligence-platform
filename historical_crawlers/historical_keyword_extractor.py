from pymongo import MongoClient
import yake

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_urls_et"]

kw_extractor = yake.KeywordExtractor(
    lan="en",
    n=1,
    top=5
)

articles = collection.find(
    {
        "content": {"$exists": True},
        "keywords": {"$exists": False}
    }
).limit(20)

for article in articles:

    keywords = kw_extractor.extract_keywords(
        article["content"]
    )

    keyword_list = [k[0] for k in keywords]

    collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "keywords": keyword_list
            }
        }
    )

    print(
        "Keywords added:",
        article["title"]
    )