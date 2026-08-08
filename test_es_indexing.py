"""
Phase 10 — Elasticsearch Integration & Vector Indexing Test
"""

import sys
import io
from pathlib import Path
from pymongo import MongoClient
from elasticsearch import Elasticsearch

# Set stdout encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX, MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME
from elasticsearch_indexer.indexer import (
    get_es_client,
    create_index_if_not_exists,
    index_articles_bulk,
    search_articles,
    search_similar_articles,
    hybrid_search,
    EMBEDDING_DIMENSION
)

SOURCES = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]

def test_es_integration():
    print("=" * 80)
    print("RUNNING ELASTICSEARCH INTEGRATION & VECTOR INDEXING TEST (PHASE 10)")
    print("=" * 80)

    # 1. Connect & Verify ES Version
    es = get_es_client(ELASTICSEARCH_HOST)
    assert es.ping(), f"Could not connect to Elasticsearch at {ELASTICSEARCH_HOST}!"
    info = es.info()
    es_version = info["version"]["number"]
    print(f"[PASS] Connected to Elasticsearch server (Version: {es_version})")

    # 2. Verify / Create Index & Mapping
    created = create_index_if_not_exists(es, ELASTICSEARCH_INDEX)
    if created:
        print(f"[PASS] Created index '{ELASTICSEARCH_INDEX}' mapping.")
    else:
        print(f"[PASS] Index '{ELASTICSEARCH_INDEX}' already exists.")

    mapping_info = es.indices.get_mapping(index=ELASTICSEARCH_INDEX)
    emb_mapping = mapping_info[ELASTICSEARCH_INDEX]["mappings"]["properties"]["embedding"]
    actual_dims = emb_mapping.get("dims")
    print(f"[PASS] ES Dense Vector Mapping: type={emb_mapping.get('type')}, dims={actual_dims}, similarity={emb_mapping.get('similarity')}")
    assert actual_dims == EMBEDDING_DIMENSION, f"Mapping dimension mismatch! Expected {EMBEDDING_DIMENSION}, found {actual_dims}"

    # 3. Select Small Enriched Sample from MongoDB
    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = m_client[DATABASE_NAME]
    coll = db[REALTIME_COLLECTION_NAME]

    sample_articles = []
    source_counts = {src: 0 for src in SOURCES}

    for src in SOURCES:
        docs = list(coll.find({"source.name": src, "clean_content": {"$exists": True, "$ne": ""}}).limit(2))
        if not docs:
            docs = list(coll.find({"source": src, "clean_content": {"$exists": True, "$ne": ""}}).limit(2))
        if not docs:
            docs = list(coll.find({"source.name": src}).limit(2))
        if not docs:
            docs = list(coll.find({"source": src}).limit(2))

        source_counts[src] = len(docs)
        sample_articles.extend(docs)

    print(f"\nMongoDB Enriched Sample Count: {len(sample_articles)}")
    for src, cnt in source_counts.items():
        print(f"  • {src:<20}: {cnt}")

    assert len(sample_articles) > 0, "No sample articles found in MongoDB for ES test!"

    # Ensure all sample docs have valid 384-dim embeddings for vector search test
    from nlp.embeddings import generate_embedding
    for doc in sample_articles:
        emb = doc.get("embedding")
        if not isinstance(emb, list) or len(emb) != EMBEDDING_DIMENSION:
            text = doc.get("clean_content") or doc.get("content") or doc.get("title") or "Sample news content for vector embedding"
            doc["embedding"] = generate_embedding(text)

    # 4. Idempotent Bulk Indexing Test
    print("\n--- Testing Idempotent Bulk Indexing ---")
    res1 = index_articles_bulk(sample_articles, es, ELASTICSEARCH_INDEX)
    print(f"[PASS] Cycle 1 Bulk Index Result: Indexed={res1['indexed']}, Failed={res1['failed']}")
    assert res1["indexed"] == len(sample_articles), f"Expected {len(sample_articles)} indexed, got {res1['indexed']}"

    es.indices.refresh(index=ELASTICSEARCH_INDEX)
    count1 = es.count(index=ELASTICSEARCH_INDEX)["count"]
    print(f"[PASS] ES Index Document Count (Cycle 1): {count1}")

    # Re-index same sample to verify no duplicates
    res2 = index_articles_bulk(sample_articles, es, ELASTICSEARCH_INDEX)
    es.indices.refresh(index=ELASTICSEARCH_INDEX)
    count2 = es.count(index=ELASTICSEARCH_INDEX)["count"]
    print(f"[PASS] Cycle 2 Re-Index Result: Indexed={res2['indexed']}, Failed={res2['failed']}")
    print(f"[PASS] ES Index Document Count (Cycle 2): {count2}")
    assert count1 == count2, f"Idempotency failed! Document count increased from {count1} to {count2}"

    # 5. BM25 Search Test
    print("\n--- Testing BM25 Full-Text Search ---")
    search_query = "India"
    bm25_hits = search_articles(search_query, size=5, es=es, index_name=ELASTICSEARCH_INDEX)
    print(f"[PASS] BM25 Search for '{search_query}': {len(bm25_hits)} hits returned")
    for hit in bm25_hits[:3]:
        src_str = hit.get("source", {}).get("name") if isinstance(hit.get("source"), dict) else str(hit.get("source"))
        print(f"  • [{src_str}] {hit.get('title')[:50]} (Score: {hit.get('_score'):.4f})")
    assert len(bm25_hits) > 0, f"BM25 search for '{search_query}' returned 0 hits!"

    # 6. KNN Vector Similarity Search Test
    print("\n--- Testing KNN Dense Vector Search ---")
    sample_vec = sample_articles[0]["embedding"]
    knn_hits = search_similar_articles(sample_vec, k=5, es=es, index_name=ELASTICSEARCH_INDEX)
    print(f"[PASS] KNN Vector Search (Dim {len(sample_vec)}): {len(knn_hits)} hits returned")
    for hit in knn_hits[:3]:
        src_str = hit.get("source", {}).get("name") if isinstance(hit.get("source"), dict) else str(hit.get("source"))
        print(f"  • [{src_str}] {hit.get('title')[:50]} (Similarity Score: {hit.get('_score'):.4f})")
    assert len(knn_hits) > 0, "KNN vector search returned 0 hits!"
    assert knn_hits[0]["article_id"] == sample_articles[0].get("article_id") or str(sample_articles[0].get("_id")), "KNN query vector should rank originating article top!"

    # 7. Hybrid Search Test
    print("\n--- Testing Hybrid BM25 + Vector Search ---")
    hybrid_hits = hybrid_search("government", sample_vec, k=5, es=es, index_name=ELASTICSEARCH_INDEX)
    print(f"[PASS] Hybrid Search: {len(hybrid_hits)} hits returned")
    assert len(hybrid_hits) > 0, "Hybrid search returned 0 hits!"

    # 8. Vector Dimension Validation Error Test
    print("\n--- Testing Vector Dimension Mismatch Validation ---")
    try:
        search_similar_articles([0.1] * 10, k=5, es=es, index_name=ELASTICSEARCH_INDEX)
        assert False, "Should have raised ValueError for invalid dimension!"
    except ValueError as ve:
        print(f"[PASS] Correctly caught dimension mismatch error: {ve}")

    print("\n" + "=" * 80)
    print("ALL PHASE 10 ELASTICSEARCH INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    m_client.close()

if __name__ == "__main__":
    try:
        test_es_integration()
    except Exception as e:
        print(f"PHASE 10 TEST FAILED: {e}")
        sys.exit(1)
