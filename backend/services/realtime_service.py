from bson import ObjectId
from bson.errors import InvalidId

from backend.services.database import realtime_collection
from backend.utils.serializer import (
    serialize_article,
    serialize_articles
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# =====================================================
# Projection
# =====================================================

NEWS_PROJECTION = {
    "title": 1,
    "summary": 1,
    "description": 1,
    "source": 1,
    "category": 1,
    "sentiment": 1,
    "published": 1,
    "created_at": 1,
    "link": 1,
    "keywords": 1
}


# =====================================================
# Get All News
# =====================================================

def get_all_realtime_news(skip=0, limit=20):

    logger.info(f"Fetching realtime news | skip={skip}, limit={limit}")

    news = list(
        realtime_collection.find({}, NEWS_PROJECTION)
        .sort("published", -1)
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Fetched {len(news)} realtime articles")

    return serialize_articles(news)


# =====================================================
# Get News By ID
# =====================================================

def get_realtime_news_by_id(news_id):

    try:

        logger.info(f"Fetching realtime article: {news_id}")

        article = realtime_collection.find_one(
            {"_id": ObjectId(news_id)}
        )

        if article:
            logger.info("Realtime article found")
        else:
            logger.warning("Realtime article not found")

        return serialize_article(article)

    except InvalidId:

        logger.error(f"Invalid ObjectId: {news_id}")

        return None


# =====================================================
# Search News
# =====================================================

def search_realtime_news(query, skip=0, limit=20):

    logger.info(f"Searching realtime news | query={query}")

    news = list(
        realtime_collection.find(
            {
                "$text": {
                    "$search": query
                }
            },
            {
                **NEWS_PROJECTION,
                "score": {
                    "$meta": "textScore"
                }
            }
        )
        .sort(
            [
                (
                    "score",
                    {
                        "$meta": "textScore"
                    }
                )
            ]
        )
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Search returned {len(news)} realtime articles")

    return serialize_articles(news)


# =====================================================
# Latest News
# =====================================================

def get_latest_realtime_news(skip=0, limit=20):

    logger.info("Fetching latest realtime news")

    news = list(
        realtime_collection.find({}, NEWS_PROJECTION)
        .sort("published", -1)
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Returned {len(news)} realtime articles")

    return serialize_articles(news)


# =====================================================
# Category Filter
# =====================================================

def get_realtime_news_by_category(category, skip=0, limit=20):

    logger.info(f"Fetching realtime category={category}")

    news = list(
        realtime_collection.find(
            {
                "category.category": {
                    "$regex": f"^{category}$",
                    "$options": "i"
                }
            },
            NEWS_PROJECTION
        )
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Returned {len(news)} articles")

    return serialize_articles(news)


# =====================================================
# Source Filter
# =====================================================

def get_realtime_news_by_source(source, skip=0, limit=20):

    logger.info(f"Fetching realtime source={source}")

    news = list(
        realtime_collection.find(
            {
                "source": {
                    "$regex": f"^{source}$",
                    "$options": "i"
                }
            },
            NEWS_PROJECTION
        )
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Returned {len(news)} articles")

    return serialize_articles(news)


# =====================================================
# Sentiment Filter
# =====================================================

def get_realtime_news_by_sentiment(sentiment, skip=0, limit=20):

    logger.info(f"Fetching realtime sentiment={sentiment}")

    news = list(
        realtime_collection.find(
            {
                "sentiment.label": {
                    "$regex": f"^{sentiment}$",
                    "$options": "i"
                }
            },
            NEWS_PROJECTION
        )
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Returned {len(news)} articles")

    return serialize_articles(news)


# =====================================================
# Keyword Filter
# =====================================================

def get_realtime_news_by_keyword(keyword, skip=0, limit=20):

    logger.info(f"Searching realtime keyword={keyword}")

    news = list(
        realtime_collection.find(
            {
                "keywords.text": {
                    "$regex": keyword,
                    "$options": "i"
                }
            },
            NEWS_PROJECTION
        )
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Returned {len(news)} articles")

    return serialize_articles(news)