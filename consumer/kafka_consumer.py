


"""
Kafka Consumer

Architecture

Kafka
    ↓
Validate Message
    ↓
Normalize Schema
    ↓
Store MongoDB
    ↓
Content Extractor
"""

import json
import logging
import signal
import sys
import time
from datetime import UTC, datetime

from kafka import KafkaConsumer
from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

from config import (

    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    KAFKA_CONSUMER_GROUP,
    AUTO_OFFSET_RESET,
    ENABLE_AUTO_COMMIT,
    LOG_SEPARATOR,
    SMALL_SEPARATOR,

    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,

    PIPELINE_VERSION,
    SCHEMA_VERSION,
    CONSUMER_VERSION,
    ENVIRONMENT,

)


# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger("Kafka_Consumer")

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

logger.info(LOG_SEPARATOR)

logger.info("Creating MongoDB Indexes")

logger.info(LOG_SEPARATOR)

collection.create_index(

    [("link", ASCENDING)],

    unique=True,

    name="link_unique"

)

collection.create_index(

    [("source.name", ASCENDING)],

    name="source_name"

)

collection.create_index(

    [("published_datetime", ASCENDING)],

    name="published_datetime"

)

collection.create_index(

    [("status.content_extracted", ASCENDING)]

)

collection.create_index(

    [("status.content_cleaned", ASCENDING)]

)

collection.create_index(

    [("status.keywords_done", ASCENDING)]

)

collection.create_index(

    [("status.sentiment_done", ASCENDING)]

)

collection.create_index(

    [("status.category_done", ASCENDING)]

)

collection.create_index(

    [("status.ner_done", ASCENDING)]

)

collection.create_index(

    [("status.summary_done", ASCENDING)]

)

collection.create_index(

    [("status.embedding_done", ASCENDING)]

)

collection.create_index(

    [("status.vector_indexed", ASCENDING)]

)

logger.info("MongoDB Indexes Ready")

# =====================================================
# Kafka Consumer
# =====================================================

consumer = KafkaConsumer(

    KAFKA_TOPIC,

    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

    group_id=KAFKA_CONSUMER_GROUP,

    auto_offset_reset=AUTO_OFFSET_RESET,

    enable_auto_commit=ENABLE_AUTO_COMMIT,

    value_deserializer=lambda value: json.loads(

        value.decode("utf-8")

    ),

    max_poll_records=100,

    consumer_timeout_ms=1000

)

logger.info(LOG_SEPARATOR)

logger.info("Kafka Consumer Started")

logger.info(LOG_SEPARATOR)

# =====================================================
# Runtime Statistics
# =====================================================

inserted = 0

duplicates = 0

updated = 0

failed = 0

running = True

started = datetime.now(UTC)

# =====================================================
# Graceful Shutdown
# =====================================================

def shutdown_handler(signum, frame):

    global running

    logger.info(LOG_SEPARATOR)

    logger.info("Shutdown Signal Received")

    logger.info(LOG_SEPARATOR)

    running = False


signal.signal(signal.SIGINT, shutdown_handler)

signal.signal(signal.SIGTERM, shutdown_handler)

# =====================================================
# Validate Article
# =====================================================

def validate_article(article):

    """
    Validate Kafka message before inserting into MongoDB.
    """

    if not isinstance(article, dict):

        return False, "Invalid document."

    link = str(

        article.get(

            "link",

            ""

        )

    ).strip()

    if not link:

        return False, "Missing article link."

    source = article.get(

        "source"

    )

    # --------------------------------------------
    # Source Validation
    # --------------------------------------------

    if not isinstance(source, dict):

        return False, "Invalid source object."

    if not source.get(

        "name"

    ):

        return False, "Missing source name."

    return True, None


# =====================================================
# Normalize Article
# =====================================================

