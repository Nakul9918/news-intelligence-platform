"""
=====================================================
Historical Keyword Worker
Version : 3.0
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


PROCESSING_VERSION = 3
MIN_CONTENT_LENGTH = 100

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]


for collection_name in COLLECTIONS:

    print("\n" + "=" * 70)
    print(f"Keyword Extraction : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find({

        "status.content_cleaned": True,

        "status.keywords_extracted": {
            "$ne": True
        }

    }).limit(PROCESS_BATCH_SIZE)

    processed = 0
    skipped = 0
    failed = 0

    for article in articles:

        try:

            title = article.get("title", "No Title")

            print(f"\nProcessing : {title}")

            cleaned_content = article.get("clean_content", "")

            if not cleaned_content.strip():
                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.keywords_extracted": False,
                            "status.keywords_failed": True,
                            "keyword_error": "Empty cleaned content",
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
                            "status.keywords_extracted": False,
                            "status.keywords_failed": True,
                            "keyword_error": "Content too short",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("Skipped : Content too short")

                continue

            print("Starting keyword extraction...")

            keywords = extract_keywords(cleaned_content)

            print("Keyword extraction finished.")

            collection.update_one(
                {"_id": article["_id"]},
                {
                    "$set": {
                        "keywords": keywords,
                        "keyword_metadata": {
                            "count": len(keywords),
                            "model": "KeyBERT",
                            "embedding_model": "all-MiniLM-L6-v2",
                            "processing_version": PROCESSING_VERSION,
                            "generated_at": datetime.now(UTC)
                        },
                        "status.keywords_extracted": True,
                        "status.keywords_failed": False,
                        "updated_at": datetime.now(UTC)
                    },
                    "$unset": {
                        "keyword_error": "",
                        "failed_at": ""
                    }
                }
            )

            processed += 1

            print(f"✓ {len(keywords)} keywords extracted")

        except Exception as e:

            failed += 1

            print("✗ Failed")
            print(e)

            collection.update_one(
                {"_id": article["_id"]},
                {
                    "$set": {
                        "status.keywords_extracted": False,
                        "status.keywords_failed": True,
                        "keyword_error": str(e),
                        "failed_at": datetime.now(UTC),
                        "updated_at": datetime.now(UTC)
                    }
                }
            )

        print("\n" + "-" * 70)

    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")

print("\nKeyword Worker Finished.")