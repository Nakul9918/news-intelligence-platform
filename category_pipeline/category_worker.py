"""
Category Classification Worker

Processes sentiment completed articles
from MongoDB.

Responsibilities
----------------
1. Fetch sentiment completed articles.
2. Predict category.
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
# Common Category Utilities
# =====================================================

from category_pipeline.common_category import (
    predict_category,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)

logger = logging.getLogger(
    "CategoryWorker"
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

PIPELINE_STAGE = "category"


# =====================================================
# Build Query
# =====================================================

def build_query():
    """
    Build MongoDB query for pending
    category classification.
    """

    return {

        "status.sentiment_done": True,

        "status.category_done": False,

        "status.category_processing": False,

        "status.category_failed": False,

    }


# =====================================================
# Get Pending Articles
# =====================================================

def get_pending_articles():
    """
    Fetch pending articles for
    category classification.
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
    processing category classification.
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

                "status.category_processing": True,

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

                "audit.updated_by": "category_worker",

                "audit.last_updated_stage": PIPELINE_STAGE,

            }

        }

    )

    logger.info(
        "Article marked for category classification."
    )


# =====================================================
# Generate Category
# =====================================================

def generate_category(
    article
):
    """
    Generate category from
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
    # Predict Category
    # =====================================

    category = predict_category(
        content
    )

    # =====================================
    # Processing Time
    # =====================================

    category_time = round(

        time.perf_counter() - started,

        3

    )

    return (

        category,

        category_time,

    )
# =====================================================
# Update MongoDB Article
# =====================================================

def update_article(
    article,
    category,
    category_time
):
    """
    Update category in MongoDB.
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
                # Category
                # =====================================

                "category": category,

                # =====================================
                # Audit
                # =====================================

                "audit.updated_by": "category_worker",

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

                "processing.category_time": category_time,

                "processing.pipeline_version": PIPELINE_VERSION,

                "processing.total_time": round(

                    previous_total + category_time,

                    3

                ),

                # =====================================
                # Status
                # =====================================

                "status.category_done": True,

                "status.category_processing": False,

                "status.category_failed": False,

                "status.category_retry_count": 0,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "MongoDB Updated"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Category      : {category['label']}"
    )

    logger.info(
        f"Confidence    : {category['score']}"
    )

    logger.info(
        f"Model         : {category['model']}"
    )

    logger.info(
        f"Process Time  : {category_time:.3f} sec"
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
        "Category Classification"
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
        # Generate Category
        # =====================================

        category, category_time = generate_category(
            article
        )

        # =====================================
        # Update MongoDB
        # =====================================

        update_article(

            article,

            category,

            category_time,

        )

        logger.info(
            "Category Classification Successful."
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

                    "status.category_processing": False,

                    "status.category_failed": True,

                    "error": str(error),

                    "updated_at": datetime.now(
                        UTC
                    ),

                    "last_pipeline_stage": PIPELINE_STAGE,

                    "last_pipeline_update": datetime.now(
                        UTC
                    ),

                    "audit.updated_by": "category_worker",

                    "audit.last_updated_stage": PIPELINE_STAGE,

                    "processing.category_time": 0,

                    "processing.total_time": article.get(
                        "processing",
                        {}
                    ).get(
                        "total_time",
                        0
                    ),

                },

                "$inc": {

                    "status.category_retry_count": 1

                }

            }

        )

        return False


# =====================================================
# Main
# =====================================================

def main():
    """
    Category Classification Worker
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Category Classification Worker"
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
        "Category Classification Summary"
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