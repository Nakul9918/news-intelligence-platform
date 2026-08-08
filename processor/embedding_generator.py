# """
# Embedding Generator

# MongoDB
#     ↓
# Find Summarized Articles
#     ↓
# Generate Vector Embeddings
#     ↓
# Store in MongoDB
# """

# from datetime import datetime, UTC

# from sentence_transformers import SentenceTransformer
# from pymongo import MongoClient

# from config import (
#     MONGO_URI,
#     DATABASE_NAME,
#     REALTIME_COLLECTION_NAME,
# )

# # =====================================================
# # Model Configuration
# # =====================================================

# MODEL_NAME = "BAAI/bge-small-en-v1.5"

# MIN_CONTENT_LENGTH = 100

# MAX_EMBEDDING_TEXT = 3000

# # =====================================================
# # MongoDB
# # =====================================================

# client = MongoClient(

#     MONGO_URI,

#     maxPoolSize=20,

#     serverSelectionTimeoutMS=5000

# )

# db = client[DATABASE_NAME]

# collection = db[REALTIME_COLLECTION_NAME]

# # =====================================================
# # Load Embedding Model
# # =====================================================

# print("=" * 70)
# print("Loading Embedding Model...")
# print("=" * 70)

# embedding_model = SentenceTransformer(

#     MODEL_NAME

# )

# print("Embedding Model Loaded Successfully")

# # =====================================================
# # Get Pending Article
# # =====================================================

# def get_pending_article():

#     return collection.find_one(

#         {

#             "status.summary_done": True,

#             "status.embedding_done": False

#         }

#     )

# # =====================================================
# # Validate Content
# # =====================================================

# def validate_content(text):

#     if not text:

#         return False

#     if len(text.strip()) < MIN_CONTENT_LENGTH:

#         return False

#     return True

# # =====================================================
# # Prepare Text for Embedding
# # =====================================================

# def prepare_embedding_text(article):

#     parts = []

#     # ----------------------------------------
#     # Title
#     # ----------------------------------------

#     title = article.get(

#         "title",

#         ""

#     ).strip()

#     if title:

#         parts.append(title)

#     # ----------------------------------------
#     # Summary
#     # ----------------------------------------

#     summary = article.get(

#         "summary",

#         ""

#     ).strip()

#     if summary:

#         parts.append(summary)

#     # ----------------------------------------
#     # Category
#     # ----------------------------------------

#     category = article.get(

#         "category",

#         ""

#     ).strip()

#     if category:

#         parts.append(

#             f"Category: {category}"

#         )

#     # ----------------------------------------
#     # Keywords
#     # ----------------------------------------

#     keywords = article.get(

#         "keywords",

#         []

#     )

#     if keywords:

#         keyword_text = ", ".join(

#             [

#                 item["text"]

#                 if isinstance(item, dict)

#                 else str(item)

#                 for item in keywords

#             ]

#         )

#         parts.append(

#             f"Keywords: {keyword_text}"

#         )

#     # ----------------------------------------
#     # Named Entities
#     # ----------------------------------------

#     entities = article.get(

#         "entities",

#         {}

#     )

#     entity_list = []

#     for values in entities.values():

#         entity_list.extend(values)

#     if entity_list:

#         parts.append(

#             "Entities: "

#             + ", ".join(entity_list)

#         )

#     # ----------------------------------------
#     # Final Text
#     # ----------------------------------------

#     text = "\n".join(parts)

#     return text[:MAX_EMBEDDING_TEXT]


# # =====================================================
# # Generate Embedding
# # =====================================================

# def generate_embedding(article):

#     text = prepare_embedding_text(

#         article

#     )

#     if not validate_content(text):

#         return None

#     embedding = embedding_model.encode(

#         text,

#         normalize_embeddings=True,

#         convert_to_numpy=True

#     )

#     return embedding.tolist()

# # =====================================================
# # Update MongoDB
# # =====================================================

# def update_article(

#     article_id,

#     embedding,

#     processing_time

# ):

#     result = collection.update_one(

#         {

