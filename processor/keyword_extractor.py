

"""
Keyword Extraction Service

MongoDB
    ↓
Find Cleaned Articles
    ↓
Validate Content
    ↓
Extract Keywords
        • spaCy Named Entities
        • KeyBERT Keyphrases
    ↓
Normalize & Merge
    ↓
Update MongoDB
"""

import re
import traceback
from datetime import datetime, UTC

import spacy
from keybert import KeyBERT
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
    "status.keywords_extracted"
)

collection.create_index(
    "status.keyword_extraction_failed"
)

collection.create_index(
    "processing.keyword_time"
)
collection.create_index(
    "keyword_count"
)

collection.create_index(
    "keyword_extraction.status"
)

# =====================================================
# Load NLP Models
# =====================================================

print("=" * 70)
print("Loading NLP Models")
print("=" * 70)

print("Loading spaCy Model...")

nlp = spacy.load(

    "en_core_web_sm"

)

print("spaCy Loaded Successfully")

print()

print("Loading KeyBERT Model...")

kw_model = KeyBERT()

print("KeyBERT Loaded Successfully")

print("=" * 70)

# =====================================================
# Keyword Configuration
# =====================================================

KEYWORD_VERSION = "1.0.0"

KEYWORD_MODEL = "spaCy + KeyBERT"
TOP_KEYWORDS_TO_PRINT = 10
MIN_CONTENT_LENGTH = 100

MIN_KEYWORD_LENGTH = 3

MAX_KEYWORD_WORDS = 2

MIN_KEYBERT_SCORE = 0.40

MAX_KEYWORDS = 20

# =====================================================
# Allowed spaCy Entity Labels
# =====================================================

ENTITY_LABELS = {

    "PERSON",

    "ORG",

    "GPE",

    "LOC",

    "EVENT",

    "PRODUCT",

    "FAC",

    "NORP",

}

# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one(

        {

            "status.content_cleaned": True,

            "status.keywords_extracted": False,

            "status.keyword_extraction_failed": False

        },

        {

            "_id": 1,

            "title": 1,

            "link": 1,

            "clean_content": 1,

            "processing": 1,

            "fetched_at": 1

        },

        sort=[

            ("fetched_at", 1)

        ]

    )

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
# Normalize Keyword
# =====================================================

def normalize_keyword(keyword):

    if not keyword:

        return ""

    # ----------------------------------------
    # Remove Possessive
    # ----------------------------------------

    keyword = keyword.replace("'s", "")

    keyword = keyword.replace("’s", "")

    # ----------------------------------------
    # Replace Hyphen
    # ----------------------------------------

    keyword = keyword.replace("-", " ")

    # ----------------------------------------
    # Remove Multiple Spaces
    # ----------------------------------------

    keyword = " ".join(

        keyword.split()

    )

    return keyword.strip()
# =====================================================
# Extract spaCy Keywords
# =====================================================

def extract_spacy_keywords(text):

    keywords = []

    seen = set()

    doc = nlp(text)

    for entity in doc.ents:

        if entity.label_ not in ENTITY_LABELS:

            continue

        keyword = normalize_keyword(

            entity.text

        )

        if len(keyword) < MIN_KEYWORD_LENGTH:

            continue

        key = keyword.lower()

        if key in seen:

            continue

        seen.add(key)

        keywords.append(

            {

                "text": keyword,

                "score": 1.0,

                "source": "spacy",

                "label": entity.label_

            }

        )

    return keywords


# =====================================================
# Extract KeyBERT Keywords
# =====================================================

def extract_keybert_keywords(text):

    keywords = []

    seen = set()

    try:

        results = kw_model.extract_keywords(

            text,

            keyphrase_ngram_range=(1, MAX_KEYWORD_WORDS),

            stop_words="english",

            top_n=MAX_KEYWORDS

        )

        for keyword, score in results:

            keyword = normalize_keyword(

                keyword

            )

            if len(keyword) < MIN_KEYWORD_LENGTH:

                continue

            if score < MIN_KEYBERT_SCORE:

                continue

            if keyword.isdigit():

                continue

            if not any(

                char.isalpha()

                for char in keyword

            ):

                continue

            key = keyword.lower()

            if key in seen:

                continue

            seen.add(key)

            keywords.append(

                {

                    "text": keyword,

                    "score": round(score, 3),

                    "source": "keybert"

                }

            )

    except Exception as e:

        print()

        print("=" * 70)

        print("KeyBERT Extraction Failed")

        print("=" * 70)

        print(e)

    return keywords


# =====================================================
# Merge Keywords
# =====================================================

def merge_keywords(

    spacy_keywords,

    keybert_keywords

):

    merged = {}

    for keyword in spacy_keywords + keybert_keywords:

        key = keyword["text"].lower()

        if key not in merged:

            merged[key] = keyword

            continue

        if keyword["score"] > merged[key]["score"]:

            merged[key] = keyword

    keywords = list(

        merged.values()

    )

    keywords.sort(

        key=lambda x: x["score"],

        reverse=True

    )

    return keywords[:MAX_KEYWORDS]


