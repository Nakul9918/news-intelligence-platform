# # from pymongo import MongoClient
# # from realtime_pipeline.realtime_nlp_pipeline import process_article

# # # MongoDB Connection
# # client = MongoClient("mongodb://localhost:27017")

# # db = client["news_db"]

# # COLLECTION_NAME = "historical_urls_et"
# # BATCH_SIZE = 10

# # collection = db[COLLECTION_NAME]


# # def process_batch():

# #     articles = list(
# #         collection.find(
# #             {
# #                 "processed": {"$exists": False}
# #             }
# #         ).limit(BATCH_SIZE)
# #     )

# #     if not articles:
# #         print("No unprocessed articles found.")
# #         return

# #     print(f"\nFound {len(articles)} articles.\n")

# #     success = 0
# #     failed = 0

# #     for i, article in enumerate(articles, start=1):

# #         print("=" * 70)
# #         print(f"[{i}/{len(articles)}]")
# #         print("Title :", article.get("title"))
# #         print("ID    :", article["_id"])

# #         try:

# #             process_article(
# #                 article["_id"],
# #                 collection
# #             )

# #             success += 1

# #             print("✅ Processed Successfully")

# #         except Exception as e:

# #             failed += 1

# #             print("❌ Failed")
# #             print(e)

# #     print("\n" + "=" * 70)
# #     print("Batch Completed")
# #     print(f"Success : {success}")
# #     print(f"Failed  : {failed}")
# #     print("=" * 70)


# # if __name__ == "__main__":
# #     process_batch()

# """
# =====================================================
# Historical News Processor
# Project : News Intelligence Platform
# Module  : historical_processor
# Version : 1.0
# =====================================================
# """

# from __future__ import annotations

# import logging
# import time
# from datetime import datetime
# from typing import Any

# from pymongo import MongoClient
# from pymongo.collection import Collection
# from pymongo.errors import PyMongoError


# # =====================================================
# # Logger
# # =====================================================

# logging.basicConfig(

#     level=logging.INFO,

#     format="%(asctime)s | %(levelname)s | %(message)s"

# )

# logger = logging.getLogger(__name__)

# # =====================================================
# # MongoDB Configuration
# # =====================================================

# MONGO_URI = "mongodb://localhost:27017"

# DATABASE_NAME = "news_db"

# COLLECTION_NAME = "historical_urls_et"

# BATCH_SIZE = 10

# # =====================================================
# # Runtime Metrics
# # =====================================================

# MODULE_START_TIME = time.time()

# TOTAL_BATCHES = 0

# TOTAL_ARTICLES = 0

# SUCCESSFUL_ARTICLES = 0

# FAILED_ARTICLES = 0

# LAST_BATCH_TIME = None

# # =====================================================
# # MongoDB Connection
# # =====================================================

# client = MongoClient(MONGO_URI)

# db = client[DATABASE_NAME]

# collection: Collection = db[COLLECTION_NAME]

# # =====================================================
# # Runtime Statistics
# # =====================================================

# def runtime_statistics() -> dict[str, Any]:

#     return {

#         "uptime_seconds": round(

#             time.time() - MODULE_START_TIME,

#             2,

#         ),

#         "total_batches": TOTAL_BATCHES,

#         "total_articles": TOTAL_ARTICLES,

#         "successful_articles": SUCCESSFUL_ARTICLES,

#         "failed_articles": FAILED_ARTICLES,

#         "last_batch_time": LAST_BATCH_TIME,

#     }

# # =====================================================
# # Health Check
# # =====================================================

# def health_check() -> dict[str, Any]:

#     try:

#         client.admin.command("ping")

#         mongodb_status = "connected"

#     except Exception:

#         mongodb_status = "disconnected"

#     return {

#         "status": "healthy",

#         "mongodb": mongodb_status,

#         "database": DATABASE_NAME,

#         "collection": COLLECTION_NAME,

#         "batch_size": BATCH_SIZE,

#         "runtime": runtime_statistics(),

