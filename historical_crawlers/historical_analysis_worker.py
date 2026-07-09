"""
=====================================================
Historical Analysis Worker
Version : 3.0
=====================================================
"""

from datetime import datetime

from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    COLLECTIONS,
    PROCESS_BATCH_SIZE
)

from nlp.content_cleaner import clean_content
from nlp.keyword_extractor import extract_keywords
from nlp.sentiment import analyze_sentiment

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

# =====================================================
# Process Every Collection
# =====================================================

for collection_name in COLLECTIONS:

    print("\n" + "=" * 70)
    print(f"Processing Collection : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(

        {
            "processed": False,
            "content": {
                "$exists": True
            }
        }

    ).limit(PROCESS_BATCH_SIZE)

    processed_count = 0

    failed_count = 0

    # =================================================
    # Process Articles
    # =================================================

    for article in articles:

        try:

            print(f"\nProcessing : {article['title']}")

            # -----------------------------------------
            # Clean Content
            # -----------------------------------------

            cleaned_content = clean_content(

                article["content"],

                article.get("source", "")

            )

            # -----------------------------------------
            # Extract Keywords
            # -----------------------------------------

            keywords = extract_keywords(
                cleaned_content
            )

            # -----------------------------------------
            # Sentiment Analysis
            # -----------------------------------------

            sentiment = analyze_sentiment(
                cleaned_content
            )

            # -----------------------------------------
            # Update MongoDB
            # -----------------------------------------

            collection.update_one(

                {
                    "_id": article["_id"]
                },

                {
                    "$set": {

                        "clean_content": cleaned_content,

                        "keywords": keywords,

                        "sentiment": sentiment["label"],

                        "sentiment_score": sentiment["score"],

                        "processed": True,

                        "status": {

                            "content_extracted": True,

                            "content_cleaned": True,

                            "keywords_extracted": True,

                            "sentiment_done": True,

                            "category_done": False

                        },

                        "processing_version": 1,

                        "updated_at": datetime.utcnow()

                    }

                }

            )

            processed_count += 1

            print(f"✓ Completed : {article['title']}")

        except Exception as e:

            failed_count += 1

            print(f"✗ Error : {article['title']}")
            print(e)

    # =================================================
    # Collection Summary
    # =================================================

    print("\n" + "-" * 70)

    print(f"Processed : {processed_count}")

    print(f"Failed    : {failed_count}")

    print("-" * 70)

print("\nHistorical Analysis Completed.")