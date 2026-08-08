"""
Phase 2 — Data Model & Schema Verification Test

Tests schema consistency across collectors, crawlers, and consumer logic.
"""

import sys
import hashlib
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from bootstrap.common_collector import build_article, generate_article_id

def test_common_collector_schema():
    url = "https://www.economictimes.indiatimes.com/industry/banking/finance/test-article/articleshow/1234567.cms"
    published = "2026-08-08 12:00:00"
    source = "Economic Times"
    
    article = build_article(url, published, source, ingestion_type="bootstrap")
    
    # Checks
    assert "article_id" in article, "Missing article_id"
    assert len(article["article_id"]) == 64, f"article_id should be 64-char SHA256, got {len(article['article_id'])}"
    assert article["article_id"] == generate_article_id(url), "article_id should match SHA256 hash"
    assert article["source"]["name"] == "Economic Times", f"source.name mismatch: {article['source']['name']}"
    assert article["ingestion_type"] == "bootstrap", f"ingestion_type mismatch: {article['ingestion_type']}"
    print("[PASS] TEST 1: build_article produces standard schema.")

def test_sha256_determinism():
    url = "https://www.thehindu.com/news/national/test-news/article999.ece"
    id1 = hashlib.sha256(url.encode("utf-8")).hexdigest()
    id2 = generate_article_id(url)
    assert id1 == id2, "SHA256 generation mismatch"
    print("[PASS] TEST 2: SHA256 article_id is deterministic.")

def test_source_taxonomies():
    supported_sources = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]
    for src in supported_sources:
        art = build_article("https://example.com/test", "2026-08-08", src)
        assert art["source"]["name"] in supported_sources, f"Unsupported source name: {art['source']['name']}"
    print("[PASS] TEST 3: Source taxonomy is valid and supported.")

if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("=" * 60)
    print("RUNNING PHASE 2 SCHEMA VALIDATION TESTS")
    print("=" * 60)
    try:
        test_common_collector_schema()
        test_sha256_determinism()
        test_source_taxonomies()
        print("=" * 60)
        print("ALL PHASE 2 TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"PHASE 2 TEST FAILED: {e}")
        sys.exit(1)
