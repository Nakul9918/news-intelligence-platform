import logging
import time

from pymongo import MongoClient

from config import (
    LOG_SEPARATOR,
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
)

from summary_pipeline.common_summary import generate_summary


logger = logging.getLogger("SummaryWorker")


# ============================================================
# MONGODB
# ============================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

collection = db[REALTIME_COLLECTION_NAME]


# ============================================================
# CONTENT EXTRACTION
# ============================================================

def get_article_text(article):
    """
    Get usable article text from MongoDB document.
    Supports common content field structures.
    """

    possible_fields = [
        "cleaned_content",
        "clean_content",
        "content",
        "article_text",
        "text",
        "description",
        "summary",
    ]

    for field in possible_fields:

        value = article.get(field)

        if isinstance(value, str) and value.strip():
            return value

        if isinstance(value, dict):

            for subfield in [
                "cleaned_text",
                "clean_text",
                "text",
                "body",
                "content",
            ]:

                subvalue = value.get(subfield)

                if isinstance(subvalue, str) and subvalue.strip():
                    return subvalue

    return ""


# ============================================================
# FETCH PENDING ARTICLES
# ============================================================

def fetch_pending_articles():

    logger.info(LOG_SEPARATOR)

    logger.info("Fetching Pending Articles")

    logger.info(LOG_SEPARATOR)

    query = {
        "status.ner_done": True,
        "$or": [
            {
                "status.summary_done": False
            },
            {
                "status.summary_done": {
                    "$exists": False
                }
            }
        ],
        "$and": [
            {
                "$or": [
                    {
                        "status.summary_processing": False
                    },
                    {
                        "status.summary_processing": {
                            "$exists": False
                        }
                    }
                ]
            },
            {
                "$or": [
                    {
                        "status.summary_failed": False
                    },
                    {
                        "status.summary_failed": {
                            "$exists": False
                        }
                    }
                ]
            }
        ]
    }

    articles = list(
        collection.find(query)
    )

    logger.info(
        f"Pending Articles : {len(articles)}"
    )

    return articles


# ============================================================
# PROCESS ARTICLE
# ============================================================

def process_article(article):

    article_id = article["_id"]

    title = article.get(
        "title",
        ""
    )

    logger.info(LOG_SEPARATOR)

    logger.info("Summary Generation")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Article ID : {article_id}"
    )

    logger.info(
        f"Title      : {title}"
    )

    # Mark processing
    collection.update_one(
        {"_id": article_id},
        {
            "$set": {
                "status.summary_processing": True,
                "status.summary_failed": False
            }
        }
    )

    start_time = time.time()

    try:

        text = get_article_text(article)

        if not text:

            raise ValueError(
                "No article content found."
            )

        summary = generate_summary(
            text
        )

        if not summary:

            raise ValueError(
                "Summary generation returned empty result."
            )

        process_time = time.time() - start_time

        collection.update_one(
            {"_id": article_id},
            {
                "$set": {
                    "summary": {
                        "text": summary,
                        "model": "facebook/bart-large-cnn"
                    },

                    "status.summary_done": True,
                    "status.summary_processing": False,
                    "status.summary_failed": False
                }
            }
        )

        logger.info(LOG_SEPARATOR)

        logger.info("MongoDB Updated")

        logger.info(LOG_SEPARATOR)

        logger.info(
            f"Summary     : {summary}"
        )

        logger.info(
            f"Process Time: {process_time:.2f} sec"
        )

        logger.info("Summary Generation Successful.")

        return True

    except Exception as e:

        collection.update_one(
            {"_id": article_id},
            {
                "$set": {
                    "status.summary_processing": False,
                    "status.summary_failed": True
                },

                "$inc": {
                    "status.summary_retry_count": 1
                }
            }
        )

        logger.error(
            f"Summary Generation Failed: {e}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(LOG_SEPARATOR)

    logger.info("Summary Worker")

    logger.info(LOG_SEPARATOR)

    articles = fetch_pending_articles()

    processed = 0
    successful = 0
    failed = 0

    start_time = time.time()

    for article in articles:

        processed += 1

        if process_article(article):
            successful += 1
        else:
            failed += 1

    total_time = time.time() - start_time

    logger.info(LOG_SEPARATOR)

    logger.info("Summary Generation Summary")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Processed  : {processed}"
    )

    logger.info(
        f"Successful : {successful}"
    )

    logger.info(
        f"Failed     : {failed}"
    )

    logger.info(
        f"Total Time : {total_time:.1f} sec"
    )

    logger.info(LOG_SEPARATOR)


if __name__ == "__main__":

    main()