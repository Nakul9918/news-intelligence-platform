from bson import ObjectId
from bson.errors import InvalidId

from backend.exceptions.custom_exceptions import (
    InvalidQueryException,
    NewsNotFoundException,
)

from backend.services.database import historical_collection

from backend.utils.logger import get_logger
from backend.utils.serializer import (
    serialize_article,
    serialize_articles,
)

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
    "keywords": 1,
}


# =====================================================
# Get All Historical News
# =====================================================

def get_all_news(skip=0, limit=20):

    logger.info(f"Fetching historical news | skip={skip}, limit={limit}")

    news = list(
        historical_collection.find({}, NEWS_PROJECTION)
        .sort("published", -1)
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Fetched {len(news)} historical articles")

    return serialize_articles(news)


# =====================================================
# Get News By ID
# =====================================================

def get_news_by_id(news_id):

    logger.info(f"Fetching historical article: {news_id}")

    try:
        object_id = ObjectId(news_id)

    except InvalidId:

        logger.warning(f"Invalid ObjectId: {news_id}")

        raise InvalidQueryException()

    article = historical_collection.find_one(
        {"_id": object_id},
        NEWS_PROJECTION,
    )

    if article is None:

        logger.warning(f"Historical article not found: {news_id}")

        raise NewsNotFoundException()

    logger.info("Historical article found")

    return serialize_article(article)


# =====================================================
# Search Historical News
# =====================================================

def search_news(query, skip=0, limit=20):

    logger.info(f"Searching historical news | query={query}")

    news = list(
        historical_collection.find(
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

    logger.info(f"Search returned {len(news)} articles")

    return serialize_articles(news)


# =====================================================
# Category Filter
# =====================================================

def get_news_by_category(category, skip=0, limit=20):

    logger.info(f"Fetching category={category}")

    news = list(
        historical_collection.find(
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

def get_news_by_source(source, skip=0, limit=20):

    logger.info(f"Fetching source={source}")

    news = list(
        historical_collection.find(
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
# Latest Historical News
# =====================================================

def get_latest_news(skip=0, limit=20):

    logger.info("Fetching latest historical news")

    news = list(
        historical_collection.find(
            {},
            NEWS_PROJECTION
        )
        .sort("published", -1)
        .skip(skip)
        .limit(limit)
    )

    logger.info(f"Returned {len(news)} latest articles")

    return serialize_articles(news)


# =====================================================
# Sentiment Filter
# =====================================================

def get_news_by_sentiment(sentiment, skip=0, limit=20):

    logger.info(f"Fetching sentiment={sentiment}")

    news = list(
        historical_collection.find(
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

def get_news_by_keyword(keyword, skip=0, limit=20):

    logger.info(f"Searching keyword={keyword}")

    news = list(
        historical_collection.find(
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