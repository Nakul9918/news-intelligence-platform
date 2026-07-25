# from pymongo import MongoClient
# from datetime import datetime, UTC

# from config import (
#     MONGO_URI,
#     DATABASE_NAME,
#     COLLECTIONS,
#     PROCESS_BATCH_SIZE
# )
        
# # =====================================================
# # MongoDB Connection
# # =====================================================

# client = MongoClient(MONGO_URI)

# db = client[DATABASE_NAME]

# # =====================================================
# # Process Collections
# # =====================================================

# for collection_name in COLLECTIONS:

#     print("\n" + "=" * 70)
#     print(f"Processing Collection : {collection_name}")
#     print("=" * 70)

#     collection = db[collection_name]

#     articles = collection.find(
#         {
#             "status.content_extracted": {
#                 "$ne": True
#             }
#         }
#     ).limit(PROCESS_BATCH_SIZE)

#     processed = 0
#     failed = 0

#     # =================================================
#     # Process Each Article
#     # =================================================

#     for doc in articles:

#         try:

#             url = doc.get("link")

#             if not url:
#                 failed += 1
#                 print("✗ Missing URL")
#                 continue

#             print(f"\nExtracting : {url}")

#             result = extract_article(url)

#             # -----------------------------------------
#             # Extraction Failed
#             # -----------------------------------------

#             if not result:

#                 current_time = datetime.now(UTC)

#                 collection.update_one(
#                     {
#                         "_id": doc["_id"]
#                     },
#                     {
#                         "$set": {
#                             "status.content_extracted": False,
#                             "status.content_cleaned": False,
#                             "error": "All extraction methods failed",
#                             "updated_at": current_time
#                         }
#                     }
#                 )

#                 failed += 1

#                 print("✗ Extraction Failed")

#                 continue

#             # -----------------------------------------
#             # Clean Content
#             # -----------------------------------------

#             cleaned_content = clean_content(

#                 result["content"],

#                 doc.get("source", "")

#             )

#             current_time = datetime.now(UTC)

#             # -----------------------------------------
#             # Update MongoDB
#             # -----------------------------------------

#             collection.update_one(

#                 {

#                     "_id": doc["_id"]

#                 },

#                 {

#                     "$set": {

#                                 "title": result["title"] or doc.get("title", ""),

#                                 "authors": result["authors"] or doc.get("authors", []),

#                                 "content": result["content"],

#                                 "clean_content": cleaned_content,

#                                  "status.content_extracted": True,

#                                 "status.content_cleaned": True,

#                                 "error": None,

#                                 "fetched_at": doc.get("fetched_at", current_time),

#                                 "updated_at": current_time,

#                                 "extraction_method": result["method"]

#                                 }

#                 }

#             )

#             processed += 1

#             print(

#                 f"✓ [{result['method']}] "

#                 f"{(result['title'] or 'No Title')[:70]}"

#             )

#         # except Exception as e:

#         #     failed += 1

#         #     print(f"✗ Error : {e}")
        
#         except Exception as e:

#             failed += 1

#             collection.update_one(
#                 {
#                     "_id": doc["_id"]
#                 },
#                 {
#                     "$set": {
#                         "error": str(e),
#                         "updated_at": datetime.now(UTC)
#                     }
#                 }
#             )

#             print(f"✗ Error : {e}")
                

#     # =================================================

#     print("\n" + "-" * 70)

#     print(f"Processed : {processed}")

#     print(f"Failed    : {failed}")

#     print("-" * 70)

# print("\nHistorical Content Extraction Finished.")






"""
historical_content_extractor.py

Version 5.1 (Testing Version)

Features:
- Process pending articles
- Test one newspaper at a time
- Easy switching between newspapers
"""

from datetime import datetime, UTC
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
# TEST MODE
# =====================================================
# Change this value while testing.
#
# Options:
# "Economic Times"
# "Hindustan Times"
# "Indian Express"
# "The Hindu"
#
# After testing all newspapers,
# set TEST_SOURCE = None
# =====================================================

TEST_SOURCE = "Hindustan Times"

# TEST_SOURCE = "Economic Times"
# TEST_SOURCE = "Indian Express"
# TEST_SOURCE = "The Hindu"
# TEST_SOURCE = None


# =====================================================
# Connect MongoDB
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]


# =====================================================
# Main Function
# =====================================================

def main():

    print("=" * 70)
    print("Historical Content Extraction Worker")
    print("=" * 70)

    query = {
        "content_extracted": {"$ne": True}
    }

    if TEST_SOURCE is not None:
        query["source"] = TEST_SOURCE

    print("\nTesting Source :", TEST_SOURCE if TEST_SOURCE else "ALL")
    print("Batch Size     :", BATCH_SIZE)

    pending_articles = collection.find(query).limit(BATCH_SIZE)

    processed = 0
    success = 0
    failed = 0

    for article in pending_articles:

        processed += 1

        article_id = article["_id"]
        url = article.get("link")
        source = article.get("source")

        print("\n" + "=" * 70)
        print(f"[{processed}/{BATCH_SIZE}]")
        print("Source :", source)
        print("URL    :", url)

        try:

            result = extract_article(url)

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

            collection.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "title": result.get("title"),
                        "authors": result.get("authors"),
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

            print("❌ Error:", e)

    print("\n" + "=" * 70)
    print("Extraction Summary")
    print("=" * 70)

    print("Testing Source :", TEST_SOURCE if TEST_SOURCE else "ALL")
    print(f"Processed      : {processed}")
    print(f"Successful     : {success}")
    print(f"Failed         : {failed}")


# =====================================================
# Program Entry
# =====================================================

if __name__ == "__main__":
    main()