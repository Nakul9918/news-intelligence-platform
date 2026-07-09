from pymongo import MongoClient

from nlp.content_cleaner import clean_content

client = MongoClient("mongodb://localhost:27017/")

db = client["news_db"]

article = db.historical_urls_et.find_one(
    {
        "content": {
            "$exists": True
        }
    }
)

print("=" * 80)
print("ORIGINAL")
print("=" * 80)

print(article["content"][:3000])

print("\n\n")

print("=" * 80)
print("CLEANED")
print("=" * 80)

cleaned = clean_content(
    article["content"],
    article.get("source", "")
)

print(cleaned[:3000])