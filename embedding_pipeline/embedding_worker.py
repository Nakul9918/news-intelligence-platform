import logging
import time

from pymongo import MongoClient

from config import (
    LOG_SEPARATOR,
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
)

from embedding_pipeline.common_embedding import generate_embedding


logger = logging.getLogger("EmbeddingWorker")


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
                "status.embedding_done": False
            },
            {
                "status.embedding_done": {
                    "$exists": False
                }
            }
        ],
        "$and": [
            {
                "$or": [
                    {
                        "status.embedding_processing": False
                    },
                    {
                        "status.embedding_processing": {
                            "$exists": False
                        }
                    }
                ]
            },
            {
                "$or": [
                    {
                        "status.embedding_failed": False
                    },
                    {
                        "status.embedding_failed": {
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

    logger.info("Embedding Generation")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Article ID : {article_id}"
    )

    logger.info(
        f"Title      : {title}"
    )

    collection.update_one(
        {"_id": article_id},
        {
            "$set": {
                "status.embedding_processing": True,
                "status.embedding_failed": False
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

        embedding = generate_embedding(
            text
        )

        if not embedding:

            raise ValueError(
                "Embedding generation returned empty vector."
            )

        process_time = time.time() - start_time

        collection.update_one(
            {"_id": article_id},
            {
                "$set": {
                    "embedding": {
                        "vector": embedding,
                        "dimension": len(embedding),
                        "model": "sentence-transformers/all-MiniLM-L6-v2"
                    },

                    "status.embedding_done": True,
                    "status.embedding_processing": False,
                    "status.embedding_failed": False
                }
            }
        )

        logger.info(LOG_SEPARATOR)

        logger.info("MongoDB Updated")

        logger.info(LOG_SEPARATOR)

        logger.info(
            f"Dimension   : {len(embedding)}"
        )

        logger.info(
            f"Model       : sentence-transformers/all-MiniLM-L6-v2"
        )

        logger.info(
            f"Process Time: {process_time:.2f} sec"
        )

        logger.info(
            "Embedding Generation Successful."
        )

        return True

    except Exception as e:

        collection.update_one(
            {"_id": article_id},
            {
                "$set": {
                    "status.embedding_processing": False,
                    "status.embedding_failed": True
                },

                "$inc": {
                    "status.embedding_retry_count": 1
                }
            }
        )

        logger.error(
            f"Embedding Generation Failed: {e}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(LOG_SEPARATOR)

    logger.info("Embedding Worker")

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

    logger.info("Embedding Generation Summary")

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