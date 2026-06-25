from pymongo import MongoClient
from newspaper import Article

from nlp.content_cleaner import clean_content
from nlp.summarizer import generate_summary

# =====================================================
# Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_db"

COLLECTIONS = [

    "historical_urls_et",

    "historical_urls_thehindu",

    "historical_urls_indianexpress"

]

TEST_MODE = True
TEST_LIMIT = 5

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

# =====================================================
# Process Collection
# =====================================================

def process_collection(collection_name):

    print("\n" + "=" * 70)
    print(f"Processing Collection : {collection_name}")
    print("=" * 70)

    collection = db[collection_name]

    query = {

        "processed": {
            "$exists": False
        }

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
                news.text
            )

            # =====================================================
            # Generate Summary
            # =====================================================

            summary = generate_summary(
                cleaned_content
            )

            # =====================================================
            # Build Final Document
            # =====================================================

            article_data = {

                "title": news.title,

                "content": cleaned_content,

                "summary": summary,

                "processed": True

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

        process_collection(
            collection_name
        )

    print("\n" + "=" * 70)
    print("Historical NLP Pipeline Completed")
    print("=" * 70)