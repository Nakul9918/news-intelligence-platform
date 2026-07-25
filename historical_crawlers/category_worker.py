"""
=====================================================
Historical Category Worker
Version : 3.0
=====================================================

Reads cleaned news articles from MongoDB
and classifies them using HuggingFace
Zero-Shot Classification.

Features
--------
✓ Batch Processing
✓ Confidence Score
✓ Top-3 Predictions
✓ Processing Metadata
✓ Better Validation
✓ Production Ready
"""

from datetime import datetime, UTC
from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.category_classifier import classify_category

# =====================================================
# Configuration
# =====================================================

PROCESSING_VERSION = 3
MIN_WORDS = 30

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
    print(f"Category Classification : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(

        {

            # Cleaner must finish first
            "status.content_cleaned": True,

            # Keywords must finish first
            "status.keywords_extracted": True,

            # Skip already processed
            "status.category_done": {
                "$ne": True
            }

        }

    ).limit(PROCESS_BATCH_SIZE)

    processed = 0
    skipped = 0
    failed = 0

    for article in articles:

        try:

            title = article.get("title", "")

            content = article.get("clean_content", "")

            print(f"\nProcessing : {title}")

            if not content.strip():

                skipped += 1

                print("Skipped : Empty content")

                continue

            if len(content.split()) < MIN_WORDS:

                skipped += 1

                print("Skipped : Content too short")

                continue

            result = classify_category(
                title,
                content
            )

            # -----------------------------------------------------
            # Validation
            # -----------------------------------------------------

            if (
                result["category"] == "General"
                and result["score"] == 0.0
                and not result["predictions"]
            ):
                failed += 1
                print("✗ Category model unavailable or classification failed")
                continue

            now = datetime.now(UTC)

            collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "category": result["category"],
                    "category_predictions": result["predictions"],
                    "category_metadata": {
                        "score": result["score"],
                        "model": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1",
                        "processing_version": PROCESSING_VERSION,
                        "classified_at": now,
                    },
                    "status.category_done": True,
                    "updated_at": now,
                }}
            )

            processed += 1
            print(f"✓ Category : {result['category']}")
            print(f"✓ Score    : {result['score']}")

        except Exception as e:
            failed += 1
            print("✗ Failed")
            print(e)

    print("\n" + "-" * 70)
    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")

print("\nCategory Worker Finished.")