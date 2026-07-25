"""
=====================================================
Historical NER Worker
Version : 1.0
=====================================================

Reads cleaned articles from MongoDB
and extracts named entities.
"""

from datetime import datetime, UTC
from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.ner import extract_entities
from nlp.models import NER_MODEL


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
    print(f"NER Generation : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(
        {
            "status.summary_done": True,
            "status.ner_done": {
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

            print(f"\nExtracting Entities : {title}")

            clean_content = article.get("clean_content", "")

            if not clean_content.strip():

                skipped += 1

                print("⚠ Skipped : Empty clean content")

                continue

            entities = extract_entities(clean_content)

            if not entities:

                skipped += 1

                print("⚠ Skipped : No entities found")

                continue

            collection.update_one(
                {
                    "_id": article["_id"]
                },
                {
                    "$set": {
                        "entities": entities,
                        "ner_metadata": {
                            "model": NER_MODEL,
                            "processed_at": datetime.now(UTC),
                            "processing_version": "1.0"
                        },
                        "status.ner_done": True
                    }
                }
            )

            processed += 1

            print("✓ Entities extracted successfully")

        except Exception as e:

            failed += 1

            print(f"✗ Error : {e}")

    print("\n" + "-" * 60)
    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")
    print("-" * 60)