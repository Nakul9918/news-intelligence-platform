import time

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from config import (
    MONGO_URI,
    DATABASE_NAME,
    HEADERS,
    TIMEOUT,
    MAX_RETRIES,
    BATCH_SIZE,
    MAX_ARTICLES_PER_MONTH
)

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

        except Exception as e:

            if attempt == MAX_RETRIES - 1:
                raise e

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

    # Respect monthly limit
    urls = urls[:MAX_ARTICLES_PER_MONTH]

    print(
        f"Collecting {len(urls)} articles "
        f"(Limit: {MAX_ARTICLES_PER_MONTH})"
    )

    for item in urls:

        try:

            article_url = item.loc.text.strip()

            published = (
                item.lastmod.text.strip()
                if item.lastmod
                else None
            )

            operations.append(

                UpdateOne(

                    {
                        "link": article_url
                    },

                    {

                        "$setOnInsert": {

                            "source": source_name,

                            "link": article_url,

                            "published_date": published,

                            "title": "",

                            "authors": [],

                            "content": "",

                            "clean_content": "",

                            "keywords": [],

                            "category": "",

                            "sentiment": "",

                            "sentiment_score": 0.0,

                            "language": "en",

                            "processing_version": 1,

                            "status": {

                                "content_extracted": False,

                                "content_cleaned": False,

                                "keywords_extracted": False,

                                "sentiment_done": False,

                                "category_done": False

                            },

                            "extraction_method": "",

                            "fetched_at": None,

                            "updated_at": None,

                            "error": None

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

        except Exception as e:

            failed += 1

            print(f"Error : {e}")

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
# Print Summary
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