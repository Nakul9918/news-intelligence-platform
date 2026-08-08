

"""
=========================================================
Extract Worker

Processes pending articles from MongoDB.

Responsibilities
----------------
Read Pending Articles
        ↓
Call Newspaper Extractor
        ↓
Update MongoDB
        ↓
Move To Next Article
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
# MongoDB
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
    LOG_SEPARATOR,
    PIPELINE_VERSION,
)

# =====================================================
# Extractors
# =====================================================

from extractor.extractors.et_extractor import (
    ETExtractor,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(

    "ExtractWorker"

)
# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(

    MONGO_URI,

    maxPoolSize=20,

    serverSelectionTimeoutMS=5000,

    retryWrites=True,

)

db = client[

    DATABASE_NAME

]

collection = db[

    REALTIME_COLLECTION_NAME

]

# =====================================================
# Extractor Registry
# =====================================================

EXTRACTORS = {

    "Economic Times": ETExtractor(),

    # "The Hindu": TheHinduExtractor(),

    # "Indian Express": IndianExpressExtractor(),

    # "Hindustan Times": HindustanTimesExtractor(),

}

# =====================================================
# Worker Configuration
# =====================================================

PIPELINE_STAGE = "extractor"

DEFAULT_AUTHOR = ["Unknown"]
# =====================================================
# Build Pending Query
# =====================================================

def build_query(
    source_name=None
):
    """
    Build MongoDB query for pending articles.
    """

    query = {

        "status.content_extracted": False,

        "status.content_extract_processing": False,

        "status.content_extract_failed": False,

    }

    if source_name:

        query["source.name"] = source_name

    return query
# =====================================================
# Get Pending Articles
# =====================================================

def get_pending_articles(
    source_name=None
):
    """
    Fetch pending articles from MongoDB.
    """

    query = build_query(
        source_name
    )

    logger.info(LOG_SEPARATOR)
    logger.info("Fetching Pending Articles")
    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Query : {query}"
    )

    articles = list(

        collection.find(

            query

        )

        .sort(

            "published_date",

            1

        )

        .limit(

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
    article_id
):
    """
    Mark an article as currently being processed.
    """

    now = datetime.now(
        UTC
    )

    collection.update_one(

        {

            "_id": article_id

        },

        {

            "$set": {

                "status.content_extract_processing": True,

                "updated_at": now,

                "last_pipeline_update": now,

                "last_pipeline_stage": PIPELINE_STAGE,

                

            }

        }

    )

    logger.info(

        "Article marked as processing."

    )
# =====================================================
# Get Extractor
# =====================================================

def get_extractor(
    source_name
):
    """
    Return extractor instance for a news source.
    """

    extractor = EXTRACTORS.get(
        source_name
    )

    if extractor is None:

        raise ValueError(

            f"No extractor registered for '{source_name}'."

        )

    return extractor
# =====================================================
# Update MongoDB Article
# =====================================================

def update_article(
    article,
    result,
    extract_time
):
    """
    Update extracted article in MongoDB.
    """

    now = datetime.now(
        UTC
    )

    collection.update_one(

        {
            "_id": article["_id"]
        },

        {
            "$set": {

                # =====================================
                # Extracted Fields
                # =====================================

                "title": result.get(
                    "title",
                    ""
                ),

                "description": result.get(
                    "description",
                    ""
                ),

                "authors": result.get(
                    "authors",
                    DEFAULT_AUTHOR
                ),

                "content": result.get(
                    "content",
                    ""
                ),

                "published_date": result.get(
                    "published_date",
                    article.get(
                        "published_date",
                        ""
                    )
                ),

                "extraction_method": result.get(
                    "extraction_method",
                    ""
                ),

                # =====================================
                # Audit
                # =====================================

                "audit.updated_by": "extract_worker",

                "audit.last_updated_stage": "extractor",

                # =====================================
                # Metadata
                # =====================================

                "updated_at": now,

                "last_pipeline_update": now,

                "last_pipeline_stage": PIPELINE_STAGE,

                "error": None,

                # =====================================
                # Processing Metrics
                # =====================================

                "processing.extract_time": extract_time,
                

                "processing.total_time": round(

                    article.get(
                        "processing",
                        {}
                    ).get(
                        "ingestion_time",
                        0
                    )

                    + extract_time,

                    3

                ),

                # =====================================
                # Status
                # =====================================

                "status.content_extracted": True,

                "status.content_extract_processing": False,

                "status.content_extract_failed": False,

                "status.content_extract_retry_count": 0,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "MongoDB Updated"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Title          : {result.get('title', '')}"
    )

    logger.info(
        f"Authors        : {result.get('authors', DEFAULT_AUTHOR)}"
    )

    logger.info(
        f"Content Length : {len(result.get('content', ''))}"
    )

    logger.info(
        f"Extract Time   : {extract_time:.3f} sec"
    )

    logger.info(LOG_SEPARATOR)
# =====================================================
# Process One Article
# =====================================================

def process_article(
    article
):
    """
    Process one article.
    """

    article_id = article["_id"]

    source = article["source"]["name"]

    article_url = article.get(
        "link",
        ""
    )

    logger.info(LOG_SEPARATOR)
    logger.info("Processing Article")
    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Source : {source}"
    )

    logger.info(
        f"URL    : {article_url}"
    )

    # =====================================
    # URL Validation
    # =====================================

    if not article_url:

        logger.warning(
            "Article URL Missing."
        )

        collection.update_one(

            {
                "_id": article_id
            },

            {
                "$set": {

                    "status.content_extract_processing": False,

                    "status.content_extract_failed": True,

                    "status.content_extract_retry_count":
                        article["status"].get(
                            "content_extract_retry_count",
                            0
                        ) + 1,

                    "error": "Missing article URL",

                    "updated_at": datetime.now(
                        UTC
                    ),

                    "last_pipeline_update": datetime.now(
                        UTC
                    ),

                }

            }

        )

        return False

    # =====================================
    # Mark Processing
    # =====================================

    mark_processing(
        article_id
    )

    started = time.perf_counter()

    try:

        extractor = get_extractor(
            source
        )

        result = extractor.extract(
            article_url
        )

        extract_time = round(

            time.perf_counter() - started,

            3

        )

        # =====================================
        # Validate Extraction
        # =====================================

        content = result.get(
            "content",
            ""
        ).strip()

        if len(content) < 100:

            logger.warning(LOG_SEPARATOR)
            logger.warning("Extraction Failed - Empty Content")
            logger.warning(LOG_SEPARATOR)

            collection.update_one(

                {
                    "_id": article_id
                },

                {
                    "$set": {

                        "status.content_extract_processing": False,

                        "status.content_extract_failed": True,

                        "error": "Empty content extracted",

                        "updated_at": datetime.now(
                            UTC
                        ),

                        "last_pipeline_update": datetime.now(
                            UTC
                        ),

                    },

                    "$inc": {

                        "status.content_extract_retry_count": 1

                    }

                }

            )

            return False

        # =====================================
        # Update MongoDB
        # =====================================

        update_article(

            article,

            result,

            extract_time,

        )

        logger.info(LOG_SEPARATOR)
        logger.info("Extraction Successful.")
        logger.info(LOG_SEPARATOR)

        return True

    except Exception as e:

        logger.exception(
            "Extraction Failed"
        )

        retry_count = article["status"].get(
            "content_extract_retry_count",
            0
        ) + 1

        collection.update_one(

            {
                "_id": article_id
            },

            {
                "$set": {

                    "status.content_extract_processing": False,

                    "status.content_extract_failed": True,

                    "status.content_extract_retry_count": retry_count,

                    "error": str(e),

                    "updated_at": datetime.now(
                        UTC
                    ),

                    "last_pipeline_update": datetime.now(
                        UTC
                    ),

                }

            }

        )

        return False
# =====================================================
# Main
# =====================================================

def main():
    """
    Run the content extraction worker.
    """

    logger.info(LOG_SEPARATOR)
    logger.info("Content Extraction Worker")
    logger.info(LOG_SEPARATOR)

    articles = get_pending_articles()

    if not articles:

        logger.info("No pending articles found.")
        logger.info(LOG_SEPARATOR)
        return

    total = len(articles)

    success = 0

    failed = 0

    started = time.perf_counter()

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
    logger.info("Extraction Summary")
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