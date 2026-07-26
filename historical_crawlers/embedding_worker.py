"""
======================================================
Historical Embedding Worker

Version : 2.0
======================================================

Generates sentence embeddings for cleaned news articles.
"""

from datetime import datetime, UTC

from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.embeddings import generate_embedding


# =====================================================
# Configuration
# =====================================================

PROCESSING_VERSION = 2
MIN_CONTENT_LENGTH = 100

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
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
    print(f"Embedding Generation : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(
        {
            "status.content_cleaned": True,
            "status.embedding_done": {
                "$ne": True
            }
        }
    ).limit(PROCESS_BATCH_SIZE)

    processed = 0
    skipped = 0
    failed = 0

    for article in articles:

        try:

            title = article.get("title", "Untitled")

            print(f"\nGenerating Embedding : {title}")

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
                            "status.embedding_done": False,
                            "status.embedding_failed": True,
                            "embedding_error": "Empty clean content",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("⚠ Empty clean content. Skipping.")

                continue

            if len(clean_content) < MIN_CONTENT_LENGTH:

                skipped += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.embedding_done": False,
                            "status.embedding_failed": True,
                            "embedding_error": "Content too short",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("⚠ Content too short. Skipping.")

                continue

            embedding = generate_embedding(clean_content)

            if not embedding:

                failed += 1

                collection.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "status.embedding_done": False,
                            "status.embedding_failed": True,
                            "embedding_error": "Embedding generation failed",
                            "failed_at": datetime.now(UTC),
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("⚠ Failed to generate embedding.")

                continue

            collection.update_one(
                {
                    "_id": article["_id"]
                },
                {
                    "$set": {

                        "embedding": embedding,

                        "embedding_metadata": {

                            "model": EMBEDDING_MODEL,

                            "dimension": EMBEDDING_DIMENSION,

                            "processed_at": datetime.now(UTC),

                            "processing_version": PROCESSING_VERSION

                        },

                        "status.embedding_done": True,

                        "status.embedding_failed": False,

                        "updated_at": datetime.now(UTC)

                    },

                    "$unset": {

                        "embedding_error": "",

                        "failed_at": ""

                    }

                }
            )

            processed += 1

            print(
                f"✓ Embedding Generated "
                f"({len(embedding)} dimensions)"
            )

        except Exception as e:

            failed += 1

            print(f"✗ Failed : {e}")

            collection.update_one(
                {
                    "_id": article["_id"]
                },
                {
                    "$set": {

                        "status.embedding_done": False,

                        "status.embedding_failed": True,

                        "embedding_error": str(e),

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

print("\n✅ Embedding Worker Finished.")