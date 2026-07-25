"""
=====================================================
Historical Summary Worker
Version : 2.0
=====================================================

Reads sentiment processed articles from MongoDB
and generates summaries.
"""

from datetime import datetime, UTC
from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.summarizer import generate_summary
from nlp.models import SUMMARIZER_MODEL

# =====================================================
# Configuration
# =====================================================

PROCESSING_VERSION = 2
MIN_CONTENT_LENGTH = 100

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# =====================================================
# Process Collections
# =====================================================

for collection_name in COLLECTIONS:

    print("\n" + "=" * 70)
    print(f"Summary Generation : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(
        {
            "status.sentiment_done": True,
            "status.summary_done": {
                "$ne": True
            }
        }
    ).limit(PROCESS_BATCH_SIZE)

    processed = 0
    skipped = 0
    failed = 0

    for article in articles:

        try:

            title = article.get("title", "No Title")

            print(f"\nGenerating Summary : {title}")

            clean_content = article.get("clean_content", "")

            # -------------------------------------------------
            # Validation
            # -------------------------------------------------

            if not clean_content.strip():

                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.summary_done": False,
                            "status.summary_failed": True,
                            "summary_error": "Empty clean content",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("⚠ Skipped : Empty clean content")

                continue

            if len(clean_content) < MIN_CONTENT_LENGTH:

                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.summary_done": False,
                            "status.summary_failed": True,
                            "summary_error": "Content too short",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("⚠ Skipped : Content too short")

                continue

            summary = generate_summary(clean_content)

            if not summary:

                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.summary_done": False,
                            "status.summary_failed": True,
                            "summary_error": "Summary generation failed",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("⚠ Skipped : Summary generation failed")

                continue

            collection.update_one(

                {
                    "_id": article["_id"]
                },

                {
                    "$set": {

                        "summary": summary,

                        "summary_metadata": {

                            "model": SUMMARIZER_MODEL,

                            "processing_version": PROCESSING_VERSION,

                            "summarized_at": datetime.now(UTC)

                        },

                        "status.summary_done": True,

                        "status.summary_failed": False,

                        "updated_at": datetime.now(UTC)

                    },

                    "$unset": {

                        "summary_error": "",

                        "failed_at": ""

                    }

                }

            )

            processed += 1

            print("✓ Summary Completed")

        except Exception as e:

            failed += 1

            print("✗ Failed")
            print("Reason :", e)

            collection.update_one(
                {
                    "_id": article["_id"]
                },
                {
                    "$set": {

                        "status.summary_done": False,

                        "status.summary_failed": True,

                        "summary_error": str(e),

                        "failed_at": datetime.now(UTC),

                        "updated_at": datetime.now(UTC)

                    }
                }
            )

    print("\n" + "-" * 70)
    print("Processed :", processed)
    print("Skipped   :", skipped)
    print("Failed    :", failed)

print("\n✅ Summary Worker Finished.")