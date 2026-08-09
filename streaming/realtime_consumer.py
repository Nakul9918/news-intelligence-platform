"""
============================================================
Realtime Kafka Consumer & MongoDB Persistence
============================================================
Project : News Intelligence Platform
Module  : realtime_consumer
Version : 3.0 (Production)
============================================================

Continuous Realtime Consumer that:
1. Listens to Kafka topic `news-topic-v2` with consumer group `news-realtime-consumer-v3`.
2. Safe JSON deserialization without crashing.
3. Durable, idempotent MongoDB persistence using SHA256 `article_id`.
4. Guarantees existing enriched NLP fields are never overwritten on duplicate replay.
5. Manually commits offsets only after successful MongoDB persistence.
6. Handles graceful shutdown (SIGINT/SIGTERM).
"""

import sys
import os
import json
import time
import signal
import logging
import hashlib
import traceback
from datetime import datetime, UTC
from pathlib import Path

from kafka import KafkaConsumer
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
)

# ==========================================================
# Logging Setup
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("RealtimeConsumer")

# Global flag for graceful shutdown
running = True

def handle_signal(sig, frame):
    global running
    logger.info(f"Received shutdown signal {sig}. Stopping consumer...")
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# ==========================================================
# Database Connection & Index Verification
# ==========================================================

def get_mongo_collection():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[REALTIME_COLLECTION_NAME]
    
    # Ensure unique index on article_id exists
    try:
        collection.create_index([("article_id", 1)], unique=True, background=True)
    except Exception as e:
        logger.warning(f"Could not ensure unique article_id index: {e}")
        
    return client, collection

# ==========================================================
# Main Consumer Process
# ==========================================================

