"""
============================================================
Automatic Real-Time News Ingestion Service
============================================================
Project : News Intelligence Platform
Module  : ingestion_service
Version : 1.0 (Production)
============================================================

Continuous background service that:
1. Polls RSS/sitemap feeds from supported news sources.
2. Normalizes article schema & generates SHA256 article_id.
3. Durable deduplication via MongoDB `ingestion_state` & in-memory cache.
4. Publishes newly discovered articles to Kafka topic `news-topic-v2`.
5. Supports configurable polling interval (INGESTION_INTERVAL_SECONDS).
6. Handles graceful shutdown (SIGINT/SIGTERM).
"""

import os
import sys
import json
import time
import signal
import logging
import hashlib
import feedparser
from datetime import datetime, UTC
from pathlib import Path

from kafka import KafkaProducer
from pymongo import MongoClient

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    HEADERS,
)

# ==========================================================
# Configuration & Constants
# ==========================================================

INGESTION_INTERVAL_SECONDS = int(
    os.getenv("INGESTION_INTERVAL_SECONDS", "60")
)

STATE_COLLECTION_NAME = "ingestion_state"

RSS_SOURCES = {
    "Economic Times": [
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms"
    ],

    "The Hindu": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.thehindu.com/business/feeder/default.rss"
    ],

    "Indian Express": [
        "https://indianexpress.com/section/india/feed/",
        "https://indianexpress.com/section/business/feed/"
    ],

    "Hindustan Times": [
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml"
    ]
}

# ==========================================================
# Logger Setup
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("IngestionService")

# Global flag for graceful shutdown
running = True

def handle_signal(sig, frame):
    global running
    logger.info(f"Received signal {sig}. Initiating graceful shutdown...")
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# ==========================================================
# Helpers
# ==========================================================

def json_serializer(value):
    """JSON Serializer handling datetime objects."""
    return json.dumps(
        value,
        default=lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime)
            else str(obj)
        ),
        ensure_ascii=False
    ).encode("utf-8")

