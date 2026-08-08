"""
NER Worker

Processes pending articles and performs
Named Entity Recognition (NER).
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import time

# =====================================================
# MongoDB
# =====================================================

from pymongo import MongoClient

# =====================================================
# Project Configuration
# =====================================================
from config import (
    LOG_SEPARATOR,
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
)

# =====================================================
# NER Utilities
# =====================================================

from ner_pipeline.common_ner import (
    predict_entities,
    build_result,
)

# =====================================================
# Logging
# =====================================================

logger = logging.getLogger(
    "NERWorker"
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
# Pending Query
# =====================================================

PENDING_QUERY = {

    "status.category_done": True,

    "status.ner_done": False,

    "status.ner_processing": False,

    "status.ner_failed": False,

}

# =====================================================
# Statistics
# =====================================================

processed_count = 0

success_count = 0

failed_count = 0

# =====================================================
# Fetch Pending Articles
# =====================================================

def fetch_pending_articles():
    """
    Fetch all pending articles
    waiting for NER.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Fetching Pending Articles"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Query : {PENDING_QUERY}"
    )

    articles = list(

        collection.find(
            PENDING_QUERY
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
    Mark article as
    currently processing.
    """

    collection.update_one(

        {
            "_id": article_id
        },

        {
            "$set": {

                "status.ner_processing": True

            }

        }

    )

    logger.info(
        "Article marked for NER."
    )

# =====================================================
# Update Success
# =====================================================

def update_success(
    article_id,
    result,
    processing_time,
):
    """
    Update MongoDB after
    successful NER.
    """

    collection.update_one(

        {
            "_id": article_id
        },

        {
            "$set": {

                "ner": result,

                "status.ner_done": True,

                "status.ner_processing": False,

                "processing.ner_time": processing_time,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "MongoDB Updated"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Entities      : {result['entity_count']}"
    )

    logger.info(
        f"Model         : {result['model']}"
    )

    logger.info(
        f"Process Time  : {processing_time:.3f} sec"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "NER Successful."
    )

# =====================================================
# Update Failure
# =====================================================

def update_failure(
    article_id,
):
    """
    Update MongoDB after
    failed NER.
    """

    collection.update_one(

        {
            "_id": article_id
        },

        {
            "$set": {

                "status.ner_failed": True,

                "status.ner_processing": False,

            }

        }

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "MongoDB Updated"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Article marked as failed."
    )

    logger.info(LOG_SEPARATOR)

# =====================================================
# Process Articles
# =====================================================

def process_articles():
    """
    Process all pending articles.
    """

    global processed_count

    global success_count

    global failed_count

    start_time = time.perf_counter()

    articles = fetch_pending_articles()

    for article in articles:

        logger.info(LOG_SEPARATOR)

        logger.info(
            "NER"
        )

        logger.info(LOG_SEPARATOR)

        logger.info(
            f"Source : {article.get('source')}"
        )

        logger.info(
            f"URL    : {article.get('url')}"
        )

        article_id = article["_id"]

        try:

            mark_processing(
                article_id
            )

            process_start = time.perf_counter()

            entities = predict_entities(

                article.get(
                    "content",
                    ""
                )

            )

            result = build_result(
                entities
            )

            processing_time = (

                time.perf_counter()

                - process_start

            )

            update_success(

                article_id,

                result,

                processing_time,

            )

            processed_count += 1

            success_count += 1

        except Exception as error:

            logger.exception(

                f"NER Failed : {error}"

            )

            update_failure(
                article_id
            )

            processed_count += 1

            failed_count += 1

    total_time = (

        time.perf_counter()

        - start_time

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "NER Summary"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Processed  : {processed_count}"
    )

    logger.info(
        f"Successful : {success_count}"
    )

    logger.info(
        f"Failed     : {failed_count}"
    )

    logger.info(
        f"Total Time : {total_time:.3f} sec"
    )

    logger.info(LOG_SEPARATOR)

# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    logging.basicConfig(

        level=logging.INFO,

        format="%(asctime)s | %(levelname)s | %(message)s",

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "NER Worker"
    )

    logger.info(LOG_SEPARATOR)

    process_articles()