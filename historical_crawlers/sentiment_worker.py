"""
=====================================================
Historical Sentiment Worker
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

from nlp.sentiment import analyze_sentiment

# =====================================================
# MongoDB
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

# =====================================================
# Process Collections
# =====================================================

for collection_name in COLLECTIONS:

    print("\n" + "=" * 70)
    print(f"Sentiment Analysis : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(

        {
            "status.keywords_extracted": True,
            "status.sentiment_done": {
                "$ne": True
            }
        }

    ).limit(PROCESS_BATCH_SIZE)

    processed = 0

    failed = 0

    for article in articles:

        try:

            print(f"Analyzing : {article['title']}")

            result = analyze_sentiment(

                article["clean_content"]

            )

            collection.update_one(

                {
                    "_id": article["_id"]
                },

                {
                    "$set": {

                        "sentiment": result["label"],

                        "sentiment_score": result["score"],

                        "status.sentiment_done": True,

                        "updated_at": datetime.now(UTC)

                    }

                }

            )

            processed += 1

            print("✓ Sentiment Completed")

        except Exception as e:

            failed += 1

            print("✗ Failed")

            print(e)

    print("\nProcessed :", processed)

    print("Failed    :", failed)

print("\nSentiment Worker Finished.")