def normalize_article(article):

    """
    Keep collector schema exactly the same.

    Consumer only fills missing values.
    """

    # --------------------------------------------
    # Basic Information
    # --------------------------------------------

    article.setdefault(

        "title",

        ""

    )

    article.setdefault(

        "description",

        ""

    )

    article.setdefault(

        "authors",

        ["Unknown"]

    )

    article.setdefault(

        "language",

        "en"

    )

    article.setdefault(

        "content",

        ""

    )

    article.setdefault(

        "clean_content",

        ""

    )

    # --------------------------------------------
    # Source Object
    # --------------------------------------------

    source = article.setdefault(

        "source",

        {}

    )

    source.setdefault(

        "name",

        ""

    )

    source.setdefault(

        "country",

        "India"

    )

    source.setdefault(

        "language",

        "en"

    )

    source.setdefault(

        "type",

        "rss"

    )

    # --------------------------------------------
    # NLP
    # --------------------------------------------

    article.setdefault(

        "keywords",

        []

    )

    article.setdefault(

        "entities",

        []

    )

    article.setdefault(

        "summary",
    {
        "text": "",
        "model": ""
    }
)

    article.setdefault(
        "embedding",
    {
        "model": "",
        "vector_id": ""
    }
)

    article.setdefault(

        "sentiment",

        {

            "label": "",

            "score": 0.0

        }

    )

    article.setdefault(

        "category",

        {

            "label": "",

            "score": 0.0

        }

    )

    # --------------------------------------------
    # Processing Object
    # --------------------------------------------

    processing = article.setdefault(

        "processing",

        {}

    )

    processing.setdefault(

        "pipeline_version",

        PIPELINE_VERSION

    )

    processing.setdefault(

        "collector",

        source.get(

            "name",

            ""

        )

    )

    processing.setdefault(

        "ingestion_time",

        0

    )

    processing.setdefault(

        "extract_time",

        0

    )

    processing.setdefault(

        "clean_time",

        0

    )

    processing.setdefault(

        "keyword_time",

        0

    )

    processing.setdefault(

        "sentiment_time",

        0

    )

    processing.setdefault(

        "category_time",

        0

    )

    processing.setdefault(

        "ner_time",

        0

    )

    processing.setdefault(

        "summary_time",

        0

    )

    processing.setdefault(

        "embedding_time",

        0

    )

    processing.setdefault(

        "vector_time",

        0

    )

    processing.setdefault(

        "total_time",

        0

    )

    # --------------------------------------------
    # Status Object
    # --------------------------------------------

    status = article.setdefault(

        "status",

        {}

    )

    status.setdefault(

        "ingested",

        True

    )

    status.setdefault(

        "content_extracted",

        False

    )

    status.setdefault(

        "content_extract_processing",

        False

    )

    status.setdefault(

        "content_extract_failed",

        False

    )

    status.setdefault(

        "content_extract_retry_count",

        0

    )

    status.setdefault(

        "content_cleaned",

        False

    )

    status.setdefault(

        "content_clean_processing",

        False

    )

    status.setdefault(

        "content_clean_failed",

        False

    )

    status.setdefault(

        "content_clean_retry_count",

        0

    )

    status.setdefault(

        "keywords_done",

        False

    )

    status.setdefault(

        "keywords_processing",

        False

    )

    status.setdefault(

        "keywords_failed",

        False

    )

    status.setdefault(

        "keywords_retry_count",

        0

    )

    status.setdefault(

        "sentiment_done",

        False

    )

    status.setdefault(

        "sentiment_processing",

        False

    )

    status.setdefault(

        "sentiment_failed",

        False

    )

    status.setdefault(

        "sentiment_retry_count",

        0

    )

    status.setdefault(

        "category_done",

        False

    )

    status.setdefault(

        "category_processing",

        False

    )

    status.setdefault(

        "category_failed",

        False

    )

    status.setdefault(

        "category_retry_count",

        0

    )

    status.setdefault(

        "ner_done",

        False

    )

    status.setdefault(

        "ner_processing",

        False

    )

    status.setdefault(

        "ner_failed",

        False

    )

    status.setdefault(

        "ner_retry_count",

        0

    )

    status.setdefault(

        "summary_done",

        False

    )

    status.setdefault(

        "summary_processing",

        False

    )

    status.setdefault(

        "summary_failed",

        False

    )

    status.setdefault(

        "summary_retry_count",

        0

    )

    status.setdefault(

        "embedding_done",

        False

    )

    status.setdefault(

        "embedding_processing",

        False

    )

    status.setdefault(

        "embedding_failed",

        False

    )

    status.setdefault(

        "embedding_retry_count",

        0

    )

    status.setdefault(

        "vector_indexed",

        False

    )

    status.setdefault(

        "vector_index_processing",

        False

    )

    status.setdefault(

        "vector_index_failed",

        False

    )

    status.setdefault(

        "vector_index_retry_count",

        0

    )
    # --------------------------------------------
    # Metadata
    # --------------------------------------------

    article.setdefault(
        "schema_version",
        SCHEMA_VERSION
    )

    article.setdefault(
        "pipeline_version",
        PIPELINE_VERSION
    )

    article.setdefault(
        "consumer_version",
        CONSUMER_VERSION
    )

    # --------------------------------------------
    # Audit
    # --------------------------------------------

    audit = article.setdefault(
        "audit",
        {}
    )

    audit.setdefault(
        "created_by",
        "bootstrap"
    )

    audit.setdefault(
        "updated_by",
        "bootstrap"
    )

    audit.setdefault(
        "last_updated_stage",
        "collector"
    )

    # --------------------------------------------
    # Error Information
    # --------------------------------------------

    article.setdefault(
        "error",
        None
    )

    article.setdefault(
        "extraction_method",
        ""
    )

    return article
# =====================================================
# Kafka Consumer Loop
# =====================================================

