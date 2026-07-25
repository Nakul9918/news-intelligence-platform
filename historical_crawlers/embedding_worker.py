"""
======================================================
Historical Embedding Worker

Version : 1.0
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

PROCESSING_VERSION = 1.0


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
            "status.embedding_done": {"$ne": True}
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

            if not clean_content.strip():

                print("⚠ Empty clean content. Skipping.")

                skipped += 1

                continue

            embedding = generate_embedding(clean_content)

            if not embedding:

                print("⚠ Failed to generate embedding.")

                failed += 1

                continue

            collection.update_one(
                {
                    "_id": article["_id"]
                },
                {
                    "$set": {

                        "embedding": embedding,

                        "embedding_metadata": {

                            "model": "sentence-transformers/all-MiniLM-L6-v2",

                            "dimension": len(embedding),

                            "processed_at": datetime.now(UTC),

                            "processing_version": PROCESSING_VERSION

                        },

                        "status.embedding_done": True

                    }
                }
            )

            print(
                f"✓ Embedding Generated "
                f"({len(embedding)} dimensions)"
            )

            processed += 1

        except Exception as e:

            print(f"✗ Failed : {e}")

            failed += 1

    print("\n" + "-" * 70)
    print(f"Processed : {processed}")
    print(f"Skipped   : {skipped}")
    print(f"Failed    : {failed}")
    print("-" * 70)

print("\n✅ Embedding Worker Finished.")