def get_kafka_producer():
    """Create durable Kafka Producer."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=json_serializer,
        acks="all",
        retries=5,
        request_timeout_ms=30000,
        delivery_timeout_ms=120000
    )

def init_durable_cache(db):
    """Load existing published article_ids into memory cache for speed."""
    published_cache = set()
    
    # Load from ingestion_state
    state_coll = db[STATE_COLLECTION_NAME]
    for doc in state_coll.find({}, {"article_id": 1, "link": 1}):
        if "article_id" in doc and doc["article_id"]:
            published_cache.add(doc["article_id"])

    # Load from realtime_articles
    realtime_coll = db[REALTIME_COLLECTION_NAME]
    for doc in realtime_coll.find({}, {"article_id": 1, "link": 1}):
        if "article_id" in doc and doc["article_id"]:
            published_cache.add(doc["article_id"])
        elif "link" in doc and doc["link"]:
            published_cache.add(hashlib.sha256(doc["link"].encode("utf-8")).hexdigest())

    logger.info(f"Durable ingestion cache initialized with {len(published_cache)} article IDs.")
    return published_cache

# ==========================================================
# Ingestion Cycle
# ==========================================================

def run_ingestion_cycle(producer, db, published_cache):
    """
    Executes one complete polling cycle across all four news sources.
    Returns summary statistics dictionary.
    """
    state_coll = db[STATE_COLLECTION_NAME]
    
    stats = {
        "sources": {},
        "total_discovered": 0,
        "total_new": 0,
        "total_duplicates": 0,
        "kafka_sent": 0,
        "failures": 0
    }

    logger.info("=" * 70)
    logger.info("STARTING REALTIME INGESTION CYCLE")
    logger.info("=" * 70)

    for source_name, urls in RSS_SOURCES.items():
        src_discovered = 0
        src_new = 0
        src_dup = 0
        src_failed = 0

        for url in urls:
            try:
                feed = feedparser.parse(url, request_headers=HEADERS)
                if not feed.entries:
                    continue

                for entry in feed.entries:
                    link = entry.get("link", "").strip()
                    if not link:
                        continue

                    src_discovered += 1

                    # Generate canonical article_id (SHA256)
                    article_id = hashlib.sha256(link.encode("utf-8")).hexdigest()
                    now_iso = datetime.now(UTC).isoformat()

                    # Deduplication check
                    if article_id in published_cache:
                        src_dup += 1
                        continue

                    # Secondary DB check if cache missed
                    if state_coll.find_one({"article_id": article_id}):
                        published_cache.add(article_id)
                        src_dup += 1
                        continue

                    # Construct Standard Schema Article
                    article = {
                        "article_id": article_id,
                        "link": link,
                        "source": {
                            "name": source_name,
                            "country": "India",
                            "language": "en",
                            "type": "rss"
                        },
                        "title": entry.get("title", "").strip(),
                        "description": entry.get("summary", "").strip(),
                        "content": "",
                        "clean_content": "",
                        "authors": ["Unknown"],
                        "language": "en",
                        "published_date": entry.get("published") or now_iso,
                        "published_datetime": now_iso,
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "fetched_at": now_iso,
                        "last_pipeline_update": now_iso,
                        "ingestion_type": "realtime",
                        "processing": {
                            "status": "PENDING",
                            "stage": "ingested",
                            "retry_count": 0
                        }
                    }

                    # Publish to Kafka
                    try:
                        future = producer.send(
                            KAFKA_TOPIC,
                            key=article_id.encode("utf-8"),
                            value=article
                        )
                        # Wait briefly for ack
                        future.get(timeout=10)

                        # Record in durable MongoDB state
                        state_coll.update_one(
                            {"article_id": article_id},
                            {
                                "$set": {
                                    "article_id": article_id,
                                    "link": link,
                                    "source": source_name,
                                    "published_at": now_iso
                                }
                            },
                            upsert=True
                        )

                        published_cache.add(article_id)
                        src_new += 1

                    except Exception as kerr:
                        logger.error(f"Kafka send error for {link}: {kerr}")
                        src_failed += 1

            except Exception as fe:
                logger.error(f"Error fetching feed {url}: {fe}")
                src_failed += 1

        stats["sources"][source_name] = {
            "discovered": src_discovered,
            "new": src_new,
            "duplicate": src_dup,
            "failed": src_failed
        }
        stats["total_discovered"] += src_discovered
        stats["total_new"] += src_new
        stats["total_duplicates"] += src_dup
        stats["kafka_sent"] += src_new
        stats["failures"] += src_failed

    producer.flush()

    logger.info("=" * 70)
    logger.info("INGESTION CYCLE SUMMARY")
    logger.info("=" * 70)
    for src, sdata in stats["sources"].items():
        logger.info(
            f"{src:<18} : discovered={sdata['discovered']:<4} "
            f"new={sdata['new']:<4} duplicate={sdata['duplicate']:<4} failed={sdata['failed']:<4}"
        )
    logger.info("-" * 70)
    logger.info(f"TOTAL DISCOVERED : {stats['total_discovered']}")
    logger.info(f"NEW ARTICLES     : {stats['total_new']}")
    logger.info(f"DUPLICATES       : {stats['total_duplicates']}")
    logger.info(f"KAFKA SENT       : {stats['kafka_sent']}")
    logger.info(f"FAILURES         : {stats['failures']}")
    logger.info("=" * 70)

    return stats

# ==========================================================
# Daemon Entry Point
# ==========================================================

def start_ingestion_daemon():
    global running

    logger.info("Starting Automatic News Ingestion Daemon...")
    logger.info(f"Polling Interval: {INGESTION_INTERVAL_SECONDS} seconds")
    logger.info(f"Kafka Topic     : {KAFKA_TOPIC}")

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    producer = get_kafka_producer()
    published_cache = init_durable_cache(db)

    try:
        while running:
            run_ingestion_cycle(producer, db, published_cache)
            logger.info(f"Sleeping for {INGESTION_INTERVAL_SECONDS} seconds...")
            
            # Sleep in 1-second chunks for quick signal responsiveness
            for _ in range(INGESTION_INTERVAL_SECONDS):
                if not running:
                    break
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Ingestion daemon interrupted by user.")
    except Exception as e:
        logger.exception(f"Unhandled error in ingestion daemon: {e}")
    finally:
        logger.info("Flushing Kafka Producer...")
        producer.flush()
        producer.close()
        client.close()
        logger.info("Ingestion Service Shutdown Complete.")

if __name__ == "__main__":
    start_ingestion_daemon()