def start_consumer(single_run=False, max_messages=None):
    global running
    
    logger.info("=" * 70)
    logger.info("STARTING REALTIME KAFKA CONSUMER (v3)")
    logger.info("=" * 70)
    logger.info(f"Kafka Server : {KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Kafka Topic  : {KAFKA_TOPIC}")
    logger.info(f"Group ID     : news-realtime-consumer-v3")
    logger.info(f"Collection   : {REALTIME_COLLECTION_NAME}")
    logger.info("=" * 70)

    client, collection = get_mongo_collection()

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="news-realtime-consumer-v3",
        enable_auto_commit=False,  # Manual commit after Mongo persistence
        value_deserializer=lambda m: m.decode("utf-8", errors="ignore")
    )

    consumed_count = 0

    try:
        while running:
            # Poll for messages with a short timeout to allow checking `running` flag
            records_dict = consumer.poll(timeout_ms=1000)
            if not records_dict:
                if single_run:
                    break
                continue

            for topic_partition, records in records_dict.items():
                for message in records:
                    if not running:
                        break

                    consumed_count += 1
                    raw_val = message.value
                    
                    logger.info(f"[RECEIVED] Partition: {message.partition} | Offset: {message.offset}")

                    # 1. Parse JSON safely
                    try:
                        article = json.loads(raw_val)
                    except Exception as je:
                        logger.error(f"[FAILED] Malformed JSON at offset {message.offset}: {je}")
                        # Commit malformed message to skip it
                        consumer.commit()
                        continue

                    # 2. Extract & Validate Fields
                    link = article.get("link", "").strip()
                    title = article.get("title", "").strip()
                    
                    if not link:
                        logger.warning(f"[FAILED] Missing link URL at offset {message.offset}. Skipping.")
                        consumer.commit()
                        continue

                    article_id = article.get("article_id")
                    if not article_id:
                        article_id = hashlib.sha256(link.encode("utf-8")).hexdigest()

                    # Source Normalization
                    raw_source = article.get("source", {})
                    if isinstance(raw_source, str):
                        source_dict = {"name": raw_source, "country": "India", "language": "en", "type": "rss"}
                    elif isinstance(raw_source, dict):
                        source_dict = raw_source
                        if "name" not in source_dict:
                            source_dict["name"] = "Unknown"
                    else:
                        source_dict = {"name": "Unknown", "country": "India", "language": "en", "type": "rss"}

                    # 3. Data Quality Gate Check
                    from qc.quality_gate import evaluate_article_quality
                    dq_result = evaluate_article_quality(article)
                    
                    if dq_result["quality_status"] == "QUARANTINED":
                        logger.warning(f"[QUARANTINED] Article '{title[:40]}' (ID: {article_id[:16]}) failed DQ (Score: {dq_result['quality_score']}). Errors: {dq_result['errors']}")
                        q_collection = client[DATABASE_NAME]["quarantine_articles"]
                        quarantined_doc = dict(article)
                        quarantined_doc["article_id"] = article_id
                        quarantined_doc["data_quality"] = dq_result
                        quarantined_doc["quarantined_at"] = datetime.now(UTC)
                        q_collection.update_one({"article_id": article_id}, {"$set": quarantined_doc}, upsert=True)
                        consumer.commit()
                        continue

                    # 4. Idempotent MongoDB Persistence
                    try:
                        # Check if article already exists
                        existing = collection.find_one({
                            "$or": [
                                {"article_id": article_id},
                                {"link": link}
                            ]
                        })

                        if existing:
                            logger.info(f"[DUPLICATE] article_id: {article_id[:16]}... | Title: {title[:40]}")
                        else:
                            now = datetime.now(UTC)
                            now_iso = now.isoformat()

                            document = {
                                "article_id": article_id,
                                "link": link,
                                "source": source_dict,
                                "title": title,
                                "description": article.get("description", ""),
                                "authors": article.get("authors", ["Unknown"]),
                                "language": article.get("language", "en"),
                                "published_date": article.get("published_date", article.get("published", "")),
                                "published_datetime": article.get("published_datetime", now_iso),
                                "created_at": now,
                                "updated_at": now,
                                "fetched_at": now,
                                "last_pipeline_update": now,
                                "content": article.get("content", ""),
                                "clean_content": "",
                                "keywords": [],
                                "entities": [],
                                "sentiment": {},
                                "category": {},
                                "summary": {"text": "", "model": ""},
                                "embedding": {"vector": [], "dimension": 0, "model": ""},
                                "data_quality": dq_result,
                                "ingestion_type": article.get("ingestion_type", "realtime"),
                                "last_pipeline_stage": "ingestion",
                                "processing": {
                                    "status": "PENDING",
                                    "stage": "ingested",
                                    "retry_count": 0
                                },
                                "status": {
                                    "ingested": True,
                                    "content_extracted": False,
                                    "content_cleaned": False,
                                    "nlp_completed": False
                                }
                            }

                            collection.insert_one(document)
                            logger.info(f"[PERSISTED] article_id: {article_id[:16]}... | Title: {title[:40]} (DQ Score: {dq_result['quality_score']})")

                        # 5. Commit Kafka Offset after Mongo operation succeeds
                        consumer.commit()
                        logger.info(f"[COMMITTED] Offset {message.offset}")

                    except DuplicateKeyError:
                        logger.info(f"[DUPLICATE] DuplicateKeyError on article_id: {article_id[:16]}...")
                        consumer.commit()
                    except PyMongoError as pme:
                        logger.error(f"[FAILED] MongoDB Error at offset {message.offset}: {pme}")
                        # Do not commit offset so message will be retried
                        time.sleep(1)

                    if max_messages and consumed_count >= max_messages:
                        running = False
                        break

    except Exception as e:
        logger.exception(f"Unexpected Consumer Error: {e}")
    finally:
        logger.info("Closing Kafka Consumer & MongoDB client...")
        consumer.close()
        client.close()
        logger.info(f"Realtime Consumer Shutdown complete. Total processed: {consumed_count}")

if __name__ == "__main__":
    start_consumer()