from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_urls"]

articles = collection.find(
    {
        "keywords": {"$exists": True},
        "category": {"$exists": False}
    }
)

for article in articles:

    text = (
        article.get("title", "") +
        " " +
        article.get("content", "")
    ).lower()

    if any(word in text for word in [
        "stock", "market", "ipo",
        "economy", "bank", "finance"
    ]):
        category = "Business"

    elif any(word in text for word in [
        "cricket", "football",
        "match", "player", "sports"
    ]):
        category = "Sports"

    elif any(word in text for word in [
        "election", "government",
        "minister", "politics"
    ]):
        category = "Politics"

    elif any(word in text for word in [
        "technology", "ai",
        "software", "tech"
    ]):
        category = "Technology"

    else:
        category = "General"

    collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "category": category
            }
        }
    )

    print(
        "Category added:",
        article["title"],
        "->",
        category
    )
