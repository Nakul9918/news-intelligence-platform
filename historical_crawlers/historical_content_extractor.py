"""
=====================================================
Historical Content Extractor
Version : 2.0
=====================================================
"""

import requests
import trafilatura

from bs4 import BeautifulSoup
from newspaper import Article
from pymongo import MongoClient

from nlp.content_cleaner import clean_content

from config import (
    MONGO_URI,
    DATABASE_NAME,
    PROCESS_BATCH_SIZE,
    COLLECTIONS
)

# =====================================================
# Extract Article
# =====================================================

def extract_article(url):

    # -------------------------------------------------
    # Method 1 : newspaper3k
    # -------------------------------------------------

    try:

        article = Article(url)

        article.download()

        article.parse()

        if article.text.strip():

            return {

                "title": article.title,

                "content": article.text,

                "method": "newspaper3k"

            }

    except Exception:

        pass

    # -------------------------------------------------
    # Method 2 : Trafilatura
    # -------------------------------------------------

    try:

        downloaded = trafilatura.fetch_url(url)

        if downloaded:

            text = trafilatura.extract(downloaded)

            if text:

                return {

                    "title": "",

                    "content": text,

                    "method": "trafilatura"

                }

    except Exception:

        pass

    # -------------------------------------------------
    # Method 3 : BeautifulSoup
    # -------------------------------------------------

    try:

        headers = {

            "User-Agent": (

                "Mozilla/5.0 "

                "AppleWebKit/537.36 "

                "Chrome/137.0 Safari/537.36"

            )

        }

        response = requests.get(

            url,

            headers=headers,

            timeout=30

        )

        response.raise_for_status()

        soup = BeautifulSoup(

            response.text,

            "html.parser"

        )

        paragraphs = soup.find_all("p")

        text = "\n".join(

            p.get_text(strip=True)

            for p in paragraphs

        )

        title = ""

        if soup.title:

            title = soup.title.get_text(strip=True)

        if text:

            return {

                "title": title,

                "content": text,

                "method": "beautifulsoup"

            }

    except Exception:

        pass

    # -------------------------------------------------

    return None


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

    print(f"Processing Collection : {collection_name}")

    print("=" * 70)

    collection = db[collection_name]

    articles = collection.find(

        {

            "status.content_extracted": {

                "$ne": True

            }

        }

    ).limit(PROCESS_BATCH_SIZE)

    processed = 0

    failed = 0

    # =================================================

    for doc in articles:

        try:

            url = doc.get("link")

            if not url:

                continue

            print(f"\nExtracting : {url}")

            # -----------------------------------------

            result = extract_article(url)

            # -----------------------------------------

            if not result:

                collection.update_one(

                    {

                        "_id": doc["_id"]

                    },

                    {

                        "$set": {

                            "status.content_extracted": False,

                            "extraction_error": "All extraction methods failed"

                        }

                    }

                )

                failed += 1

                print("✗ Extraction Failed")

                continue

            # -----------------------------------------

            cleaned_content = clean_content(

                result["content"],

                doc.get("source", "")

            )

            # -----------------------------------------

            collection.update_one(

                {

                    "_id": doc["_id"]

                },

                {

                    "$set": {

                        "title": result["title"],

                        "content": result["content"],

                        "clean_content": cleaned_content,

                        "content_extracted": True,

                        "content_cleaned": True,

                        "processed": False,

                        "status.content_extracted": True,

                        "extraction_method": result["method"]

                    }

                }

            )

            processed += 1

            print(

                f"✓ "

                f"{result['method']} "

                f"-> "

                f"{result['title'][:70]}"

            )

        except Exception as e:

            failed += 1

            print(f"✗ Error : {e}")

    # =================================================

    print("\n" + "-" * 70)

    print(f"Processed : {processed}")

    print(f"Failed    : {failed}")

    print("-" * 70)

print("\nHistorical Content Extraction Finished.")