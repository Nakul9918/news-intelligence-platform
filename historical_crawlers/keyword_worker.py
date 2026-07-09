"""
=====================================================
Historical Keyword Worker
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

from nlp.keyword_extractor import extract_keywords

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
    print(f"Keyword Extraction : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(

        {
            "status.content_cleaned": True,
            "status.keywords_extracted": {
                "$ne": True
            }
        }

    ).limit(PROCESS_BATCH_SIZE)

    processed = 0

    failed = 0

    for article in articles:

        try:

            print(f"Keywords : {article['title']}")

            keywords = extract_keywords(

                article["clean_content"]

            )

            collection.update_one(

                {
                    "_id": article["_id"]
                },

                {
                    "$set": {

                        "keywords": keywords,

                        "status.keywords_extracted": True,

                        "updated_at": datetime.now(UTC)

                    }

                }

            )

            processed += 1

            print("✓ Keywords Extracted")

        except Exception as e:

            failed += 1

            print("✗ Failed")

            print(e)

    print("\nProcessed :", processed)

    print("Failed    :", failed)

print("\nKeyword Worker Finished.")