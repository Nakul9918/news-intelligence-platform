from collections import Counter

from backend.services.database import (
    historical_collection,
    realtime_collection,
)

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def get_statistics():

    logger.info("Calculating news statistics")

    historical_count = historical_collection.count_documents({})
    realtime_count = realtime_collection.count_documents({})

    total_articles = historical_count + realtime_count

    # ============================================
    # Top Sources (Realtime)
    # ============================================

    source_counter = Counter()

    for article in realtime_collection.find({}, {"source": 1}):

        source = article.get("source", "Unknown")

        source_counter[source] += 1

    # ============================================
    # Categories (Realtime)
    # ============================================

    category_counter = Counter()

    for article in realtime_collection.find({}, {"category.category": 1}):

        category = (
            article.get("category", {})
            .get("category", "Unknown")
        )

        category_counter[category] += 1

    # ============================================
    # Sentiment (Realtime)
    # ============================================

    sentiment_counter = Counter()

    for article in realtime_collection.find({}, {"sentiment.label": 1}):

        sentiment = (
            article.get("sentiment", {})
            .get("label", "Unknown")
        )

        sentiment_counter[sentiment] += 1

    logger.info("Statistics calculated successfully")

    return {

        "historical_articles": historical_count,

        "realtime_articles": realtime_count,

        "total_articles": total_articles,

        "top_sources": dict(source_counter),

        "top_categories": dict(category_counter),

        "sentiment_distribution": dict(sentiment_counter)

    }