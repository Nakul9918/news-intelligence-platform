"""
Named Entity Recognition (NER) Service

MongoDB
    ↓
Find Category Processed Articles
    ↓
Validate Content
    ↓
Extract Named Entities
    ↓
Normalize Entities
    ↓
Update MongoDB
"""

import logging
from datetime import datetime, UTC

import spacy

from pymongo import (
    MongoClient,
    ReturnDocument
)

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

logger = logging.getLogger("NER_Service")

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

        ("status.category_done", 1),

        ("status.ner_done", 1),

        ("status.ner_failed", 1),

        ("status.ner_processing", 1)

    ]

)

# Processing Metrics
collection.create_index(

    "processing.ner_time"

)

# Entity Search
collection.create_index(

    "entities.text"

)

collection.create_index(

    "entities.normalized"

)

collection.create_index(

    "entities.label"

)

# =====================================================
# Configuration
# =====================================================

NER_VERSION = "1.0.0"

NER_MODEL = "en_core_web_sm"

SPACY_VERSION = spacy.__version__

MIN_CONTENT_LENGTH = 100

MAX_ENTITIES = 100

TOP_ENTITIES_TO_PRINT = 10

MAX_NER_RETRIES = 3

# =====================================================
# Allowed Entity Labels
# =====================================================

ENTITY_LABELS = {

    "PERSON",

    "ORG",

    "GPE",

    "LOC",

    "FAC",

    "NORP",

    "PRODUCT",

    "EVENT",

    "WORK_OF_ART",

    "LAW",

    "LANGUAGE",

    "DATE",

    "TIME",

    "MONEY",

    "PERCENT",

    "QUANTITY",

    "ORDINAL",

    "CARDINAL"

}

# =====================================================
# Load spaCy Model
# =====================================================

logger.info("=" * 70)

logger.info("Loading spaCy NER Model")

logger.info(f"Model          : {NER_MODEL}")

logger.info(f"spaCy Version  : {SPACY_VERSION}")

try:

    nlp = spacy.load(

        NER_MODEL,

        disable=[

            "parser",

            "textcat",

            "lemmatizer"

        ]

    )

    logger.info("spaCy Model Loaded Successfully")

except Exception:

    logger.exception("Failed To Load spaCy Model")

    raise