#             "_id": article_id

#         },

#         {

#             "$set": {

#                 "embedding": embedding,

#                 "embedding_dimension": len(embedding),

#                 "embedding_model": MODEL_NAME,

#                 "status.embedding_done": True,

#                 "processing.embedding_time": round(

#                     processing_time,

#                     3

#                 ),

#                 "updated_at": datetime.now(UTC),

#                 "error": None

#             }

#         }

#     )

#     print()

#     print("=" * 70)

#     print("MongoDB Updated")

#     print("=" * 70)

#     print(f"Matched  : {result.matched_count}")

#     print(f"Modified : {result.modified_count}")

#     print(f"Dimension: {len(embedding)}")

#     print("=" * 70)

# # =====================================================
# # Main
# # =====================================================

# def main():

#     started = datetime.now(UTC)

#     article = get_pending_article()

#     if article is None:

#         print("=" * 70)

#         print("No Pending Articles")

#         print("=" * 70)

#         return

#     print("=" * 70)

#     print("Generating Embedding")

#     print(article["link"])

#     print("=" * 70)

#     try:

#         # ----------------------------------------
#         # Prepare Text
#         # ----------------------------------------

#         embedding = generate_embedding(

#             article

#         )

#         if embedding is None:

#             raise ValueError(

#                 "Embedding generation failed."

#             )

#         # ----------------------------------------
#         # Processing Time
#         # ----------------------------------------

#         duration = (

#             datetime.now(UTC) - started

#         ).total_seconds()

#         # ----------------------------------------
#         # Update MongoDB
#         # ----------------------------------------

#         update_article(

#             article["_id"],

#             embedding,

#             duration

#         )

#         # ----------------------------------------
#         # Summary
#         # ----------------------------------------

#         print()

#         print("=" * 70)

#         print("Embedding Generation Completed")

#         print("=" * 70)

#         print(f"Model            : {MODEL_NAME}")

#         print(f"Dimensions       : {len(embedding)}")

#         print(f"Processing Time  : {duration:.2f} sec")

#         print("=" * 70)

#     except Exception as e:

#         print()

#         print("=" * 70)

#         print("Embedding Generation Failed")

#         print("=" * 70)

#         print(f"Article : {article['link']}")

#         print(f"Reason  : {e}")

#         print("=" * 70)

#         collection.update_one(

#             {

#                 "_id": article["_id"]

#             },

#             {

#                 "$set": {

#                     "error": str(e),

#                     "updated_at": datetime.now(UTC)

#                 }

#             }

#         )


# # =====================================================
# # Main
# # =====================================================

# if __name__ == "__main__":

#     main()



"""
Embedding Generator Service

MongoDB
    ↓
Find Summarized Articles
    ↓
Prepare Embedding Text
    ↓
Generate Vector Embedding
    ↓
Store Embedding
    ↓
Update MongoDB
"""

import logging
from datetime import datetime, UTC

from pymongo import (
    MongoClient,
    ReturnDocument
)

from sentence_transformers import SentenceTransformer

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

logger = logging.getLogger("Embedding_Generator")

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

        ("status.summary_done", 1),

        ("status.embedding_done", 1),

        ("status.embedding_failed", 1),

        ("status.embedding_processing", 1)

    ]

)

# Processing Metrics

collection.create_index(

    "processing.embedding_time"

)

# Embedding Metadata

collection.create_index(

    "embedding.model"

)

# =====================================================
# Configuration
# =====================================================

EMBEDDING_VERSION = "1.0.0"

MODEL_NAME = "BAAI/bge-small-en-v1.5"

MIN_CONTENT_LENGTH = 100

MAX_EMBEDDING_TEXT = 3000

MAX_EMBEDDING_RETRIES = 3

EXPECTED_EMBEDDING_DIMENSION = 384

# =====================================================
# Load Embedding Model
# =====================================================

logger.info("=" * 70)

logger.info("Loading Embedding Model")

logger.info(f"Model : {MODEL_NAME}")

