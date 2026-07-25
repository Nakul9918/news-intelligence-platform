"""
historical_content_extractor.py

Version 8

Processes pending historical articles from MongoDB.

Features
--------
✓ Test one newspaper at a time
✓ Skip already extracted articles
✓ Preserve sitemap title if extractor title is empty
✓ Store authors as ["Unknown"] if missing
✓ Save extraction method
✓ Continue even if one article fails
✓ Process oldest articles first
✓ Skip articles without URL
"""

from datetime import datetime, UTC
import argparse
from pymongo import MongoClient

from historical_crawlers.extractor import extract_article


# =====================================================
# MongoDB Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "news_db"
COLLECTION_NAME = "historical_articles"

BATCH_SIZE = 10


# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# =====================================================
# Command Line Arguments
# =====================================================

parser = argparse.ArgumentParser(
    description="Historical Content Extraction Worker"
)

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument(
    "--source",
    type=str,
    help="Process a specific newspaper"
)

group.add_argument(
    "--all",
    action="store_true",
    help="Process all newspapers"
)

args = parser.parse_args()

# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print("Historical Content Extraction Worker")
    print("=" * 70)

    # =====================================================
    # Build MongoDB Query
    # =====================================================

    query = {
        "content_extracted": {"$ne": True}
    }

    if args.source:
        query["source"] = args.source

    selected_source = args.source if args.source else "ALL SOURCES"

    print(f"\nTesting Source : {selected_source}")
    print(f"Batch Size     : {BATCH_SIZE}")

    pending_articles = (
        collection
        .find(query)
        .sort("published", 1)
        .limit(BATCH_SIZE)
    )

    processed = 0
    success = 0
    failed = 0
    skipped = 0

    for article in pending_articles:

        processed += 1

        article_id = article["_id"]
        source = article.get("source")
        url = article.get("link")

        print("\n" + "=" * 70)
        print(f"[{processed}/{BATCH_SIZE}]")
        print(f"{'Source':<15}: {source}")
        print(f"{'URL':<15}: {url}")

        # -------------------------------------------------
        # Skip if URL missing
        # -------------------------------------------------

        if not url:

            skipped += 1

            collection.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "content_extracted": False,
                        "error": "Missing article URL",
                        "updated_at": datetime.now(UTC)
                    }
                }
            )

            print("⚠ Missing URL - Skipped")
            continue
       
        try:

            result = extract_article(url)

            # --------------------------------------------
            # Extraction failed
            # --------------------------------------------

            if result is None:

                failed += 1

                collection.update_one(
                    {"_id": article_id},
                    {
                        "$set": {
                            "content_extracted": False,
                            "error": "Extraction returned None",
                            "updated_at": datetime.now(UTC)
                        }
                    }
                )

                print("❌ Extraction Failed")
                continue

            title = result.get("title") or article.get("title", "")
            authors = result.get("authors") or ["Unknown"]

            print(f"{'Title':<15}: {title}")
            print(f"{'Authors':<15}: {authors}")

            collection.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "title": title,
                        "authors": authors,
                        "content": result.get("content"),
                        "extraction_method": result.get("method"),
                        "content_extracted": True,
                        "updated_at": datetime.now(UTC),
                        "error": None
                    }
                }
            )

            success += 1

            print("✅ Extraction Successful")

        except Exception as e:

            failed += 1

            collection.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "content_extracted": False,
                        "error": str(e),
                        "updated_at": datetime.now(UTC)
                    }
                }
            )

            print(f"❌ Error : {e}")

    print("\n" + "=" * 70)
    print("Extraction Summary")
    print("=" * 70)

    print(f"{'Testing Source':<18}: {selected_source}")
    print(f"{'Processed':<18}: {processed}")
    print(f"{'Successful':<18}: {success}")
    print(f"{'Failed':<18}: {failed}")
    print(f"{'Skipped':<18}: {skipped}")


# =====================================================
# Program Entry
# =====================================================

if __name__ == "__main__":
    main()