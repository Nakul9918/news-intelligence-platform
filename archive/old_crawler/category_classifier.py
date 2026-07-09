from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles"]

def classify(title):

    title = title.lower()

    if any(word in title for word in [
        "cricket", "football", "wimbledon",
        "match", "sports"
    ]):
        return "Sports"

    elif any(word in title for word in [
        "sensex", "stock", "ipo",
        "bank", "market", "shares"
    ]):
        return "Business"

    elif any(word in title for word in [
        "g7", "government", "minister",
        "election", "politics"
    ]):
        return "Politics"

    else:
        return "General"


articles = collection.find(
    {"category": {"$exists": False}}
)

for article in articles:

    category = classify(article["title"])

    collection.update_one(
        {"_id": article["_id"]},
        {
            "$set": {
                "category": category
            }
        }
    )

    print(article["title"], "->", category)