try:

    embedding_model = SentenceTransformer(

        MODEL_NAME

    )

    logger.info(

        "Embedding Model Loaded Successfully"

    )

except Exception:

    logger.exception(

        "Failed To Load Embedding Model"

    )

    raise

logger.info("=" * 70)

# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one_and_update(

        filter={

            "status.summary_done": True,

            "status.embedding_done": False,

            "status.embedding_failed": False,

            "status.embedding_processing": False,

            "status.embedding_retry_count": {

                "$lt": MAX_EMBEDDING_RETRIES

            }

        },

        update={

            "$set": {

                "status.embedding_processing": True,

                "status.embedding_started_at": datetime.now(UTC)

            }

        },

        projection={

            "_id": 1,

            "title": 1,

            "summary": 1,

            "category": 1,

            "keywords": 1,

            "entities": 1,

            "processing": 1,

            "status": 1,

            "link": 1,

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
# Prepare Embedding Text
# =====================================================

def prepare_embedding_text(article):

    sections = []

    # ----------------------------------------
    # Title
    # ----------------------------------------

    title = article.get(

        "title",

        ""

    ).strip()

    if title:

        sections.append(

            f"Title: {title}"

        )

    # ----------------------------------------
    # Summary
    # ----------------------------------------

    summary = article.get(

        "summary",

        {}

    )

    if isinstance(summary, dict):

        summary_text = summary.get(

            "text",

            ""

        ).strip()

    else:

        summary_text = str(summary).strip()

    if summary_text:

        sections.append(

            f"Summary: {summary_text}"

        )

    # ----------------------------------------
    # Category
    # ----------------------------------------

    category = article.get(

        "category",

        ""

    )

    if isinstance(category, dict):

        category = category.get(

            "label",

            ""

        )

    category = str(category).strip()

    if category:

        sections.append(

            f"Category: {category}"

        )

    # ----------------------------------------
    # Keywords
    # ----------------------------------------

    keywords = article.get(

        "keywords",

        []

    )

    keyword_list = []

    for keyword in keywords:

        if isinstance(keyword, dict):

            keyword_list.append(

                keyword.get(

                    "text",

                    ""

                )

            )

        else:

            keyword_list.append(

                str(keyword)

            )

    keyword_list = [

        keyword.strip()

        for keyword in keyword_list

        if keyword.strip()

    ]

    if keyword_list:

        sections.append(

            "Keywords: "

            + ", ".join(keyword_list)

        )

    # ----------------------------------------
    # Named Entities
    # ----------------------------------------

    entities = article.get(

        "entities",

        []

    )

    entity_list = []

    for entity in entities:

        if isinstance(entity, dict):

            entity_list.append(

                entity.get(

                    "text",

                    ""

                )

            )

        else:

            entity_list.append(

                str(entity)

            )

    entity_list = [

        entity.strip()

        for entity in entity_list

        if entity.strip()

    ]

    if entity_list:

        sections.append(

            "Entities: "

            + ", ".join(entity_list)

        )

    # ----------------------------------------
    # Final Text
    # ----------------------------------------

    text = "\n".join(

        sections

    )

    return text[:MAX_EMBEDDING_TEXT]


# =====================================================
# Generate Embedding
# =====================================================

def generate_embedding(article):

    text = prepare_embedding_text(

        article

    )

    if not validate_content(text):

        raise ValueError(

            "Invalid embedding text"

        )

    embedding = embedding_model.encode(

        text,

        normalize_embeddings=True,

        convert_to_numpy=True

    )

    embedding = embedding.tolist()

    if len(embedding) != EXPECTED_EMBEDDING_DIMENSION:

        raise ValueError(

            "Unexpected embedding dimension"

        )

    return (

        embedding,

        text

    )
# =====================================================
# Mark Embedding Failed
# =====================================================

def mark_embedding_failed(

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

                "status.embedding_done": False,

                "status.embedding_failed": True,

                "status.embedding_processing": False,

                # ------------------------------------
                # Embedding Metadata
                # ------------------------------------

                "embedding": {

                    "vector": [],

                    "dimension": 0,

                    "model": MODEL_NAME,

                    "version": EMBEDDING_VERSION,

                    "normalized": True,

                    "source": "",

                    "processing_time": 0,

                    "status": "failed",

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Metadata
                # ------------------------------------

                "updated_at": datetime.now(UTC),

                "error": error_message

            },

            "$inc": {

                "status.embedding_retry_count": 1

            }

        }

    )

    logger.error("=" * 70)

    logger.error("Embedding Generation Failed")

    logger.error(error_message)

    logger.error("=" * 70)


