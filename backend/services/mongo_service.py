from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
client = MongoClient("mongodb://localhost:27017")

db = client["news_db"]

collection = db["historical_articles"]


# ----------------------------
# Get All News
# ----------------------------
def get_all_news(skip=0, limit=20):

    news = list(
        collection.find(
            {},
            {
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news

# ----------------------------
# Get News By ID
# ----------------------------
def get_news_by_id(news_id: str):

    try:
        article = collection.find_one(
            {"_id": ObjectId(news_id)},
            {
                "embedding": 0,
                "embedding_metadata": 0,
                "summary_metadata": 0,
                "keyword_metadata": 0,
                "cleaning": 0
            }
        )

        if article:
            article["_id"] = str(article["_id"])

        return article

    except InvalidId:
        return None

# ----------------------------
# Search News
# ----------------------------
def search_news(query: str, skip=0, limit=20):

    news = list(
        collection.find(
            {
                "$text": {
                    "$search": query
                }
            },
            {
                "score": {
                    "$meta": "textScore"
                },
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .sort([("score", {"$meta": "textScore"})])
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news
# ----------------------------
# Get News By Category
# ----------------------------
def get_news_by_category(category: str, skip=0, limit=20):

    news = list(
        collection.find(
            {
                "category": category
            },
            {
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news
# ----------------------------
# Get News By Source
# ----------------------------
def get_news_by_source(source: str, skip=0, limit=20):

    news = list(
        collection.find(
            {
                "source": source
            },
            {
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news
# ----------------------------
# Latest News
# ----------------------------
def get_latest_news(skip=0, limit=20):

    news = list(
        collection.find(
            {},
            {
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .sort("published", -1)
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news
# ----------------------------
# Get News By Sentiment
# ----------------------------
def get_news_by_sentiment(sentiment: str, skip=0, limit=20):

    news = list(
        collection.find(
            {
                "sentiment": sentiment
            },
            {
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news
# ----------------------------
# Get News By Keyword
# ----------------------------
def get_news_by_keyword(keyword: str, skip=0, limit=20):

    news = list(
        collection.find(
            {
                "keywords": keyword
            },
            {
                "title": 1,
                "summary": 1,
                "source": 1,
                "category": 1,
                "sentiment": 1,
                "published": 1,
                "link": 1
            }
        )
        .skip(skip)
        .limit(limit)
    )

    for article in news:
        article["_id"] = str(article["_id"])

    return news
# ----------------------------
# Statistics
# ----------------------------
def get_statistics():

    return {
        "total_articles": collection.count_documents({}),
        "technology": collection.count_documents({"category": "Technology"}),
        "business": collection.count_documents({"category": "Business"}),
        "positive": collection.count_documents({"sentiment": "POSITIVE"}),
        "negative": collection.count_documents({"sentiment": "NEGATIVE"}),
        "neutral": collection.count_documents({"sentiment": "NEUTRAL"})
    }