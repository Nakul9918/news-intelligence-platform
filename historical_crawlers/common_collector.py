import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

# =====================================================
# Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_db"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 60
MAX_RETRIES = 3
BATCH_SIZE = 500

# =====================================================
# MongoDB Connection
# =====================================================

def get_collection(collection_name):

    client = MongoClient(MONGO_URI)

    db = client[DATABASE_NAME]

    return db[collection_name]


# =====================================================
# Download XML
# =====================================================

def download_xml(url):

    for attempt in range(MAX_RETRIES):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT
            )

            response.raise_for_status()

            return BeautifulSoup(
                response.text,
                "xml"
            )

        except Exception:

            if attempt == MAX_RETRIES - 1:
                raise

            print(f"Retry {attempt + 1}/{MAX_RETRIES}")
            time.sleep(2)


# =====================================================
# Store URLs
# =====================================================

def store_urls(
    urls,
    collection,
    source_name
):

    operations = []

    processed = 0
    failed = 0

    for item in urls:

        try:

            article_url = item.loc.text

            published = (
                item.lastmod.text
                if item.lastmod
                else None
            )

            operations.append(

                UpdateOne(

                    {
                        "link": article_url
                    },

                    {
                        "$set": {

                            "source": source_name,
                            "link": article_url,
                            "published": published

                        }

                    },

                    upsert=True

                )

            )

            processed += 1

            if len(operations) >= BATCH_SIZE:

                collection.bulk_write(
                    operations,
                    ordered=False
                )

                print(f"Processed : {processed}")

                operations.clear()

        except Exception:

            failed += 1

    if operations:

        try:

            collection.bulk_write(
                operations,
                ordered=False
            )

        except BulkWriteError:
            pass

    return processed, failed


# =====================================================
# Summary
# =====================================================

def print_summary(

    source_name,
    processed,
    failed

):

    print("\n" + "=" * 70)
    print(f"{source_name} Collection Completed")
    print("=" * 70)
    print(f"Processed URLs : {processed}")
    print(f"Failed         : {failed}")