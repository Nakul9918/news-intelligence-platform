"""
Summary Generator Service

MongoDB
    ↓
Find NER Processed Articles
    ↓
Validate Content
    ↓
Split Long Article
    ↓
Generate Summary
    ↓
Store Summary
    ↓
Update MongoDB
"""

import logging
from datetime import datetime, UTC

from pymongo import (
    MongoClient,
    ReturnDocument
)

from transformers import pipeline

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger("Summary_Generator")

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

# Main Worker Index

collection.create_index(

    [

        ("status.ner_done", 1),

        ("status.summary_done", 1),

        ("status.summary_failed", 1),

        ("status.summary_processing", 1)

    ]

)

# Processing Metrics

collection.create_index(

    "processing.summary_time"

)

# Search Index

collection.create_index(

    "summary.text"

)

# =====================================================
# Configuration
# =====================================================

SUMMARY_VERSION = "1.0.0"

SUMMARY_MODEL = "facebook/bart-large-cnn"

MIN_CONTENT_LENGTH = 100

MAX_INPUT_LENGTH = 900

MIN_SUMMARY_LENGTH = 50

MAX_SUMMARY_LENGTH = 150

MAX_SUMMARY_RETRIES = 3

TOP_SUMMARY_PREVIEW = 200

# =====================================================
# Load Model
# =====================================================

logger.info("=" * 70)

logger.info("Loading Summary Model")

logger.info(f"Model            : {SUMMARY_MODEL}")

try:

    summarizer = pipeline(

        task="summarization",

        model=SUMMARY_MODEL,

        tokenizer=SUMMARY_MODEL

    )

    logger.info("Summary Model Loaded Successfully")

except Exception:

    logger.exception(

        "Failed To Load Summary Model"

    )

    raise

logger.info("=" * 70)
# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one_and_update(

        filter={

            "status.ner_done": True,

            "status.summary_done": False,

            "status.summary_failed": False,

            "status.summary_processing": False,

            "status.summary_retry_count": {

                "$lt": MAX_SUMMARY_RETRIES

            }

        },

        update={

            "$set": {

                "status.summary_processing": True,

                "status.summary_started_at": datetime.now(UTC)

            }

        },

        projection={

            "_id": 1,

            "title": 1,

            "link": 1,

            "clean_content": 1,

            "processing": 1,

            "status": 1,

            "fetched_at": 1

        },

        sort=[

            ("fetched_at", 1)

        ],

        return_document=ReturnDocument.AFTER

    )


# =====================================================
# Validate Content
# =====================================================

def validate_content(text):

    if not text:

        return False

    text = text.strip()

    return len(text) >= MIN_CONTENT_LENGTH


# =====================================================
# Split Text into Chunks
# =====================================================

def split_text(text):

    chunks = []

    paragraphs = [

        paragraph.strip()

        for paragraph in text.split("\n")

        if paragraph.strip()

    ]

    current_chunk = ""

    for paragraph in paragraphs:

        # ----------------------------------------
        # Small Paragraph
        # ----------------------------------------

        if len(paragraph) <= MAX_INPUT_LENGTH:

            if (

                len(current_chunk)

                + len(paragraph)

                <= MAX_INPUT_LENGTH

            ):

                if current_chunk:

                    current_chunk += "\n"

                current_chunk += paragraph

            else:

                if current_chunk:

                    chunks.append(

                        current_chunk.strip()

                    )

                current_chunk = paragraph

            continue

        # ----------------------------------------
        # Large Paragraph
        # ----------------------------------------

        words = paragraph.split()

        for word in words:

            if (

                len(current_chunk)

                + len(word)

                + 1

                <= MAX_INPUT_LENGTH

            ):

                if current_chunk:

                    current_chunk += " "

                current_chunk += word

            else:

                chunks.append(

                    current_chunk.strip()

                )

                current_chunk = word

    if current_chunk:

        chunks.append(

            current_chunk.strip()

        )

    return chunks


# =====================================================
# Validate Chunks
# =====================================================

def validate_chunks(chunks):

    if not chunks:

        return False

    for chunk in chunks:

        if not chunk.strip():

            return False

    return True
# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one_and_update(

        filter={

            "status.ner_done": True,

            "status.summary_done": False,

            "status.summary_failed": False,

            "status.summary_processing": False,

            "status.summary_retry_count": {

                "$lt": MAX_SUMMARY_RETRIES

            }

        },

        update={

            "$set": {

                "status.summary_processing": True,

                "status.summary_started_at": datetime.now(UTC)

            }

        },

        projection={

            "_id": 1,

            "title": 1,

            "link": 1,

            "clean_content": 1,

            "processing": 1,

            "status": 1,

            "fetched_at": 1

        },

        sort=[

            ("fetched_at", 1)

        ],

        return_document=ReturnDocument.AFTER

    )


