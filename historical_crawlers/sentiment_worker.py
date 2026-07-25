"""
=====================================================
Historical Sentiment Worker
Version : 3.0
=====================================================

Reads cleaned articles from MongoDB
and performs sentiment analysis.
"""

from datetime import datetime, UTC
from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.sentiment import analyze_sentiment


# =====================================================
# Configuration
# =====================================================

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
    print(f"Sentiment Analysis : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(
        {
            "status.keywords_extracted": True,
            "status.sentiment_done": {
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

            print(f"\nAnalyzing : {title}")

            cleaned_content = article.get("clean_content", "")

            # -------------------------------------------------
            # Validation
            # -------------------------------------------------

            if not cleaned_content.strip():

                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.sentiment_done": False,
                            "status.sentiment_failed": True,
                            "sentiment_error": "Empty cleaned content",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("Skipped : Empty content")

                continue

            if len(cleaned_content) < MIN_CONTENT_LENGTH:

                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.sentiment_done": False,
                            "status.sentiment_failed": True,
                            "sentiment_error": "Content too short",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("Skipped : Content too short")

                continue

            result = analyze_sentiment(cleaned_content)

            collection.update_one(
                {
                    "_id": article["_id"]
                },
                {
                    "$set": {

                        "sentiment": result["label"],

                        "sentiment_score": result["score"],

                        "status.sentiment_done": True,

                        "status.sentiment_failed": False,

                        "updated_at": datetime.now(UTC)

                    },

                    "$unset": {

                        "sentiment_error": "",

                        "failed_at": ""

                    }

                }
            )

            processed += 1

            print("✓ Sentiment Completed")
            print(f"Label : {result['label']}")
            print(f"Score : {result['score']}")

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

                        "status.sentiment_done": False,

                        "status.sentiment_failed": True,

                        "sentiment_error": str(e),

                        "failed_at": datetime.now(UTC),

                        "updated_at": datetime.now(UTC)

                    }
                }
            )

    print("\n" + "-" * 70)
    print("Processed :", processed)
    print("Skipped   :", skipped)
    print("Failed    :", failed)

print("\n✅ Sentiment Worker Finished.")