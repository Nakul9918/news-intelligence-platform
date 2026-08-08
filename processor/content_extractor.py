"""
Content Extraction Service

MongoDB
    ↓
Find Pending Articles
    ↓
Download HTML
    ↓
Extract Metadata + Content
    ↓
Update MongoDB
"""

from datetime import datetime, UTC
import html

import requests
import trafilatura
import time
# =====================================================
# HTTP Session
# =====================================================

session = requests.Session()

from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
    HEADERS,
    TIMEOUT,
    MAX_RETRIES,
)
# =====================================================
# MongoDB
# =====================================================

client = MongoClient(

    MONGO_URI,

    maxPoolSize=20,

    serverSelectionTimeoutMS=5000

)
db = client[DATABASE_NAME]

collection = db[REALTIME_COLLECTION_NAME]

# =====================================================
# Get One Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one(

        {

            "status.content_extracted": False,

            "status.content_extraction_failed": False

        }

    )

# =====================================================
# Download HTML
# =====================================================

def download_html(url):

    for attempt in range(MAX_RETRIES):

        try:

            response = session.get(

                url,

                headers=HEADERS,

                timeout=TIMEOUT

            )

            response.raise_for_status()
            print(f"Downloaded : {url}")

            return response.text

        except requests.RequestException as e:

            if attempt == MAX_RETRIES - 1:

                raise

            print(

                f"Retry {attempt + 1}/{MAX_RETRIES} : {e}"

            )
            time.sleep(2 ** attempt)
# =====================================================
# Extract Article
# =====================================================

def extract_article(html_text):

    metadata = trafilatura.extract_metadata(html_text)

    content = trafilatura.extract(
        html_text,
        include_comments=False,
        include_tables=False
    )

    # ----------------------------------------
    # Title
    # ----------------------------------------

    title = ""

    if metadata and metadata.title:
        title = metadata.title.strip()

    # ----------------------------------------
    # Description
    # ----------------------------------------

    description = ""

    if metadata and metadata.description:
        description = metadata.description.strip()

    # ----------------------------------------
    # Authors
    # ----------------------------------------

    authors = ["Unknown"]

    if metadata and metadata.author:
        authors = [
            author.strip()
            for author in metadata.author.split(",")
            if author.strip()
        ]

        if len(authors) == 0:
            authors = ["Unknown"]

    # ----------------------------------------
    # Language
    # ----------------------------------------

    language = "en"

    if metadata and metadata.language:
        language = metadata.language

    # ----------------------------------------
    # Final Cleanup
    # ----------------------------------------

    title = html.unescape(title).strip()
    description = html.unescape(description).strip()
    content = (content or "").strip()

    return {
        "title": title,
        "description": description,
        "authors": authors,
        "content": content,
        "language": language
    }

# =====================================================
# Validate Content
# =====================================================
def validate_content(content):

    if content is None:

        return False

    content = content.strip()

    if len(content) < 100:

        return False

    return True
# =====================================================
# Update MongoDB
# =====================================================

def update_article(article_id, article_data):

    # ----------------------------------------
    # Existing Article
    # ----------------------------------------

    existing_article = collection.find_one(

        {
            "_id": article_id
        },

        {
            "title": 1,
            "description": 1
        }

    )

    result = collection.update_one(

        {
            "_id": article_id
        },

        {
            "$set": {

                "title": article_data["title"] or (
    existing_article.get("title", "Untitled Article")
    if existing_article else
    "Untitled Article"
),
                "description": article_data["description"] or (
    existing_article.get("description", "")
    if existing_article else
    ""
),

                "authors": article_data["authors"],

                "content": article_data["content"],

                "language": article_data["language"],

                "status.content_extracted": True,

                "extraction_method": "trafilatura",

                "processing.extraction_time": round(
                    article_data["processing_time"],
                    3
                ),

                "processing.total_time": round(
                    article_data["processing_time"],
                    3
                ),

                "updated_at": datetime.now(UTC),

                "error": None

            }

        }

    )
    # Log result
    print()
    print("=" * 70)
    print("MongoDB Updated")
    print("=" * 70)
    print(f"Matched  : {result.matched_count}")
    print(f"Modified : {result.modified_count}")
    print("=" * 70)
# =====================================================
# Main
# =====================================================

def main():

    while True:

        started = datetime.now(UTC)

        article = get_pending_article()

        if article is None:

            print("=" * 70)
            print("No Pending Articles")
            print("=" * 70)

            break

        print("=" * 70)
        print("URL")
        print(article["link"])
        print("=" * 70)

        try:

            # ----------------------------------------
            # Download HTML
            # ----------------------------------------

            html_content = download_html(

                article["link"]

            )

            # ----------------------------------------
            # Validate HTML
            # ----------------------------------------

            if not html_content:

                raise ValueError(

                    "Downloaded HTML is empty."

                )

            # ----------------------------------------
            # Extract Article
            # ----------------------------------------

            article_data = extract_article(

                html_content

            )

            # ----------------------------------------
            # Validate Extracted Content
            # ----------------------------------------

            if not validate_content(

                article_data["content"]

            ):

                print("Content extraction failed")

                collection.update_one(

                    {

                        "_id": article["_id"]

                    },

                    {

                        "$set": {

    "status.content_extraction_failed": True,

    "error": "Content extraction failed",

    "updated_at": datetime.now(UTC)

}

                    }

                )

                continue

            # ----------------------------------------
            # Processing Time
            # ----------------------------------------

            duration = (

                datetime.now(UTC) - started

            ).total_seconds()

            article_data["processing_time"] = duration

            # ----------------------------------------
            # Update MongoDB
            # ----------------------------------------

            update_article(

                article["_id"],

                article_data

            )

            # ----------------------------------------
            # Summary
            # ----------------------------------------

            print()

            print("=" * 70)
            print("Extraction Summary")
            print("=" * 70)

            print(f"Title            : {article_data['title']}")

            print(f"Author(s)        : {', '.join(article_data['authors'])}")

            print(f"Language         : {article_data['language']}")

            print(f"Characters       : {len(article_data['content'])}")

            print(f"Processing Time  : {duration:.2f} sec")

            print("=" * 70)

        except Exception as e:

            print()

            print("=" * 70)
            print("Extraction Failed")
            print("=" * 70)

            print(e)

            collection.update_one(

                {

                    "_id": article["_id"]

                },

                {

                    "$set": {

    "status.content_extraction_failed": True,

    "error": str(e),

    "updated_at": datetime.now(UTC)

}

                }

            )

            continue


if __name__ == "__main__":

    main()