# =====================================================
# Extract Keywords
# =====================================================

def extract_keywords(text):

    spacy_keywords = extract_spacy_keywords(

        text

    )

    keybert_keywords = extract_keybert_keywords(

        text

    )

    keywords = merge_keywords(

        spacy_keywords,

        keybert_keywords

    )

    return (

        keywords,

        len(spacy_keywords),

        len(keybert_keywords)

    )
# =====================================================
# Update MongoDB
# =====================================================

def update_article(

    article,

    keywords,

    processing_time,

    spacy_count,

    keybert_count

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
    # Keyword Statistics
    # ----------------------------------------

    keyword_count = len(keywords)

    duplicate_keywords_removed = max(

        (spacy_count + keybert_count) - keyword_count,

        0

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

                "keywords": keywords,

                "keyword_count": keyword_count,

                "spacy_keyword_count": spacy_count,

                "keybert_keyword_count": keybert_count,

                "duplicate_keywords_removed": duplicate_keywords_removed,

                "keyword_extraction": {

                    "version": KEYWORD_VERSION,

                    "model": KEYWORD_MODEL,

                    "status": "success",

                    "completed_at": datetime.now(UTC)

                },
                "status.keywords_extracted": True,

                "status.keyword_extraction_failed": False,

                "processing.keyword_time": round(

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

    print(f"Matched               : {result.matched_count}")

    print(f"Modified              : {result.modified_count}")

    print(f"spaCy Keywords        : {spacy_count}")

    print(f"KeyBERT Keywords      : {keybert_count}")

    print(f"Merged Keywords       : {keyword_count}")
    print()


# =====================================================
# Mark Keyword Extraction Failed
# =====================================================

def mark_keyword_failed(
    article_id,
    error_message
):

    collection.update_one(
        {
            "_id": article_id
        },
        {
            "$set": {
                "status.keywords_extracted": False,
                "status.keyword_extraction_failed": True,

                "keyword_extraction": {
                    "version": KEYWORD_VERSION,
                    "model": KEYWORD_MODEL,
                    "status": "failed",
                    "completed_at": datetime.now(UTC)
                },

                "updated_at": datetime.now(UTC),
                "error": error_message
            }
        }
    )


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
            print("Keyword Extraction Summary")
            print("=" * 70)
            print(f"Processed : {processed}")
            print(f"Failed    : {failed}")
            print(f"Success   : {processed}")
            print("=" * 70)

            break

        print("=" * 70)
        print("Keyword Extraction")
        print(f"Title : {article.get('title', '')}")
        print(f"URL   : {article['link']}")
        print("=" * 70)

        try:

            # ----------------------------------------
            # Validate Content
            # ----------------------------------------

            text = article.get(
                "clean_content",
                ""
            )

            if not validate_content(text):

                failed += 1

                print("Invalid Clean Content")

                mark_keyword_failed(
                    article["_id"],
                    "Invalid clean content"
                )

                continue

            # ----------------------------------------
            # Extract Keywords
            # ----------------------------------------

            (
                keywords,
                spacy_count,
                keybert_count
            ) = extract_keywords(text)

            if len(keywords) == 0:

                failed += 1

                print("No Keywords Found")

                mark_keyword_failed(
                    article["_id"],
                    "No keywords extracted"
                )

                continue

            # ----------------------------------------
            # Processing Time
            # ----------------------------------------

            duration = (
                datetime.now(UTC) - started
            ).total_seconds()

            # ----------------------------------------
            # Update MongoDB
            # ----------------------------------------

            update_article(
                article,
                keywords,
                duration,
                spacy_count,
                keybert_count
            )

            processed += 1

            # ----------------------------------------
            # Summary
            # ----------------------------------------

            print()

            print("=" * 70)
            print("Keyword Extraction Summary")
            print("=" * 70)
            print(f"spaCy Keywords        : {spacy_count}")
            print(f"KeyBERT Keywords      : {keybert_count}")
            print(f"Merged Keywords       : {len(keywords)}")
            print()

            print("Top Keywords")
            print("-" * 70)

            for keyword in keywords[:TOP_KEYWORDS_TO_PRINT]:

                print(
                    f"{keyword['text']} ({keyword['source']})"
                )

            print("-" * 70)
            print(f"Processing Time : {duration:.2f} sec")
            print("=" * 70)

        except Exception as e:

            traceback.print_exc()

            failed += 1

            print()
            print("=" * 70)
            print("Keyword Extraction Failed")
            print("=" * 70)
            print(e)

            mark_keyword_failed(
                article["_id"],
                str(e)
            )

            continue


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    main()