"""
Keyword Extraction Worker

Processes cleaned articles from MongoDB.

Responsibilities
----------------
1. Fetch cleaned articles.
2. Extract keywords using YAKE.
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
# Common Keyword Utilities
# =====================================================

from keyword_pipeline.common_keyword import (
    extract_keywords,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)

logger = logging.getLogger(
    "KeywordWorker"
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

PIPELINE_STAGE = "keywords"

DEFAULT_KEYWORDS = []
# =====================================================
# Build Query
# =====================================================

def build_query():
    """
    Build MongoDB query for pending
    keyword extraction.
    """

    return {

        "status.content_cleaned": True,

        "status.keywords_done": False,

        "status.keywords_processing": False,

        "status.keywords_failed": False,

    }


# =====================================================
# Get Pending Articles
# =====================================================

def get_pending_articles():
    """
    Fetch pending articles for
    keyword extraction.
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
    processing keywords.
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

                "status.keywords_processing": True,

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

                "audit.updated_by": "keyword_worker",

                "audit.last_updated_stage": PIPELINE_STAGE,

            }

        }

    )

    logger.info(
        "Article marked for keyword extraction."
    )


# =====================================================
# Generate Keywords
# =====================================================

def generate_keywords(
    article
):
    """
    Generate keywords from
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
    # Extract Keywords
    # =====================================

    keywords = extract_keywords(
        content
    )

    # =====================================
    # Processing Time
    # =====================================

    keyword_time = round(

        time.perf_counter() - started,

        3

    )

    return (

        keywords,

        keyword_time,

    )
# =====================================================
# Update MongoDB Article
# =====================================================

def update_article(
    article,
    keywords,
    keyword_time
):
    """
    Update extracted keywords
    in MongoDB.
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
                # Keywords
                # =====================================

                "keywords": keywords,

                # =====================================
                # Audit
                # =====================================

                "audit.updated_by": "keyword_worker",

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

                "processing.keyword_time": keyword_time,

                "processing.pipeline_version": PIPELINE_VERSION,

                "processing.total_time": round(

                    previous_total + keyword_time,

                    3

                ),

                # =====================================
                # Status
                # =====================================

                "status.keywords_done": True,

                "status.keywords_processing": False,

                "status.keywords_failed": False,

                "status.keywords_retry_count": 0,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "MongoDB Updated"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Keywords      : {keywords}"
    )

    logger.info(
        f"Keyword Count : {len(keywords)}"
    )

    logger.info(
        f"Keyword Time  : {keyword_time:.3f} sec"
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
        "Keyword Extraction"
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
        # Generate Keywords
        # =====================================

        keywords, keyword_time = generate_keywords(
            article
        )

        if not keywords:

            raise ValueError(
                "No keywords generated."
            )

        # =====================================
        # Update MongoDB
        # =====================================

        update_article(

            article,

            keywords,

            keyword_time,

        )

        logger.info(
            "Keyword Extraction Successful."
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

                    "status.keywords_processing": False,

                    "status.keywords_failed": True,

                    "error": str(error),

                    "updated_at": datetime.now(
                        UTC
                    ),

                    "last_pipeline_stage": PIPELINE_STAGE,

                    "last_pipeline_update": datetime.now(
                        UTC
                    ),

                    "audit.updated_by": "keyword_worker",

                    "audit.last_updated_stage": PIPELINE_STAGE,

                    "processing.keyword_time": 0,

                    "processing.total_time": article.get(
                        "processing",
                        {}
                    ).get(
                        "total_time",
                        0
                    ),

                },

                "$inc": {

                    "status.keywords_retry_count": 1

                }

            }

        )

        return False


# =====================================================
# Main
# =====================================================

def main():
    """
    Keyword Extraction Worker
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Keyword Extraction Worker"
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
        "Keyword Extraction Summary"
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
    