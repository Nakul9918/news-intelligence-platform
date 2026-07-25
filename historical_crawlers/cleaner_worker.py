"""
=====================================================
Historical Content Cleaner Worker
Version : 2.0
=====================================================
"""

from datetime import datetime, UTC

from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.content_cleaner import clean_content


# =====================================================
# Configuration
# =====================================================

MIN_CONTENT_LENGTH = 100

PROCESSING_VERSION = 2


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
    print(f"Cleaning Collection : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(
        {
            "content": {"$exists": True},
            "status.content_cleaned": {"$ne": True}
        }
    ).limit(PROCESS_BATCH_SIZE)

    processed = 0
    skipped = 0
    failed = 0

    for article in articles:

        try:

            title = article.get("title", "Untitled")

            print(f"\nCleaning : {title}")

            original_content = article.get("content", "")

            if not original_content.strip():

                print("⚠ Empty content. Skipping.")

                skipped += 1

                continue

            original_length = len(original_content)

            cleaned = clean_content(
                original_content,
                article.get("source", "")
            )

            cleaned = cleaned.strip()

            cleaned_length = len(cleaned)

            removed_characters = original_length - cleaned_length

            # --------------------------------------------
            # Validation
            # --------------------------------------------

            if cleaned_length < MIN_CONTENT_LENGTH:

                print("⚠ Cleaned content too small. Skipping.")

                collection.update_one(
    {"_id": article["_id"]},
    {
        "$set": {
            "status.content_cleaned": False,
            "status.cleaning_failed": True,
            "cleaning_error": "Content too short after cleaning",
            "failed_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
    }
)

                skipped += 1

                continue

            # --------------------------------------------
            # Save
            # --------------------------------------------

            collection.update_one(
                {"_id": article["_id"]},
                {
                    "$set": {

                        "clean_content": cleaned,

                        "cleaning": {

                            "version": PROCESSING_VERSION,

                            "original_length": original_length,

                            "cleaned_length": cleaned_length,

                            "removed_characters": removed_characters,

                            "cleaned_at": datetime.now(UTC)

                        },

                        "status.content_cleaned": True,

                        "status.cleaning_failed": False,

                        "updated_at": datetime.now(UTC)

                    },

                    "$unset": {
                        "cleaning_error": "",
                        "failed_at": ""
                    }

                }

            )

            processed += 1

            print(
                f"✓ Cleaned "
                f"({original_length} → {cleaned_length} chars)"
            )

        except Exception as e:

            failed += 1

            print(f"✗ Failed : {e}")

            collection.update_one(
                {"_id": article["_id"]},
                {
                    "$set": {
    "status.cleaning_failed": True,
    "cleaning_error": str(e),
    "failed_at": datetime.now(UTC),
    "updated_at": datetime.now(UTC)
}
                }
            )

    print("\n" + "-" * 70)
    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")
    print("-" * 70)

print("\n✅ Cleaner Worker Finished.")