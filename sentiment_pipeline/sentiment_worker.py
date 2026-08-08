"""
Sentiment Analysis Worker

Processes keyword completed articles
from MongoDB.

Responsibilities
----------------
1. Fetch keyword completed articles.
2. Generate sentiment.
3. Update MongoDB.
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import time

from datetime import (
    datetime,
    UTC,
)

# =====================================================
# Third Party Libraries
# =====================================================

from pymongo import (
    MongoClient,
)

# =====================================================
# Project Configuration
# =====================================================

from config import (

    MONGO_URI,

    DATABASE_NAME,

    REALTIME_COLLECTION_NAME,

    BATCH_SIZE,

    PIPELINE_VERSION,

    LOG_SEPARATOR,

)

# =====================================================
# Common Sentiment Utilities
# =====================================================

from sentiment_pipeline.common_sentiment import (
    predict_sentiment,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)

logger = logging.getLogger(
    "SentimentWorker"
)

# =====================================================
# MongoDB
# =====================================================

client = MongoClient(
    MONGO_URI
)

database = client[
    DATABASE_NAME
]

collection = database[
    REALTIME_COLLECTION_NAME
]

# =====================================================
# Constants
# =====================================================

PIPELINE_STAGE = "sentiment"

# =====================================================
# Build Query
# =====================================================

def build_query():
    """
    Build MongoDB query for pending
    sentiment analysis.
    """

    return {

        "status.keywords_done": True,

        "status.sentiment_done": False,

        "status.sentiment_processing": False,

        "status.sentiment_failed": False,

    }


# =====================================================
# Get Pending Articles
# =====================================================

def get_pending_articles():
    """
    Fetch pending articles for
    sentiment analysis.
    """

    query = build_query()

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Fetching Pending Articles"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Query : {query}"
    )

    articles = list(

        collection.find(

            query

        ).limit(

            BATCH_SIZE

        )

    )

    logger.info(
        f"Pending Articles : {len(articles)}"
    )

    logger.info(LOG_SEPARATOR)

    return articles

# =====================================================
# Mark Processing
# =====================================================

def mark_processing(
    article
):
    """
    Mark article as currently
    processing sentiment.
    """

    collection.update_one(

        {
            "_id": article["_id"]
        },

        {
            "$set": {

                # =====================================
                # Status
                # =====================================

                "status.sentiment_processing": True,

                # =====================================
                # Pipeline
                # =====================================

                "last_pipeline_stage": PIPELINE_STAGE,

                "last_pipeline_update": datetime.now(
                    UTC
                ),

                # =====================================
                # Audit
                # =====================================

                "audit.updated_by": "sentiment_worker",

                "audit.last_updated_stage": PIPELINE_STAGE,

            }

        }

    )

    logger.info(
        "Article marked for sentiment analysis."
    )


# =====================================================
# Generate Sentiment
# =====================================================

def generate_sentiment(
    article
):
    """
    Generate sentiment from
    cleaned article content.
    """

    content = article.get(
        "clean_content",
        ""
    )

    # =====================================
    # Start Timer
    # =====================================

    started = time.perf_counter()

    # =====================================
    # Predict Sentiment
    # =====================================

    sentiment = predict_sentiment(
        content
    )

    # =====================================
    # Processing Time
    # =====================================

    sentiment_time = round(

        time.perf_counter() - started,

        3

    )

    return (

        sentiment,

        sentiment_time,

    )

# =====================================================
# Update MongoDB Article
# =====================================================

def update_article(
    article,
    sentiment,
    sentiment_time
):
    """
    Update sentiment in MongoDB.
    """

    now = datetime.now(
        UTC
    )

    previous_total = article.get(
        "processing",
        {}
    ).get(
        "total_time",
        0
    )

    collection.update_one(

        {
            "_id": article["_id"]
        },

        {
            "$set": {

                # =====================================
                # Sentiment
                # =====================================

                "sentiment": sentiment,

                # =====================================
                # Audit
                # =====================================

                "audit.updated_by": "sentiment_worker",

                "audit.last_updated_stage": PIPELINE_STAGE,

                # =====================================
                # Metadata
                # =====================================

                "updated_at": now,

                "last_pipeline_update": now,

                "last_pipeline_stage": PIPELINE_STAGE,

                "error": None,

                # =====================================
                # Processing
                # =====================================

                "processing.sentiment_time": sentiment_time,

                "processing.pipeline_version": PIPELINE_VERSION,

                "processing.total_time": round(

                    previous_total + sentiment_time,

                    3

                ),

                # =====================================
                # Status
                # =====================================

                "status.sentiment_done": True,

                "status.sentiment_processing": False,

                "status.sentiment_failed": False,

                "status.sentiment_retry_count": 0,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "MongoDB Updated"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Sentiment     : {sentiment['label']}"
    )

    logger.info(
        f"Confidence    : {sentiment['score']}"
    )

    logger.info(
        f"Model         : {sentiment['model']}"
    )

    logger.info(
        f"Process Time  : {sentiment_time:.3f} sec"
    )

    logger.info(LOG_SEPARATOR)

# =====================================================
# Process Article
# =====================================================

def process_article(
    article
):
    """
    Process one article.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Sentiment Analysis"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Source : {article.get('source', {}).get('name', '')}"
    )

    logger.info(
        f"URL    : {article.get('link', '')}"
    )

    try:

        # =====================================
        # Mark Processing
        # =====================================

        mark_processing(
            article
        )

        # =====================================
        # Generate Sentiment
        # =====================================

        sentiment, sentiment_time = generate_sentiment(
            article
        )

        # =====================================
        # Update MongoDB
        # =====================================

        update_article(

            article,

            sentiment,

            sentiment_time,

        )

        logger.info(
            "Sentiment Analysis Successful."
        )

        return True

    except Exception as error:

        logger.exception(error)

        collection.update_one(

            {
                "_id": article["_id"]
            },

            {
                "$set": {

                    "status.sentiment_processing": False,

                    "status.sentiment_failed": True,

                    "error": str(error),

                    "updated_at": datetime.now(
                        UTC
                    ),

                    "last_pipeline_stage": PIPELINE_STAGE,

                    "last_pipeline_update": datetime.now(
                        UTC
                    ),

                    "audit.updated_by": "sentiment_worker",

                    "audit.last_updated_stage": PIPELINE_STAGE,

                    "processing.sentiment_time": 0,

                    "processing.total_time": article.get(
                        "processing",
                        {}
                    ).get(
                        "total_time",
                        0
                    ),

                },

                "$inc": {

                    "status.sentiment_retry_count": 1

                }

            }

        )

        return False


# =====================================================
# Main
# =====================================================

def main():
    """
    Sentiment Analysis Worker
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Sentiment Analysis Worker"
    )

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    articles = get_pending_articles()

    if not articles:

        logger.info(
            "No pending articles found."
        )

        logger.info(LOG_SEPARATOR)

        return

    total = len(
        articles
    )

    success = 0

    failed = 0

    for article in articles:

        if process_article(
            article
        ):

            success += 1

        else:

            failed += 1

    total_time = round(

        time.perf_counter() - started,

        3

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Sentiment Analysis Summary"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Processed  : {total}"
    )

    logger.info(
        f"Successful : {success}"
    )

    logger.info(
        f"Failed     : {failed}"
    )

    logger.info(
        f"Total Time : {total_time:.3f} sec"
    )

    logger.info(LOG_SEPARATOR)


# =====================================================
# Program Entry
# =====================================================

if __name__ == "__main__":

    main()