# =====================================================
# Validate Content
# =====================================================

def validate_content(text):

    if not text:

        return False

    text = text.strip()

    return len(text) >= MIN_CONTENT_LENGTH


# =====================================================
# Split Text into Chunks
# =====================================================

def split_text(text):

    chunks = []

    paragraphs = [

        paragraph.strip()

        for paragraph in text.split("\n")

        if paragraph.strip()

    ]

    current_chunk = ""

    for paragraph in paragraphs:

        # ----------------------------------------
        # Small Paragraph
        # ----------------------------------------

        if len(paragraph) <= MAX_INPUT_LENGTH:

            if (

                len(current_chunk)

                + len(paragraph)

                <= MAX_INPUT_LENGTH

            ):

                if current_chunk:

                    current_chunk += "\n"

                current_chunk += paragraph

            else:

                if current_chunk:

                    chunks.append(

                        current_chunk.strip()

                    )

                current_chunk = paragraph

            continue

        # ----------------------------------------
        # Large Paragraph
        # ----------------------------------------

        words = paragraph.split()

        for word in words:

            if (

                len(current_chunk)

                + len(word)

                + 1

                <= MAX_INPUT_LENGTH

            ):

                if current_chunk:

                    current_chunk += " "

                current_chunk += word

            else:

                chunks.append(

                    current_chunk.strip()

                )

                current_chunk = word

    if current_chunk:

        chunks.append(

            current_chunk.strip()

        )

    return chunks


# =====================================================
# Validate Chunks
# =====================================================

def validate_chunks(chunks):

    if not chunks:

        return False

    for chunk in chunks:

        if not chunk.strip():

            return False

    return True

# =====================================================
# Main
# =====================================================

def main():

    processed = 0

    failed = 0

    total_chunks = 0

    total_processing_time = 0.0

    while True:

        started = datetime.now(UTC)

        article = get_pending_article()

        # ----------------------------------------
        # No Pending Articles
        # ----------------------------------------

        if article is None:

            average_time = (

                total_processing_time / processed

                if processed

                else 0

            )

            logger.info("=" * 70)

            logger.info("Summary Worker Summary")

            logger.info("=" * 70)

            logger.info(

                f"Processed             : {processed}"

            )

            logger.info(

                f"Failed                : {failed}"

            )

            logger.info(

                f"Total Chunks          : {total_chunks}"

            )

            logger.info(

                f"Average Process Time  : {average_time:.2f} sec"

            )

            logger.info("=" * 70)

            break

        # ----------------------------------------
        # Worker Started
        # ----------------------------------------

        logger.info("=" * 70)

        logger.info("Summary Generation Started")

        logger.info("=" * 70)

        logger.info(

            f"Title : {article.get('title', '')}"

        )

        logger.info(

            f"URL   : {article.get('link', '')}"

        )

        logger.info("=" * 70)

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

                logger.warning(

                    "Invalid Clean Content"

                )

                mark_summary_failed(

                    article["_id"],

                    "Invalid clean content"

                )

                continue

            # ----------------------------------------
            # Generate Summary
            # ----------------------------------------

            summary, chunk_count = generate_summary(

                text

            )

            if not summary.strip():

                failed += 1

                logger.warning(

                    "Generated Summary Is Empty"

                )

                mark_summary_failed(

                    article["_id"],

                    "Empty summary generated"

                )

                continue

            # ----------------------------------------
            # Processing Time
            # ----------------------------------------

            duration = (

                datetime.now(UTC)

                - started

            ).total_seconds()

            # ----------------------------------------
            # Update MongoDB
            # ----------------------------------------

            update_article(

                article,

                summary,

                chunk_count,

                duration

            )

            processed += 1

            total_chunks += chunk_count

            total_processing_time += duration

            # ----------------------------------------
            # Summary
            # ----------------------------------------

            logger.info("")

            logger.info("=" * 70)

            logger.info("Summary Generation Completed")

            logger.info("=" * 70)

            logger.info(

                f"Chunks Processed      : {chunk_count}"

            )

            logger.info(

                f"Summary Length        : {len(summary)}"

            )

            logger.info(

                f"Summary Words         : {len(summary.split())}"

            )

            logger.info(

                f"Processing Time       : {duration:.2f} sec"

            )

            logger.info("=" * 70)

        except Exception as e:

            failed += 1

            logger.exception(

                "Summary Generation Failed"

            )

            mark_summary_failed(

                article["_id"],

                str(e)

            )

            continue

    logger.info("Summary Worker Stopped")


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    main()
    