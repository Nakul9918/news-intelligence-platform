"""
=====================================================
Historical Summary Worker
Version : 1.0
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
    failed = 0
    skipped = 0

    for article in articles:

        try:

            title = article.get("title", "No Title")

            print(f"\nGenerating Summary : {title}")

            clean_content = article.get("clean_content", "")

            if not clean_content.strip():

                skipped += 1

                print("⚠ Skipped : Empty clean content")

                continue

            summary = generate_summary(clean_content)

            if not summary:

                skipped += 1

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

                            "processing_version": 1,

                            "summarized_at": datetime.now(UTC)

                        },

                        "status.summary_done": True,

                        "updated_at": datetime.now(UTC)

                    }

                }

            )

            processed += 1

            print("✓ Summary Completed")

        except Exception as e:

            failed += 1

            print("✗ Failed")
            print("Reason :", e)

    print("\n" + "-" * 70)
    print("Processed :", processed)
    print("Skipped   :", skipped)
    print("Failed    :", failed)

print("\nSummary Worker Finished.")