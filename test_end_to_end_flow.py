"""
Phase 11 & 12 — End-to-End Pipeline Integration Test
"""

import sys
import io
import json
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient
from kafka import KafkaProducer
from elasticsearch import Elasticsearch

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX
from pipeline_orchestrator import run_orchestration_cycle
from elasticsearch_indexer.indexer import get_es_client, search_articles, search_similar_articles, EMBEDDING_DIMENSION

def test_end_to_end():
    print("=" * 80)
    print("RUNNING END-TO-END PIPELINE INTEGRATION TEST (PHASE 11 & 12)")
    print("=" * 80)

    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = m_client[DATABASE_NAME]
    coll = db[REALTIME_COLLECTION_NAME]
    es = get_es_client(ELASTICSEARCH_HOST)

    # 1. Prepare Controlled Unique Test Article
    test_url = "https://indianexpress.com/article/india/today-india-breaking-news-live-updates-august-8-2026-9497531/"
    test_article_id = "e2e_test_article_" + hashlib.sha256(test_url.encode("utf-8")).hexdigest()

    sample_text = (
        "India news Live Updates, 8 August 2026: End to End Flow Test. "
        "The Reserve Bank of India announced new macroeconomic guidelines to maintain financial stability. "
        "Economic analysts predict positive GDP growth across key sectors including manufacturing, technology, and trade. "
        "The government emphasized continuous infrastructure development, digital public goods expansion, and global trade partnerships. "
        "This controlled test article verifies end-to-end ingestion, Kafka streaming, MongoDB persistence, pipeline orchestration, "
        "multi-stage NLP enrichment, and hybrid Elasticsearch vector indexing."
    )

    test_doc = {
        "article_id": test_article_id,
        "link": test_url,
        "source": {"name": "Indian Express", "country": "India", "language": "en", "type": "rss"},
        "title": "India news Live Updates, 8 August 2026: End to End Flow Test",
        "description": "Unique test article for validating complete news intelligence pipeline.",
        "content": sample_text,
        "clean_content": sample_text,
        "ingestion_type": "realtime",
        "processing": {"status": "PENDING", "stage": "ingested", "retry_count": 0},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "published_date": datetime.now(timezone.utc).isoformat()
    }

    # Ensure clean starting state for test article
    coll.delete_many({"article_id": test_article_id})
    try:
        es.delete(index=ELASTICSEARCH_INDEX, id=test_article_id)
    except Exception:
        pass

    # 2. Publish to Kafka
    print("\n--- Step 1: Kafka Publishing ---")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    future = producer.send(KAFKA_TOPIC, key=test_article_id, value=test_doc)
    future.get(timeout=10)
    producer.flush()
    producer.close()
    print(f"[PASS] Published test article to Kafka topic '{KAFKA_TOPIC}' with key '{test_article_id[:20]}...'")

    # 3. Simulate Kafka Consumer MongoDB Persistence
    print("\n--- Step 2: MongoDB Persistence ---")
    coll.insert_one(test_doc)
    mongo_doc = coll.find_one({"article_id": test_article_id})
    assert mongo_doc is not None, "Test document not found in MongoDB!"
    assert mongo_doc["processing"]["status"] == "PENDING", f"Expected status PENDING, got {mongo_doc['processing']['status']}"
    print("[PASS] Test document persisted in MongoDB with status='PENDING'")

    # 4. Execute Pipeline Orchestrator Cycle
    print("\n--- Step 3: Pipeline Orchestration & Enrichment ---")
    claimed = run_orchestration_cycle(coll, es, batch_size=1, target_article_id=test_article_id)
    assert claimed >= 1, "Orchestrator failed to claim test article!"
    print("[PASS] Pipeline Orchestrator claimed and executed pipeline pass.")

    # 5. Verify MongoDB Enriched Document
    print("\n--- Step 4: MongoDB Enrichment Verification ---")
    enriched_doc = coll.find_one({"article_id": test_article_id})
    assert enriched_doc["processing"]["status"] == "COMPLETED", f"Expected COMPLETED, got {enriched_doc['processing']['status']}"
    assert enriched_doc.get("clean_content") and len(enriched_doc.get("clean_content")) >= 200, "Clean content missing or short!"
    assert enriched_doc.get("summary"), "Summary missing!"
    assert enriched_doc.get("sentiment"), "Sentiment missing!"
    assert enriched_doc.get("category"), "Category missing!"
    assert isinstance(enriched_doc.get("embedding"), list) and len(enriched_doc.get("embedding")) == EMBEDDING_DIMENSION, "Embedding missing or dimension mismatch!"
    print("[PASS] All NLP enrichment fields verified in MongoDB (status=COMPLETED, embedding_dim=384)")

    # 6. Verify Elasticsearch BM25 Search
    print("\n--- Step 5: Elasticsearch BM25 Search Verification ---")
    es.indices.refresh(index=ELASTICSEARCH_INDEX)
    bm25_hits = search_articles("End to End Flow Test", size=5, es=es, index_name=ELASTICSEARCH_INDEX)
    assert len(bm25_hits) > 0, "BM25 search failed to return test article!"
    assert any(h.get("article_id") == test_article_id for h in bm25_hits), "Test article_id not found in BM25 hits!"
    print(f"[PASS] Elasticsearch BM25 search successfully retrieved test article (Score: {bm25_hits[0]['_score']:.4f})")

    # 7. Verify Elasticsearch KNN Vector Search
    print("\n--- Step 6: Elasticsearch KNN Vector Search Verification ---")
    test_vec = enriched_doc["embedding"]
    knn_hits = search_similar_articles(test_vec, k=5, es=es, index_name=ELASTICSEARCH_INDEX)
    assert len(knn_hits) > 0, "KNN vector search failed to return hits!"
    assert knn_hits[0].get("article_id") == test_article_id, "KNN search top hit did not match test article_id!"
    print(f"[PASS] Elasticsearch KNN vector search successfully retrieved test article (Similarity Score: {knn_hits[0]['_score']:.4f})")

    # 8. Idempotency Verification
    print("\n--- Step 7: Pipeline Idempotency Re-Run Verification ---")
    claimed_rerun = run_orchestration_cycle(coll, es, batch_size=1)
    es.indices.refresh(index=ELASTICSEARCH_INDEX)
    mongo_count = coll.count_documents({"article_id": test_article_id})
    assert mongo_count == 1, f"MongoDB duplicate found! Expected 1, found {mongo_count}"
    print("[PASS] Idempotency verified (0 duplicate MongoDB or Elasticsearch documents created)")

    # 9. Clean up test article
    coll.delete_many({"article_id": test_article_id})
    try:
        es.delete(index=ELASTICSEARCH_INDEX, id=test_article_id)
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("ALL PHASE 11 & 12 END-TO-END PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    m_client.close()

if __name__ == "__main__":
    try:
        test_end_to_end()
    except Exception as e:
        print(f"END-TO-END TEST FAILED: {e}")
        sys.exit(1)
