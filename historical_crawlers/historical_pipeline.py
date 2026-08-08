"""
=========================================================
Historical NLP Pipeline

Runs the Realtime NLP Pipeline
for all extracted historical articles.

Version : 4.0
=========================================================
"""

from pymongo import MongoClient

from realtime_pipeline.realtime_nlp_pipeline import process_article

# =====================================================
# MongoDB
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "news_db"

COLLECTIONS = [

    "historical_urls_et",

    "historical_urls_thehindu",

    "historical_urls_indianexpress",

    "historical_urls_hindustantimes"

]

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
    print(f"Processing Collection : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(
    {
        "processing.status": {
            "$ne": "COMPLETED"
        }
    }
)

    processed = 0

    failed = 0

    for article in articles:

        try:

            success = process_article(

                str(article["_id"]),

                collection

            )

            if success:

                processed += 1

            else:

                failed += 1

        except Exception as e:

            failed += 1

            print(e)

    print()

    print(f"Processed : {processed}")

    print(f"Failed    : {failed}")

client.close()

print("\nHistorical Pipeline Completed.")