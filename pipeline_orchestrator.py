"""
=====================================================
Pipeline Orchestrator Daemon
Version : 5.0 (Production Ready)
=====================================================

Purpose:
Continuously claims eligible articles from MongoDB (PENDING, retryable FAILED, or stale PROCESSING),
executes Phase 7 Extraction -> Phase 8 Cleaning -> Phase 9 NLP Enrichment -> Phase 10 ES Indexing.
"""

from __future__ import annotations

import argparse
import io
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pymongo import MongoClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME, ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX
from realtime_pipeline.realtime_nlp_pipeline import process_article, get_mongo_query
from elasticsearch_indexer.indexer import index_article, get_es_client, create_index_if_not_exists

# Configuration
ORCHESTRATOR_POLL_INTERVAL_SECONDS = 3
ORCHESTRATOR_BATCH_SIZE = 5
MAX_RETRY_COUNT = 3
STALE_LEASE_TIMEOUT_SECONDS = 300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PipelineOrchestrator")

RUNNING = True

def signal_handler(signum, frame):
    global RUNNING
    logger.info("Shutdown signal received. Stopping Pipeline Orchestrator...")
    RUNNING = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def claim_next_article(collection, target_article_id=None):
    """Atomically claim the next eligible article for processing."""
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(seconds=STALE_LEASE_TIMEOUT_SECONDS)

    if target_article_id:
        query = get_mongo_query(target_article_id)
    else:
        query = {
            "$or": [
                {"processing.status": "PENDING"},
                {
                    "processing.status": "FAILED",
                    "processing.retryable": {"$ne": False},
                    "$or": [
                        {"processing.retry_count": {"$lt": MAX_RETRY_COUNT}},
                        {"processing.retry_count": {"$exists": False}}
                    ]
                },
                {
                    "processing.status": "PROCESSING",
                    "$or": [
                        {"processing.claimed_at": {"$lt": stale_cutoff}},
                        {"processing.claimed_at": {"$exists": False}}
                    ]
                }
            ]
        }

    update = {
        "$set": {
            "processing.status": "PROCESSING",
            "processing.stage": "orchestrator_claimed",
            "processing.claimed_at": now,
            "updated_at": now
        }
    }

    # Atomic find and update to prevent concurrent duplicate claims
    article = collection.find_one_and_update(
        query,
        update,
        return_document=True
    )
    return article

def run_orchestration_cycle(db_coll, es_client, batch_size=ORCHESTRATOR_BATCH_SIZE, target_article_id=None):
    """Executes one processing cycle up to batch_size articles."""
    pending_count = db_coll.count_documents({
        "$or": [
            {"processing.status": "PENDING"},
            {"processing.status": "FAILED", "processing.retryable": {"$ne": False}}
        ]
    })

    claimed_count = 0
    completed_count = 0
    failed_count = 0
    es_indexed_count = 0

    for _ in range(batch_size):
        if not RUNNING:
            break

        article = claim_next_article(db_coll, target_article_id=target_article_id)
        if not article:
            break

        claimed_count += 1
        article_id = article.get("article_id") or str(article.get("_id"))
        source_val = article.get("source", {})
        src_name = source_val.get("name") if isinstance(source_val, dict) else str(source_val)

        logger.info(f"Claimed Article: {article_id[:20]}... | Source: {src_name}")

        try:
            # 1. Run Pipeline (Extraction -> Cleaning -> NLP)
            t_start = time.perf_counter()
            success = process_article(article["_id"], db_coll)
            duration = time.perf_counter() - t_start

            if success:
                # Load enriched document
                enriched_doc = db_coll.find_one(get_mongo_query(article["_id"]))

                # 2. Index to Elasticsearch
                es_ok = index_article(enriched_doc, es=es_client, index_name=ELASTICSEARCH_INDEX)

                now = datetime.now(timezone.utc)
                if es_ok:
                    es_indexed_count += 1
                    db_coll.update_one(
                        get_mongo_query(article["_id"]),
                        {
                            "$set": {
                                "processing.status": "COMPLETED",
                                "processing.stage": "indexed_es",
                                "processing.es_indexed": True,
                                "processing.completed_at": now,
                                "processing.total_orchestrator_time": round(duration, 4),
                                "updated_at": now
                            }
                        }
                    )
                    completed_count += 1
                    logger.info(f"✅ Successfully Processed & Indexed Article: {article_id[:20]}... in {duration:.2f}s")
                else:
                    logger.error(f"❌ ES Indexing failed for article {article_id}")
                    failed_count += 1
                    db_coll.update_one(
                        get_mongo_query(article["_id"]),
                        {
                            "$set": {
                                "processing.status": "FAILED",
                                "processing.stage": "es_indexing",
                                "processing.error": "Elasticsearch indexing failed",
                                "processing.retryable": True,
                                "updated_at": now
                            },
                            "$inc": {"processing.retry_count": 1}
                        }
                    )
            else:
                failed_count += 1
                curr_retries = article.get("processing", {}).get("retry_count", 0) + 1
                retryable = curr_retries < MAX_RETRY_COUNT
                logger.warning(f"⚠️ NLP Pipeline returned failure for article {article_id} (retry {curr_retries}/{MAX_RETRY_COUNT})")
                
                db_coll.update_one(
                    get_mongo_query(article["_id"]),
                    {
                        "$set": {
                            "processing.status": "FAILED",
                            "processing.retryable": retryable,
                            "updated_at": datetime.now(timezone.utc)
                        },
                        "$inc": {"processing.retry_count": 1}
                    }
                )

        except Exception as exc:
            failed_count += 1
            logger.exception(f"Unhandled exception processing article {article_id}: {exc}")
            curr_retries = article.get("processing", {}).get("retry_count", 0) + 1
            db_coll.update_one(
                get_mongo_query(article["_id"]),
                {
                    "$set": {
                        "processing.status": "FAILED",
                        "processing.stage": "exception",
                        "processing.error": str(exc),
                        "processing.retryable": curr_retries < MAX_RETRY_COUNT,
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$inc": {"processing.retry_count": 1}
                }
            )

    if claimed_count > 0:
        print("\n" + "=" * 60)
        print("PIPELINE ORCHESTRATOR CYCLE SUMMARY")
        print("=" * 60)
        print(f"Batch Size   : {batch_size}")
        print(f"Pending Docs : {pending_count}")
        print(f"Claimed      : {claimed_count}")
        print(f"Completed    : {completed_count}")
        print(f"Failed       : {failed_count}")
        print(f"ES Indexed   : {es_indexed_count}")
        print("=" * 60 + "\n")

    return claimed_count

def main():
    parser = argparse.ArgumentParser(description="Pipeline Orchestrator Daemon")
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    args = parser.parse_args()

    print("=" * 80)
    print("STARTING PIPELINE ORCHESTRATOR DAEMON")
    print("=" * 80)

    # Initialize Clients
    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = m_client[DATABASE_NAME]
    coll = db[REALTIME_COLLECTION_NAME]

    es_client = get_es_client(ELASTICSEARCH_HOST)
    create_index_if_not_exists(es_client, ELASTICSEARCH_INDEX)

    logger.info("Connected to MongoDB & Elasticsearch cleanly.")

    while RUNNING:
        claimed = run_orchestration_cycle(coll, es_client)

        if args.once:
            break

        if claimed == 0:
            time.sleep(ORCHESTRATOR_POLL_INTERVAL_SECONDS)

    logger.info("Pipeline Orchestrator shut down cleanly.")
    m_client.close()

if __name__ == "__main__":
    main()
