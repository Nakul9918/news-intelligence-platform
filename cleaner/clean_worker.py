"""
=========================================================
Content Cleaning Worker

Processes extracted articles from MongoDB.

Responsibilities
----------------
Read Extracted Articles
        ↓
Clean Article Content
        ↓
Update MongoDB
=========================================================
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
# Common Extractor Utilities
# =====================================================

from cleaner.common_cleaner import (
    clean_text,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)

logger = logging.getLogger(
    "CleanWorker"
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

PIPELINE_STAGE = "cleaner"

DEFAULT_CONTENT = ""

# =====================================================
# Build Query
# =====================================================

def build_query():
    """
    Build MongoDB query for pending
    content cleaning.
    """

    return {

        "status.content_extracted": True,

        "status.content_cleaned": False,

        "status.content_clean_processing": False,

        "status.content_clean_failed": False,

    }


# =====================================================
# Get Pending Articles
# =====================================================

def get_pending_articles():
    """
    Fetch pending articles for cleaning.
    """

    query = build_query()

    logger.info(LOG_SEPARATOR)
    logger.info("Fetching Pending Articles")
    logger.info(LOG_SEPARATOR)
    logger.info(f"Query : {query}")

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
    Mark article as currently cleaning.
    """

    collection.update_one(

        {
            "_id": article["_id"]
        },

        {
            "$set": {

    "status.content_clean_processing": True,

    "last_pipeline_stage": PIPELINE_STAGE,

    "last_pipeline_update": datetime.now(UTC),

    "audit.updated_by": "clean_worker",

    "audit.last_updated_stage": PIPELINE_STAGE,

}

        }

    )

    logger.info(
        "Article marked as cleaning."
    )
# =====================================================
# Clean Article
# =====================================================

def clean_article(
    article
):
    """
    Clean extracted article content.
    """

    content = article.get(
        "content",
        DEFAULT_CONTENT
    )

    # =====================================
    # Start Timer
    # =====================================

    started = time.perf_counter()

    # =====================================
    # Clean Content
    # =====================================

    clean_content = clean_text(
        content
    )

    # =====================================
    # Processing Time
    # =====================================

    clean_time = round(

        time.perf_counter() - started,

        3

    )

    return (

        clean_content,

        clean_time,

    )


# =====================================================
# Update MongoDB Article
# =====================================================

def update_article(
    article,
    clean_content,
    clean_time
):
    """
    Update cleaned article in MongoDB.
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
                # Clean Content
                # =====================================

                "clean_content": clean_content,

                # =====================================
                # Audit
                # =====================================

                "audit.updated_by": "clean_worker",

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

                "processing.clean_time": clean_time,
                "processing.pipeline_version": PIPELINE_VERSION,
                "processing.total_time": round(
                previous_total + clean_time,
                3
            ),

                # =====================================
                # Status
                # =====================================

                "status.content_cleaned": True,

                "status.content_clean_processing": False,

                "status.content_clean_failed": False,

                "status.content_clean_retry_count": 0,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info("MongoDB Updated")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Content Length : {len(clean_content)}"
    )

    logger.info(
        f"Clean Time     : {clean_time:.3f} sec"
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
    logger.info("Cleaning Article")
    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Source : {article.get('source', {}).get('name', '')}"
    )

    logger.info(
        f"URL    : {article.get('link', '')}"
    )

    try:

        mark_processing(
            article
        )

        clean_content, clean_time = clean_article(
            article
        )
        if not clean_content:

            raise ValueError(
                "Cleaned content is empty."
            )

        update_article(
            article,
            clean_content,
            clean_time,
        )

        logger.info("Cleaning Successful.")

        return True

    except Exception as error:

        logger.exception(error)

        collection.update_one(

            {
                "_id": article["_id"]
            },

            {
                "$set": {

                            "status.content_clean_processing": False,

                            "status.content_clean_failed": True,

                            "error": str(error),

                            "updated_at": datetime.now(UTC),

                            "last_pipeline_stage": PIPELINE_STAGE,

                            "last_pipeline_update": datetime.now(UTC),

                            "audit.updated_by": "clean_worker",

                            "audit.last_updated_stage": PIPELINE_STAGE,

                            "processing.clean_time": 0,

                            "processing.total_time": article.get(
                                "processing",
                                {}
                            ).get(
                                "total_time",
                                0
                            ),

                        },

                "$inc": {

                    "status.content_clean_retry_count": 1

                }

            }

        )

        return False


# =====================================================
# Main
# =====================================================

def main():
    """
    Content Cleaning Worker
    """

    logger.info(LOG_SEPARATOR)
    logger.info("Content Cleaning Worker")
    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    articles = get_pending_articles()

    if not articles:

        logger.info("No pending articles found.")
        logger.info(LOG_SEPARATOR)

        return

    total = len(articles)

    success = 0

    failed = 0

    for article in articles:

        if process_article(article):

            success += 1

        else:

            failed += 1

    total_time = round(

        time.perf_counter() - started,

        3

    )

    logger.info(LOG_SEPARATOR)
    logger.info("Cleaning Summary")
    logger.info(LOG_SEPARATOR)

    logger.info(f"Processed  : {total}")
    logger.info(f"Successful : {success}")
    logger.info(f"Failed     : {failed}")
    logger.info(f"Total Time : {total_time:.3f} sec")

    logger.info(LOG_SEPARATOR)


# =====================================================
# Program Entry
# =====================================================

if __name__ == "__main__":

    main()