logger.info("=" * 70)
# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one_and_update(

        filter={

            "status.category_done": True,

            "status.ner_done": False,

            "status.ner_failed": False,

            "status.ner_processing": False,

            "status.ner_retry_count": {

                "$lt": MAX_NER_RETRIES

            }

        },

        update={

            "$set": {

                "status.ner_processing": True,

                "status.ner_started_at": datetime.now(UTC)

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
# Normalize Entity
# =====================================================

def normalize_entity(text):

    if not text:

        return ""

    text = " ".join(

        text.strip().split()

    )

    text = text.replace(

        "\u200b",

        ""

    )

    text = text.replace(

        "\xa0",

        " "

    )

    return text


# =====================================================
# Extract Entities
# =====================================================

def extract_entities(text):

    doc = nlp(text)

    entities = []

    seen = set()

    label_statistics = {}

    for entity in doc.ents:

        # ----------------------------------------
        # Allowed Labels
        # ----------------------------------------

        if entity.label_ not in ENTITY_LABELS:

            continue

        # ----------------------------------------
        # Normalize Entity
        # ----------------------------------------

        entity_text = normalize_entity(

            entity.text

        )

        # ----------------------------------------
        # Ignore Empty / Non-Text Entities
        # ----------------------------------------

        if not entity_text:

            continue

        if not any(

            character.isalpha()

            for character in entity_text

        ):

            continue

        # ----------------------------------------
        # Minimum Length
        # ----------------------------------------

        if len(entity_text) < 2:

            continue

        # ----------------------------------------
        # Remove Duplicate
        # ----------------------------------------

        key = (

            entity.label_,

            entity_text.lower()

        )

        if key in seen:

            continue

        seen.add(key)

        # ----------------------------------------
        # Label Statistics
        # ----------------------------------------

        label_statistics[entity.label_] = (

            label_statistics.get(

                entity.label_,

                0

            )

            + 1

        )

        # ----------------------------------------
        # Store Entity
        # ----------------------------------------

        entities.append(

            {

                "text": entity_text,

                "normalized": entity_text.lower(),

                "label": entity.label_,

                "length": len(entity_text),

                "start": entity.start_char,

                "end": entity.end_char,

                "occurrences": 1

            }

        )

        # ----------------------------------------
        # Maximum Entity Limit
        # ----------------------------------------

        if len(entities) >= MAX_ENTITIES:

            break

    # ----------------------------------------
    # Sort Entities
    # ----------------------------------------

    entities.sort(

        key=lambda entity: (

            entity["label"],

            entity["normalized"]

        )

    )

    return (

        entities,

        label_statistics

    )


# =====================================================
# Mark NER Failed
# =====================================================

def mark_ner_failed(
    article_id,
    error_message
):

    collection.update_one(

        {

            "_id": article_id

        },

        {

            "$set": {

                # ------------------------------------
                # Status
                # ------------------------------------

                "status.ner_done": False,

                "status.ner_failed": True,

                "status.ner_processing": False,

                # ------------------------------------
                # NER Metadata
                # ------------------------------------

                "ner": {

                    "version": NER_VERSION,

                    "model": NER_MODEL,

                    "spacy_version": SPACY_VERSION,

                    "status": "failed",

                    "entity_count": 0,

                    "entity_labels": 0,

                    "entity_types": [],

                    "processing_time": 0,

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Metadata
                # ------------------------------------

                "updated_at": datetime.now(UTC),

                "error": error_message

            },

            "$inc": {

                "status.ner_retry_count": 1

            }

        }

    )

    logger.error("=" * 70)
    logger.error("NER Failed")
    logger.error(error_message)
    logger.error("=" * 70)


# =====================================================
# Update MongoDB
# =====================================================

def update_article(
    article,
    entities,
    entity_statistics,
    processing_time
):

    # ----------------------------------------
    # Pipeline Processing Time
    # ----------------------------------------

    total_time = (

        article.get(

            "processing",

            {}

        ).get(

            "total_time",

            0

        )

        + processing_time

    )

    entity_count = len(entities)

    unique_labels = len(entity_statistics)

    result = collection.update_one(

        {

            "_id": article["_id"]

        },

        {

            "$set": {

                # ------------------------------------
                # Entity Data
                # ------------------------------------

                "entities": entities,

                "entity_count": entity_count,

                "entity_statistics": entity_statistics,

                # ------------------------------------
                # NER Metadata
                # ------------------------------------

                "ner": {

                    "version": NER_VERSION,

                    "model": NER_MODEL,

                    "spacy_version": SPACY_VERSION,

                    "status": "success",

                    "entity_count": entity_count,

                    "entity_labels": unique_labels,

                    "entity_types": sorted(

                        entity_statistics.keys()

                    ),

                    "processing_time": round(

                        processing_time,

                        3

                    ),

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Status
                # ------------------------------------

                "status.ner_done": True,

                "status.ner_failed": False,

                "status.ner_processing": False,

                # ------------------------------------
                # Processing
                # ------------------------------------

                "processing.ner_time": round(

                    processing_time,

                    3

                ),

                "processing.total_time": round(

                    total_time,

                    3

                ),

                # ------------------------------------
                # Metadata
                # ------------------------------------

                "updated_at": datetime.now(UTC),

                "error": None

            }

        }

    )

    # ----------------------------------------
    # Logging
    # ----------------------------------------

    logger.info("=" * 70)

    logger.info("MongoDB Updated")

    logger.info("=" * 70)

    logger.info(

        f"Matched               : {result.matched_count}"

    )

    logger.info(

        f"Modified              : {result.modified_count}"

    )

    logger.info("")

    logger.info(

        f"Total Entities        : {entity_count}"

    )

    logger.info(

        f"Unique Labels         : {unique_labels}"

    )

    logger.info("")

    logger.info("Entity Statistics")

    logger.info("-" * 70)

    for label, count in sorted(

        entity_statistics.items()

    ):

        logger.info(

            f"{label:<20}: {count}"

        )

    logger.info("")

    logger.info("Top Entities")

    logger.info("-" * 70)

    for entity in entities[:TOP_ENTITIES_TO_PRINT]:

        logger.info(

            f"{entity['text']:<35}"

            f"{entity['label']}"

        )

    if entity_count > TOP_ENTITIES_TO_PRINT:

        logger.info("...")

    logger.info("-" * 70)

    logger.info(

        f"NER Time              : {processing_time:.2f} sec"

    )

    logger.info(

        f"Pipeline Time         : {total_time:.2f} sec"

    )

    logger.info("=" * 70)


# =====================================================
# Main
# =====================================================

def main():

    processed = 0

    failed = 0

    total_entities = 0

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
            logger.info("NER Worker Summary")
            logger.info("=" * 70)

            logger.info(

                f"Processed            : {processed}"

            )

            logger.info(

                f"Failed               : {failed}"

            )

            logger.info(

                f"Total Entities       : {total_entities}"

            )

            logger.info(

                f"Average Process Time : {average_time:.2f} sec"

            )

            logger.info("=" * 70)

            break

        # ----------------------------------------
        # Worker Started
        # ----------------------------------------

        logger.info("=" * 70)

        logger.info("Named Entity Recognition")

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

                mark_ner_failed(

                    article["_id"],

                    "Invalid clean content"

                )

                continue

            # ----------------------------------------
            # Extract Entities
            # ----------------------------------------

            entities, entity_statistics = extract_entities(

                text

            )

            if not entities:

                failed += 1

                logger.warning(

                    "No Named Entities Found"

                )

                mark_ner_failed(

                    article["_id"],

                    "No entities extracted"

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

                entities,

                entity_statistics,

                duration

            )

            processed += 1

            total_entities += len(entities)

            total_processing_time += duration

            # ----------------------------------------
            # Worker Summary
            # ----------------------------------------

            logger.info("")

            logger.info("=" * 70)

            logger.info("NER Summary")

            logger.info("=" * 70)

            logger.info(

                f"Entities Found     : {len(entities)}"

            )

            logger.info(

                f"Entity Labels      : {len(entity_statistics)}"

            )

            logger.info(

                f"Processing Time    : {duration:.2f} sec"

            )

            logger.info("=" * 70)

        except Exception as e:

            failed += 1

            logger.exception(

                "NER Processing Failed"

            )

            mark_ner_failed(

                article["_id"],

                str(e)

            )

            continue

    logger.info("NER Worker Stopped")


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    main()
