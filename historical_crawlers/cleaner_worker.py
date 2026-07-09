"""
=====================================================
Historical Content Cleaner Worker
Version : 1.0
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

    failed = 0

    for article in articles:

        try:

            print(f"Cleaning : {article['title']}")

            cleaned = clean_content(

                article["content"],

                article.get("source", "")

            )

            collection.update_one(

                {
                    "_id": article["_id"]
                },

                {
                    "$set": {

                        "clean_content": cleaned,

                        "status.content_cleaned": True,

                        "processing_version": 1,

                        "updated_at": datetime.now(UTC)

                    }

                }

            )

            processed += 1

            print("✓ Cleaned")

        except Exception as e:

            failed += 1

            print("✗ Failed")

            print(e)

    print("\nProcessed :", processed)

    print("Failed    :", failed)

print("\nCleaner Worker Finished.")