#     }

# # =====================================================
# # Load Batch
# # =====================================================

# def load_batch():

#     return list(

#         collection.find(

#             {

#                 "processed": {

#                     "$exists": False

#                 }

#             }

#         ).limit(BATCH_SIZE)

#     )

# # =====================================================
# # Public API
# # =====================================================

# __all__ = [

#     "collection",

#     "load_batch",

#     "runtime_statistics",

#     "health_check",

# ]
# # =====================================================
# # Process Single Article
# # =====================================================

# def process_single_article(
#     article: dict[str, Any],
# ) -> bool:
#     """
#     Process a single article through the NLP pipeline.
#     Returns True on success, False on failure.
#     """

#     global SUCCESSFUL_ARTICLES
#     global FAILED_ARTICLES

#     article_id = article.get("_id")

#     title = article.get(
#         "title",
#         "Untitled",
#     )

#     logger.info(
#         "=" * 70
#     )

#     logger.info(
#         "Processing: %s",
#         title,
#     )

#     start_time = time.perf_counter()

#     try:

#         # Lazy import
#         from realtime_pipeline.realtime_nlp_pipeline import (
#             process_article,
#         )

#         process_article(
#             article_id,
#             collection,
#         )

#         processing_time = round(
#             time.perf_counter()
#             - start_time,
#             2,
#         )

#         SUCCESSFUL_ARTICLES += 1

#         logger.info(
#             "SUCCESS | %.2f sec",
#             processing_time,
#         )

#         return True

#     except Exception as exc:

#         FAILED_ARTICLES += 1

#         logger.exception(
#             "FAILED | %s",
#             exc,
#         )

#         return False
# # =====================================================
# # Process Batch
# # =====================================================

# def process_batch() -> None:
#     """
#     Process one batch of historical articles.
#     """

#     global TOTAL_BATCHES
#     global TOTAL_ARTICLES
#     global LAST_BATCH_TIME

#     batch = load_batch()

#     if not batch:

#         logger.info(
#             "No unprocessed articles found."
#         )

#         return

#     TOTAL_BATCHES += 1

#     TOTAL_ARTICLES += len(batch)

#     logger.info("=" * 70)

#     logger.info(
#         "Starting Batch #%d",
#         TOTAL_BATCHES,
#     )

#     logger.info(
#         "Articles Found : %d",
#         len(batch),
#     )

#     logger.info("=" * 70)

#     batch_start = time.perf_counter()

#     success = 0

#     failed = 0

#     for index, article in enumerate(

#         batch,

#         start=1,

#     ):

#         logger.info(

#             "[%d/%d]",

#             index,

#             len(batch),

#         )

#         if process_single_article(article):

#             success += 1

#         else:

#             failed += 1

#     LAST_BATCH_TIME = datetime.utcnow().isoformat()

#     batch_time = round(

#         time.perf_counter()
#         - batch_start,

#         2,

#     )

#     logger.info("=" * 70)

#     logger.info("Batch Completed")

#     logger.info(
#         "Processed : %d",
#         len(batch),
#     )

#     logger.info(
#         "Success  : %d",
#         success,
#     )

#     logger.info(
#         "Failed   : %d",
#         failed,
#     )

#     logger.info(
#         "Time     : %.2f sec",
#         batch_time,
#     )

#     logger.info("=" * 70)
# if __name__ == "__main__":

#     process_batch()


"""
=====================================================
Historical News Processor
News Intelligence Platform
Version : 2.0
=====================================================
"""

from __future__ import annotations
import logging
import time
from datetime import UTC
from datetime import datetime
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from historical_crawlers.extractor import extract_article

# =====================================================
# Logger
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# =====================================================
# Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "news_db"

COLLECTIONS = [
    "historical_urls_et",
    "historical_urls_hindustantimes",
    "historical_urls_indianexpress",
    "historical_urls_thehindu",
]

BATCH_SIZE = 10

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

# =====================================================
# Runtime Statistics
# =====================================================