try:

    while running:

        for message in consumer:

            if not running:
                break

            # -----------------------------------------
            # Read Kafka Message
            # -----------------------------------------

            article = message.value

            # -----------------------------------------
            # Validate
            # -----------------------------------------

            valid, reason = validate_article(article)

            if not valid:

                failed += 1

                logger.warning(
                    f"Skipped : {reason}"
                )

                continue

            # -----------------------------------------
            # Normalize Schema
            # -----------------------------------------

            article = normalize_article(article)
            start_time = time.perf_counter()

            now = datetime.now(UTC)
            article["fetched_at"] = now
            article["updated_at"] = now
            article["last_pipeline_update"] = now
            article["last_pipeline_stage"] = "consumer"
            article["ingestion_type"] = "bootstrap"

            # -----------------------------------------
            # Kafka Metadata
            # -----------------------------------------

            article["kafka"] = {
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "timestamp": message.timestamp,
                "consumer_group": KAFKA_CONSUMER_GROUP
            }

            # -----------------------------------------
            # Consumer Metadata
            # -----------------------------------------

           


            audit = article.setdefault(
                "audit",
                {}
            )

            audit["created_by"] = audit.get(
                "created_by",
                "bootstrap"
            )
            audit["updated_by"] = "consumer"
            audit["last_updated_stage"] = "consumer"

            processing = article.setdefault(
                "processing",
                {}
            )

            processing["ingestion_time"] = round(
                time.perf_counter() - start_time,
                3
            )

            processing.setdefault("extract_time", 0)
            processing.setdefault("clean_time", 0)
            processing.setdefault("keyword_time", 0)
            processing.setdefault("category_time", 0)
            processing.setdefault("sentiment_time", 0)
            processing.setdefault("ner_time", 0)
            processing.setdefault("summary_time", 0)
            processing.setdefault("embedding_time", 0)
            processing.setdefault("vector_time", 0)

            processing["total_time"] = round(
                processing["ingestion_time"]
                + processing["extract_time"]
                + processing["clean_time"]
                + processing["keyword_time"]
                + processing["category_time"]
                + processing["sentiment_time"]
                + processing["ner_time"]
                + processing["summary_time"]
                + processing["embedding_time"]
                + processing["vector_time"],
                3
            )

            # -----------------------------------------
            # MongoDB Upsert
            # -----------------------------------------

            result = collection.update_one(
    {
        "link": article["link"]
    },
    {
        "$set": {
            "updated_at": article["updated_at"],
            "last_pipeline_stage": article["last_pipeline_stage"],
            "last_pipeline_update": article["last_pipeline_update"],
            "audit.updated_by": article["audit"]["updated_by"],
            "audit.last_updated_stage": article["audit"]["last_updated_stage"],
            "processing.ingestion_time": article["processing"]["ingestion_time"],
            "kafka": article["kafka"]
        },
        "$setOnInsert": article
    },
    upsert=True
)
            # -----------------------------------------
            # Statistics
            # -----------------------------------------

            if result.upserted_id:
                inserted += 1
                logger.info(
                    f"[INSERTED] {article['source']['name']} | {article['link']}"
                )
            else:
                duplicates += 1
                logger.info(
                    f"[DUPLICATE] {article['link']}"
                )

except KeyboardInterrupt:

    logger.info(LOG_SEPARATOR)
    logger.info("Keyboard Interrupt Received")
    logger.info(LOG_SEPARATOR)

except Exception as e:

    logger.exception(
        f"Kafka Consumer Failed : {e}"
    )

finally:

    # =================================================
    # Close Kafka Consumer
    # =================================================

    try:
        consumer.close()
        logger.info(
            "Kafka Consumer Closed"
        )
    except Exception as e:
        logger.warning(
            f"Unable To Close Kafka Consumer : {e}"
        )

    # =================================================
    # Close MongoDB Connection
    # =================================================

    try:
        client.close()
        logger.info(
            "MongoDB Connection Closed"
        )
    except Exception as e:
        logger.warning(
            f"Unable To Close MongoDB : {e}"
        )

    # =================================================
    # Runtime
    # =================================================

    duration = (
        datetime.now(UTC) - started
    ).total_seconds()

    # =================================================
    # Final Summary
    # =================================================

    logger.info(LOG_SEPARATOR)
    logger.info("Kafka Consumer Summary")
    logger.info(LOG_SEPARATOR)
    logger.info(
        f"Inserted Articles   : {inserted}"
    )
    logger.info(
        f"Duplicate Articles  : {duplicates}"
    )
    logger.info(
        f"Updated Articles    : {updated}"
    )
    logger.info(
        f"Failed Articles     : {failed}"
    )
    logger.info(
        f"Processing Time     : {duration:.2f} sec"
    )
    logger.info(
        f"Consumer Group      : {KAFKA_CONSUMER_GROUP}"
    )
    logger.info(
        f"Kafka Topic         : {KAFKA_TOPIC}"
    )
    logger.info(
        f"Database            : {DATABASE_NAME}"
    )
    logger.info(
        f"Collection          : {REALTIME_COLLECTION_NAME}"
    )
    logger.info(LOG_SEPARATOR)
    logger.info("Kafka Consumer Stopped")
    logger.info(LOG_SEPARATOR)

