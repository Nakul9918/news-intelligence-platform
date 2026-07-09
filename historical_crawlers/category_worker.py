"""
=====================================================
Historical Category Worker
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

from nlp.category_classifier import classify_category

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

for collection_name in COLLECTIONS:

    print("\n" + "=" * 70)
    print(f"Category Worker : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(

        {
            "status.sentiment_done": True,
            "status.category_done": {
                "$ne": True
            }
        }

    ).limit(PROCESS_BATCH_SIZE)

    processed = 0

    failed = 0

    for article in articles:

        try:

            print(f"Classifying : {article['title']}")

            category = classify_category(

                article["clean_content"]

            )

            collection.update_one(

                {
                    "_id": article["_id"]
                },

                {
                    "$set": {

                        "category": category,

                        "status.category_done": True,

                        "updated_at": datetime.now(UTC)

                    }

                }

            )

            processed += 1

            print(f"✓ {category}")

        except Exception as e:

            failed += 1

            print(e)

    print(f"\nProcessed : {processed}")

    print(f"Failed    : {failed}")

print("\nCategory Worker Finished.")