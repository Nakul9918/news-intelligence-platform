from datetime import datetime, UTC

from pymongo import MongoClient
from newspaper import Article

from nlp.content_cleaner import clean_content
from nlp.summarizer import generate_summary
from nlp.sentiment import analyze_sentiment
from nlp.keyword_extractor import extract_keywords

# =====================================================
# Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_db"

PIPELINE_VERSION = 2


TEST_MODE = True
TEST_LIMIT = 5

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

# =====================================================
# Automatically Discover Historical Collections
# =====================================================

COLLECTIONS = sorted(
    [
        name
        for name in db.list_collection_names()
        if name.startswith("historical_urls_")
    ]
)

print("\nCollections Found:")

for collection in COLLECTIONS:
    print(f"  ✓ {collection}")

# =====================================================
# Process Collection
# =====================================================

def process_collection(collection_name):

    print("\n" + "=" * 70)
    print(f"Processing Collection : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    query = {

        "$or": [

            {

                "processing.pipeline_version": {
                    "$exists": False
                }

            },

            {

                "processing.pipeline_version": {
                    "$lt": PIPELINE_VERSION
                }

            }

        ]

    }

    if TEST_MODE:

        articles = collection.find(query).limit(TEST_LIMIT)

    else:

        articles = collection.find(query)

    processed = 0
    failed = 0

    for article in articles:

        try:

            url = article["link"]

            print("\nDownloading")
            print(url)

            news = Article(url)

            news.download()
            news.parse()

            # =====================================================
            # Clean Content
            # =====================================================

            cleaned_content = clean_content(

                news.text,

                article["source"]

            )

            # =====================================================
            # Generate Summary
            # =====================================================

            summary = generate_summary(

                cleaned_content

            )

            # =====================================================
            # Sentiment
            # =====================================================

            sentiment, sentiment_score = analyze_sentiment(

                cleaned_content

            )

            # =====================================================
            # Keywords
            # =====================================================

            keywords = extract_keywords(

                cleaned_content

            )

            # =====================================================
            # Final Document
            # =====================================================

            article_data = {

                "title": news.title,

                "content": cleaned_content,

                "summary": summary,

                "sentiment": sentiment,

                "sentiment_score": sentiment_score,

                "keywords": keywords,

                "processing": {

                    "completed": True,

                    "pipeline_version": PIPELINE_VERSION,

                    "processed_at": datetime.now(UTC),

                    "modules": {

                        "cleaner": True,

                        "summary": True,

                        "sentiment": True,

                        "keywords": True,

                        "content_hash": False,

                        "duplicate_detection": False,

                        "category": False

                    }

                }

            }

            # =====================================================
            # Update MongoDB
            # =====================================================

            collection.update_one(

                {

                    "_id": article["_id"]

                },

                {

                    "$set": article_data

                }

            )

            processed += 1

            print("Stored :", news.title)

        except Exception as e:

            failed += 1

            print("Error :", e)

    print("\nCompleted :", collection_name)

    print("Processed :", processed)

    print("Failed :", failed)


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    for collection_name in COLLECTIONS:

        process_collection(collection_name)

    print("\n" + "=" * 70)
    print("Historical NLP Pipeline Completed")
    print("=" * 70)