# =====================================================
# Update MongoDB
# =====================================================

def update_article(

    article,

    embedding,

    embedding_text,

    processing_time

):

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

    vector_dimension = len(

        embedding

    )

    source_length = len(

        embedding_text

    )

    result = collection.update_one(

        {

            "_id": article["_id"]

        },

        {

            "$set": {

                # ------------------------------------
                # Embedding
                # ------------------------------------

                "embedding": {

                    "vector": embedding,

                    "dimension": vector_dimension,

                    "model": MODEL_NAME,

                    "version": EMBEDDING_VERSION,

                    "normalized": True,

                    "source": "summary",

                    "source_length": source_length,

                    "processing_time": round(

                        processing_time,

                        3

                    ),

                    "status": "success",

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Status
                # ------------------------------------

                "status.embedding_done": True,

                "status.embedding_failed": False,

                "status.embedding_processing": False,

                # ------------------------------------
                # Processing
                # ------------------------------------

                "processing.embedding_time": round(

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

    logger.info("=" * 70)

    logger.info("MongoDB Updated")

    logger.info("=" * 70)

    logger.info(

        f"Matched              : {result.matched_count}"

    )

    logger.info(

        f"Modified             : {result.modified_count}"

    )

    logger.info(

        f"Vector Dimension     : {vector_dimension}"

    )

    logger.info(

        f"Embedding Length     : {source_length}"

    )

    logger.info(

        f"Model                : {MODEL_NAME}"

    )

    logger.info(

        f"Normalized           : True"

    )

    logger.info(

        f"Processing Time      : {processing_time:.2f} sec"

    )

    logger.info("=" * 70)

    logger.info("Embedding Preview")

    logger.info("-" * 70)

    logger.info(

        embedding[:10]

    )

    logger.info("...")

    logger.info("-" * 70)
# =====================================================
# Main
# =====================================================

def main():

    processed = 0

    failed = 0

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

            logger.info("Embedding Worker Summary")

            logger.info("=" * 70)

            logger.info(

                f"Processed              : {processed}"

            )

            logger.info(

                f"Failed                 : {failed}"

            )

            logger.info(

                f"Average Process Time   : {average_time:.2f} sec"

            )

            logger.info("=" * 70)

            break

        # ----------------------------------------
        # Worker Started
        # ----------------------------------------

        logger.info("=" * 70)

        logger.info("Embedding Generation Started")

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
            # Generate Embedding
            # ----------------------------------------

            embedding, embedding_text = generate_embedding(

                article

            )

            if not embedding:

                failed += 1

                logger.warning(

                    "Embedding Generation Failed"

                )

                mark_embedding_failed(

                    article["_id"],

                    "Embedding is empty"

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

                embedding,

                embedding_text,

                duration

            )

            processed += 1

            total_processing_time += duration

            # ----------------------------------------
            # Summary
            # ----------------------------------------

            logger.info("")

            logger.info("=" * 70)

            logger.info("Embedding Generated")

            logger.info("=" * 70)

            logger.info(

                f"Vector Dimension      : {len(embedding)}"

            )

            logger.info(

                f"Source Length         : {len(embedding_text)}"

            )

            logger.info(

                f"Processing Time       : {duration:.2f} sec"

            )

            logger.info("=" * 70)

        except Exception as e:

            failed += 1

            logger.exception(

                "Embedding Generation Failed"

            )

            mark_embedding_failed(

                article["_id"],

                str(e)

            )

            continue

    logger.info("Embedding Worker Stopped")


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    main()

    