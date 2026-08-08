"""
Event Detection Worker

Processes pending articles and updates
MongoDB with detected events.
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import time

# =====================================================
# Third Party Libraries
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
# Common Event Utilities
# =====================================================

from event_pipeline.common_event import (

    predict_event,

    build_result,

)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)

logger = logging.getLogger(
    "EventWorker"
)

# =====================================================
# MongoDB
# =====================================================

client = MongoClient(
    MONGO_URI
)

db = client[
    DATABASE_NAME
]

collection = db[
    REALTIME_COLLECTION_NAME
]

"""
Event Detection Worker

Processes pending articles and updates
MongoDB with detected events.
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import time

# =====================================================
# Third Party Libraries
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
# Common Event Utilities
# =====================================================

from event_pipeline.common_event import (

    predict_event,

    build_result,

)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)

logger = logging.getLogger(
    "EventWorker"
)

# =====================================================
# MongoDB
# =====================================================

client = MongoClient(
    MONGO_URI
)

db = client[
    DATABASE_NAME
]

collection = db[
    REALTIME_COLLECTION_NAME
]
# =====================================================
# Fetch Pending Articles
# =====================================================

def fetch_pending_articles():
    """
    Fetch articles waiting for
    event detection.
    """

    query = {

    "status.ner_done": True,

    "$and": [

        {
            "$or": [

                {
                    "status.event_done": False
                },

                {
                    "status.event_done": {
                        "$exists": False
                    }
                }

            ]
        },

        {
            "$or": [

                {
                    "status.event_processing": False
                },

                {
                    "status.event_processing": {
                        "$exists": False
                    }
                }

            ]
        },

        {
            "$or": [

                {
                    "status.event_failed": False
                },

                {
                    "status.event_failed": {
                        "$exists": False
                    }
                }

            ]
        }

    ]

}

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
        )

    )

    logger.info(
        f"Pending Articles : {len(articles)}"
    )

    logger.info(LOG_SEPARATOR)

    return articles

# =====================================================
# Process One Article
# =====================================================

def process_article(
    article
):
    """
    Process one article for
    event detection.
    """

    start_time = time.time()

    article_id = article["_id"]

    source = article.get(
        "source",
        ""
    )

    url = article.get(
        "url",
        ""
    )

    content = article.get(
        "clean_content",
        ""
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Event Detection"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Source : {source}"
    )

    logger.info(
        f"URL    : {url}"
    )

    try:

        collection.update_one(

            {

                "_id": article_id

            },

            {

                "$set": {

                    "status.event_processing": True

                }

            }

        )

        logger.info(
            "Article marked for event detection."
        )

        event = predict_event(
            content
        )

        result = build_result(
            event
        )

        process_time = round(

            time.time() - start_time,

            3,

        )

        collection.update_one(

            {

                "_id": article_id

            },

            {

                "$set": {

                    "event": result,

                    "status.event_done": True,

                    "status.event_processing": False,

                    "status.event_failed": False,

                }

            }

        )

        logger.info(LOG_SEPARATOR)

        logger.info(
            "MongoDB Updated"
        )

        logger.info(LOG_SEPARATOR)

        logger.info(
            f"Event         : {result['label']}"
        )

        logger.info(
            f"Confidence    : {result['score']}"
        )

        logger.info(
            f"Model         : {result['model']}"
        )

        logger.info(
            f"Process Time  : {process_time} sec"
        )

        logger.info(LOG_SEPARATOR)

        logger.info(
            "Event Detection Successful."
        )

    except Exception as error:

        logger.exception(
            f"Event Detection Failed : {error}"
        )

        collection.update_one(

            {

                "_id": article_id

            },

            {

                "$set": {

                    "status.event_processing": False,

                    "status.event_failed": True,

                }

            }

        )

        return False

    return True

# =====================================================
# Main
# =====================================================

def main():
    """
    Event Detection Pipeline
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Event Detection Worker"
    )

    logger.info(LOG_SEPARATOR)

    articles = fetch_pending_articles()

    total = len(articles)

    success = 0

    failed = 0

    pipeline_start = time.time()

    for article in articles:

        if process_article(article):

            success += 1

        else:

            failed += 1

    total_time = round(

        time.time() - pipeline_start,

        3,

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Event Detection Summary"
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
        f"Total Time : {total_time} sec"
    )

    logger.info(LOG_SEPARATOR)


# =====================================================
# Run
# =====================================================

if __name__ == "__main__":

    main()