"""
Content Cleaner

MongoDB
    ↓
Find Extracted Articles
    ↓
Clean Text
    ↓
Update MongoDB
"""

import re
import traceback
from datetime import datetime, UTC

from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
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
# MongoDB Indexes
# =====================================================

collection.create_index(
    "status.content_cleaned"
)

collection.create_index(
    "status.content_cleaning_failed"
)
collection.create_index(
    "status.content_extracted"
)

# =====================================================
# Cleaner Configuration
# =====================================================

CLEANING_VERSION = "1.0.0"

CLEANING_METHOD = "regex"

MIN_CONTENT_LENGTH = 100

# =====================================================
# Cleaning Patterns
# =====================================================

CLEANING_PATTERNS = [

    r"Advertisement",

    r"Read More",

    r"Subscribe",

    r"Follow Us",

    r"Breaking News",

    r"Updated\s*:",

    r"Published\s*:",

    r"Share this article",

    r"WhatsApp",

    r"Facebook",

    r"Twitter",

    r"Telegram",

    r"Instagram",

    r"LinkedIn",

    r"Related Stories",

    r"Recommended Stories",

    r"Copyright.*",

]

COMPILED_PATTERNS = [

    re.compile(pattern, re.IGNORECASE)

    for pattern in CLEANING_PATTERNS

]

# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one(

    {
        "status.content_extracted": True,
        "status.content_cleaned": False,
        "status.content_cleaning_failed": False
    },

    {
    "_id": 1,
    "title": 1,
    "link": 1,
    "content": 1,
    "processing": 1,
    "fetched_at": 1
},

    sort=[
        ("fetched_at", 1)
    ]

)

# =====================================================
# Clean Text
# =====================================================

def clean_text(text):

    if not text:

        return ""

    # ----------------------------------------
    # Unicode Cleanup
    # ----------------------------------------

    text = text.replace("\xa0", " ")

    text = text.replace("\u200b", "")

    text = text.replace("\r", " ")

    text = text.replace("\t", " ")

    # ----------------------------------------
    # Normalize Quotes
    # ----------------------------------------

    text = text.replace("’", "'")

    text = text.replace("‘", "'")

    text = text.replace("“", '"')

    text = text.replace("”", '"')

    # ----------------------------------------
    # Remove Patterns
    # ----------------------------------------

    for pattern in COMPILED_PATTERNS:

        text = pattern.sub("", text)

    # ----------------------------------------
    # Remove Empty Lines
    # ----------------------------------------

    text = re.sub(

        r"\n\s*\n+",

        "\n",

        text

    )

    # ----------------------------------------
    # Remove Extra Spaces
    # ----------------------------------------

    text = re.sub(

        r"[ ]{2,}",

        " ",

        text

    )

    # ----------------------------------------
    # Remove Multiple Spaces
    # ----------------------------------------

    text = re.sub(

        r"\s+",

        " ",

        text

    )

    return text.strip()
# =====================================================
# Validate Content
# =====================================================

def validate_content(text):

    if not text:

        return False

    if len(text.strip()) < MIN_CONTENT_LENGTH:

        return False

    return True

# =====================================================
# Update MongoDB
# =====================================================

def update_article(
    article,
    clean_content,
    processing_time,
    content_length,
    clean_content_length,
    removed_characters,
    cleaning_ratio
):
    # ----------------------------------------
    # Total Processing Time
    # ----------------------------------------

    total = (
        article.get("processing", {})
        .get("total_time", 0)
        + processing_time
    )


    # ----------------------------------------
    # Update MongoDB
    # ----------------------------------------

    result = collection.update_one(

        {
            "_id": article["_id"]
        },

        {
            "$set": {

                "clean_content": clean_content,

                "content_length": content_length,

                "clean_content_length": clean_content_length,

                "removed_characters": removed_characters,

                "cleaning_ratio": cleaning_ratio,

                "cleaning": {

                    "version": CLEANING_VERSION,

                    "method": CLEANING_METHOD,

                    "status": "success"

                },

                "status.content_cleaned": True,

                "status.content_cleaning_failed": False,

                "processing.cleaning_time": round(
                    processing_time,
                    3
                ),

                "processing.total_time": round(
                    total,
                    3
                ),

                "updated_at": datetime.now(UTC),

                "error": None

            }

        }

    )

    # ----------------------------------------
    # Log Result
    # ----------------------------------------

    print()

    print("=" * 70)
    print("MongoDB Updated")
    print("=" * 70)
    print(f"Matched              : {result.matched_count}")
    print(f"Modified             : {result.modified_count}")
    print(f"Original Characters  : {content_length}")
    print(f"Clean Characters     : {clean_content_length}")
    print(f"Removed Characters   : {removed_characters}")
    print(f"Cleaning Ratio       : {cleaning_ratio:.2%}")
    print("=" * 70)
# =====================================================
# Main
# =====================================================

def main():
    processed = 0
    failed = 0

    while True:
        started = datetime.now(UTC)
        article = get_pending_article()

        if article is None:
            print("=" * 70)
            print("No Pending Articles")
            print("=" * 70)

            print()

            print("=" * 70)
            print("Cleaner Summary")
            print("=" * 70)
            print(f"Processed : {processed}")
            print(f"Failed    : {failed}")
            print("=" * 70)

            break

        print("=" * 70)
        print("Cleaning")
        print(f"Title : {article.get('title', '')}")
        print(f"URL   : {article['link']}")
        print("=" * 70)

        try:
            content = article.get("content", "")
            if not content:
                failed += 1
                mark_cleaning_failed(
                    article["_id"],
                    "Empty content"
                )
                continue

            clean_content = clean_text(content)
            content_length = len(content)
            clean_content_length = len(clean_content)
            removed_characters = max(
                content_length - clean_content_length,
                0
            )
            cleaning_ratio = (
                round(
                    clean_content_length / content_length,
                    3
                )
                if content_length
                else 0.0
            )

            if not validate_content(clean_content):
                print("Content Cleaning Failed")
                failed += 1
                mark_cleaning_failed(article["_id"], "Content cleaning failed")
                continue

            duration = (datetime.now(UTC) - started).total_seconds()
            update_article(
                article,
                clean_content,
                duration,
                content_length,
                clean_content_length,
                removed_characters,
                cleaning_ratio
            )
            processed += 1

            print()
            print("=" * 70)
            print("Cleaning Summary")
            print("=" * 70)
            print(f"Original Characters : {content_length}")
            print(f"Clean Characters    : {clean_content_length}")
            print(f"Removed Characters  : {removed_characters}")
            print(f"Cleaning Ratio      : {cleaning_ratio:.2%}")
            print(f"Processing Time     : {duration:.3f} sec")
            print("=" * 70)
        except Exception as e:
            traceback.print_exc()
            failed += 1

            print()
            print("=" * 70)
            print("Cleaning Failed")
            print("=" * 70)

            print(e)
            mark_cleaning_failed(article["_id"], str(e))
            continue

# =====================================================
# Mark Cleaning Failed
# =====================================================

def mark_cleaning_failed(
    article_id,
    error_message
):

    collection.update_one(

        {
            "_id": article_id
        },

        {
            "$set": {

                "status.content_cleaned": False,

                "status.content_cleaning_failed": True,

                "cleaning": {

                    "version": CLEANING_VERSION,

                    "method": CLEANING_METHOD,

                    "status": "failed"

                },

                "updated_at": datetime.now(UTC),

                "error": error_message

            }

        }

    )
# =====================================================
# Main
# =====================================================

if __name__ == "__main__":
    main()

  