MODULE_START_TIME = time.time()

TOTAL_BATCHES = 0

TOTAL_ARTICLES = 0

SUCCESSFUL_ARTICLES = 0

FAILED_ARTICLES = 0

LAST_BATCH_TIME = None


def runtime_statistics() -> dict[str, Any]:
    """
    Return runtime statistics.
    """

    return {

        "uptime_seconds": round(
            time.time() - MODULE_START_TIME,
            2,
        ),

        "total_batches": TOTAL_BATCHES,

        "total_articles": TOTAL_ARTICLES,

        "successful_articles": SUCCESSFUL_ARTICLES,

        "failed_articles": FAILED_ARTICLES,

        "last_batch_time": LAST_BATCH_TIME,

    }

# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Check MongoDB connection.
    """

    try:

        client.admin.command("ping")

        status = "connected"

    except PyMongoError:

        status = "disconnected"

    return {

    "status": status,

    "database": DATABASE_NAME,

    "collections": COLLECTIONS,

    "batch_size": BATCH_SIZE,

    "runtime": runtime_statistics(),

}
def load_batch(
    collection: Collection,
) -> list[dict[str, Any]]:
    """
    Load one batch of pending articles.
    """

    return list(

        collection.find(
            {
                "nlp_completed": {
                    "$ne": True
                }
            }
        )
        .sort("_id", 1)
        .limit(BATCH_SIZE)

    )

# =====================================================
# Remaining Articles
# =====================================================

def remaining_articles(collection: Collection,) -> int:
    """
    Return number of articles still pending NLP.
    """

    return collection.count_documents(
        {
            "nlp_completed": {
                "$ne": True
            }
        }
    )
# =====================================================
# Collection Statistics
# =====================================================

def collection_statistics(
    collection: Collection,
    remaining: int,
) -> dict[str, int | float]:
    """
    Return collection progress statistics.
    """

    total = collection.estimated_document_count()

    completed = total - remaining

    percentage = round(
        (completed / total) * 100,
        2,
    ) if total else 0

    return {

        "total": total,

        "completed": completed,

        "remaining": remaining,

        "percentage": percentage,

    }
# =====================================================
# Decision Engine
# =====================================================

def decide_next_step(
    article: dict[str, Any],
) -> str:
    """
    Decide what action should be taken for an article.
    """

    if not article.get("link"):

        return "SKIP"

    if not article.get("content"):

        return "EXTRACT_CONTENT"

    if article.get("nlp_completed") is True:

        return "SKIP"

    return "RUN_NLP"
# =====================================================
# Process Single Article
# =====================================================

def process_single_article(
    article: dict[str, Any],
    collection: Collection,
) -> bool:
    """
    Process one historical article.
    """

    action = decide_next_step(article)

    print(f"Action : {action}")

    # -------------------------------------------------
    # Skip
    # -------------------------------------------------

    if action == "SKIP":
        return True

    # -------------------------------------------------
    # Extract Content + Run NLP
    # -------------------------------------------------

    if action == "EXTRACT_CONTENT":

        result = extract_article(article["link"])

        if result is None:

            print("❌ Content extraction failed.")
            return False

        collection.update_one(
            {"_id": article["_id"]},
            {
                "$set": {
                    "title": result["title"],
                    "authors": result["authors"],
                    "content": result["content"],
                    "content_length": len(result["content"]),
                    "content_extracted": True,
                    "extraction_method": result["method"],
                    "updated_at": datetime.now(UTC),
                }
            },
        )

        print("✅ Content saved to MongoDB.")

        # Reload updated article
        article = collection.find_one(
            {"_id": article["_id"]}
        )

        print("\nStarting NLP Pipeline...")

        from realtime_pipeline.realtime_nlp_pipeline import (
            process_article,
        )

        process_article(
            article["_id"],
            collection,
        )

        print("✅ NLP Completed")

        return True

# -------------------------------------------------
# Run NLP Only
# -------------------------------------------------
    if action == "RUN_NLP":

        

        from realtime_pipeline.realtime_nlp_pipeline import (
            process_article,
        )

        process_article(
            article["_id"],
            collection,
    )

    print("✅ Realtime NLP completed.")

    return True
    # -------------------------------------------------
    # Unknown Action
    # -------------------------------------------------

    return False
# Temp
if __name__ == "__main__":

    total_success = 0
    total_failed = 0
    total_skipped = 0

    overall_start = time.perf_counter()

    for collection_name in COLLECTIONS:

        collection = db[collection_name]

        remaining = remaining_articles(collection)

        print("\n" + "=" * 80)
        print(f"Processing Collection : {collection_name}")
        print(f"Pending Articles      : {remaining:,}")
        print("=" * 80)

        if remaining == 0:

            print(f"✅ {collection_name} already completed.")
            continue

        batch_number = 1

        collection_start = time.perf_counter()

        while True:

            batch_start = time.perf_counter()

            batch = load_batch(collection)

            if not batch:

                print("\n" + "=" * 70)
                print(f"✅ Collection Completed : {collection_name}")
                print(
                    f"Collection Time : "
                    f"{round(time.perf_counter() - collection_start, 2)} sec"
                )
                print("=" * 70)
                break

            remaining = remaining_articles(collection)

            stats = collection_statistics(
                collection,
                remaining,
            )

            batch_success = 0
            batch_failed = 0
            batch_skipped = 0

            print("\n" + "=" * 70)
            print(f"Collection         : {collection_name}")
            print(f"Batch              : {batch_number}")
            print(f"Articles Loaded    : {len(batch)}")
            print(f"Total Articles     : {stats['total']:,}")
            print(f"Completed          : {stats['completed']:,}")
            print(f"Remaining          : {stats['remaining']:,}")
            print(f"Progress           : {stats['percentage']}%")
            print("=" * 70)

            for index, article in enumerate(batch, start=1):

                print("\n" + "-" * 60)
                print(f"Processing Article {index} of {len(batch)}")
                print("-" * 60)

                try:

                    status = process_single_article(
                        article,
                        collection,
                    )

                    if status:

                        batch_success += 1
                        total_success += 1

                        print("✅ Article Completed")

                    else:

                        batch_skipped += 1
                        total_skipped += 1

                        print("⏭ Article Skipped")

                except KeyboardInterrupt:

                    print("\nInterrupted by user.")
                    raise

                except Exception as e:

                    batch_failed += 1
                    total_failed += 1

                    logger.exception(e)

                    collection.update_one(
                        {
                            "_id": article["_id"]
                        },
                        {
                            "$set": {
                                "processing_error": str(e),
                                "last_failed_at": datetime.now(),
                            }
                        }
                    )

                    print(
                        f"❌ Article Failed : "
                        f"{article.get('title', 'Unknown')}"
                    )
                    print(f"Reason            : {e}")

            batch_time = round(
                time.perf_counter() - batch_start,
                2,
            )

            print("\n" + "=" * 70)
            print("Batch Summary")
            print("=" * 70)
            print(f"Success           : {batch_success}")
            print(f"Failed            : {batch_failed}")
            print(f"Skipped           : {batch_skipped}")
            print(f"Batch Time        : {batch_time} sec")
            print("=" * 70)

            print("Overall Progress")
            print("=" * 70)
            print(f"Success           : {total_success}")
            print(f"Failed            : {total_failed}")
            print(f"Skipped           : {total_skipped}")
            print("=" * 70)

            batch_number += 1

    overall_time = round(
        time.perf_counter() - overall_start,
        2,
    )

    print("\n" + "=" * 80)
    print("🎉 ALL COLLECTIONS COMPLETED")
    print("=" * 80)
    print(f"Total Success : {total_success}")
    print(f"Total Failed  : {total_failed}")
    print(f"Total Skipped : {total_skipped}")
    print(f"Total Runtime : {overall_time} sec")
    print("=" * 80) 