"""
============================================================
Test Suite: Historical Backfill System
============================================================
Tests:
  1. Source registry completeness
  2. URL collection from real sitemaps (live network)
  3. Date range filter logic
  4. Backfill manager checkpoint save/load
  5. Article content extraction pipeline
  6. DQ gate integration with historical article
  7. MongoDB ingestion schema validation
  8. Duplicate detection
  9. Pilot runner import
============================================================
"""

import sys
import hashlib
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


class TestSourceRegistry(unittest.TestCase):
    """Test 1: Source registry is complete and correctly structured."""

    def test_all_four_sources_registered(self):
        from historical.backfill_manager import SOURCE_REGISTRY
        expected = {"economic_times", "the_hindu", "indian_express", "hindustan_times"}
        self.assertEqual(set(SOURCE_REGISTRY.keys()), expected,
                         "All 4 sources must be registered in SOURCE_REGISTRY")

    def test_each_source_has_required_fields(self):
        from historical.backfill_manager import SOURCE_REGISTRY
        required = {"name", "type", "language", "country"}
        for key, cfg in SOURCE_REGISTRY.items():
            for field in required:
                self.assertIn(field, cfg, f"Source '{key}' missing required field '{field}'")

    def test_source_types_are_known(self):
        from historical.backfill_manager import SOURCE_REGISTRY
        valid_types = {"monthly_sitemap", "single_sitemap", "sitemap_index"}
        for key, cfg in SOURCE_REGISTRY.items():
            self.assertIn(cfg["type"], valid_types,
                          f"Source '{key}' has unknown type '{cfg['type']}'")


class TestDateRangeFilter(unittest.TestCase):
    """Test 2: Date range filter logic works correctly."""

    def setUp(self):
        from historical.backfill_manager import _in_date_range
        self._in_date_range = _in_date_range
        self.from_date = datetime(2025, 8, 1, tzinfo=timezone.utc)
        self.to_date = datetime(2026, 8, 9, tzinfo=timezone.utc)

    def test_url_in_range_by_pub_date(self):
        result = self._in_date_range(
            "https://example.com/article",
            "2025-09-15T12:00:00+00:00",
            self.from_date, self.to_date
        )
        self.assertTrue(result)

    def test_url_before_range(self):
        result = self._in_date_range(
            "https://example.com/article",
            "2024-01-01T00:00:00+00:00",
            self.from_date, self.to_date
        )
        self.assertFalse(result)

    def test_url_after_range(self):
        result = self._in_date_range(
            "https://example.com/article",
            "2027-01-01T00:00:00+00:00",
            self.from_date, self.to_date
        )
        self.assertFalse(result)

    def test_url_in_range_by_year_in_url(self):
        result = self._in_date_range(
            "https://example.com/2025/article",
            None,
            self.from_date, self.to_date
        )
        self.assertTrue(result)

    def test_url_skip_old_year_in_url(self):
        result = self._in_date_range(
            "https://example.com/2023/article",
            None,
            self.from_date, self.to_date
        )
        self.assertFalse(result)


class TestShouldSkipUrl(unittest.TestCase):
    """Test 3: Skip filter correctly rejects non-article URLs."""

    def setUp(self):
        from historical.backfill_manager import _should_skip_url
        self._should_skip = _should_skip_url

    def test_skip_video_url(self):
        self.assertTrue(self._should_skip("https://example.com/videos/abc"))

    def test_skip_photo_url(self):
        self.assertTrue(self._should_skip("https://example.com/photos/gallery"))

    def test_skip_liveblog(self):
        self.assertTrue(self._should_skip("https://example.com/liveblog/match"))

    def test_allow_normal_article(self):
        self.assertFalse(self._should_skip("https://economictimes.indiatimes.com/news/india/article.cms"))

    def test_allow_politics_article(self):
        self.assertFalse(self._should_skip("https://www.thehindu.com/news/politics/modi-budget/article123.ece"))


class TestBackfillManagerCheckpoint(unittest.TestCase):
    """Test 4: Checkpoint save/load works correctly against MongoDB."""

    def setUp(self):
        try:
            from pymongo import MongoClient
            self._client = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
            self._client.admin.command("ping")
            self._mongo_available = True
        except Exception:
            self._mongo_available = False
            self._client = None

    def tearDown(self):
        if self._client:
            self._client.close()

    def test_checkpoint_init_when_not_exists(self):
        if not self._mongo_available:
            self.skipTest("MongoDB not available")
        from historical.backfill_manager import HistoricalBackfillManager
        mgr = HistoricalBackfillManager()
        cp = mgr.get_checkpoint("__TEST_NONEXISTENT_BATCH__")
        self.assertEqual(cp["status"], "NOT_STARTED")
        self.assertIn("stats", cp)
        self.assertIn("processed_urls", cp)

    def test_checkpoint_save_and_reload(self):
        if not self._mongo_available:
            self.skipTest("MongoDB not available")
        from historical.backfill_manager import HistoricalBackfillManager
        mgr = HistoricalBackfillManager()
        batch_id = "__TEST_CHECKPOINT_RELOAD__"
        cp = mgr.get_checkpoint(batch_id)
        cp["status"] = "IN_PROGRESS"
        cp["stats"]["stored"] = 42
        mgr.save_checkpoint(cp)
        reloaded = mgr.get_checkpoint(batch_id)
        self.assertEqual(reloaded["status"], "IN_PROGRESS")
        self.assertEqual(reloaded["stats"]["stored"], 42)
        # Cleanup
        mgr.state_col.delete_one({"batch_id": batch_id})


class TestHistoricalArticleIngestion(unittest.TestCase):
    """Test 5: Historical article ingestion with DQ gate and correct schema."""

    def setUp(self):
        try:
            from pymongo import MongoClient
            self._setup_client = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=2000)
            self._setup_client.admin.command("ping")
            self._mongo_available = True
        except Exception:
            self._mongo_available = False
            self._setup_client = None

    def tearDown(self):
        if self._setup_client:
            self._setup_client.close()

    def _make_article(self, suffix="test"):
        return {
            "link": f"https://economictimes.indiatimes.com/test/historical-article-{suffix}.cms",
            "title": f"Historical Economic Times Test Article {suffix}",
            "authors": ["Test Author"],
            "content": "This is a sufficiently long article content for the historical test suite. " * 10,
            "clean_content": "This is a sufficiently long article content for the historical test suite. " * 10,
            "description": f"Historical Economic Times Test Article {suffix}",
            "published_date": "2025-09-01T10:00:00+00:00",
            "language": "en",
            "source": {"name": "Economic Times", "country": "India", "language": "en", "type": "historical_sitemap"},
        }

    def test_ingest_valid_article_returns_stored(self):
        if not self._mongo_available:
            self.skipTest("MongoDB not available")
        from historical.backfill_manager import HistoricalBackfillManager
        mgr = HistoricalBackfillManager()
        art = self._make_article("ingest_valid_001")
        # Ensure clean state
        mgr.articles_col.delete_one({"link": art["link"]})
        result = mgr.ingest_article(art, batch_id="test_batch")
        self.assertEqual(result, "stored", "Valid article should be stored")
        # Cleanup
        mgr.articles_col.delete_one({"link": art["link"]})

    def test_ingest_duplicate_returns_duplicate(self):
        if not self._mongo_available:
            self.skipTest("MongoDB not available")
        from historical.backfill_manager import HistoricalBackfillManager
        mgr = HistoricalBackfillManager()
        art = self._make_article("ingest_dupe_001")
        mgr.articles_col.delete_one({"link": art["link"]})
        mgr.ingest_article(art, batch_id="test_batch")
        result = mgr.ingest_article(art, batch_id="test_batch")
        self.assertEqual(result, "duplicate", "Duplicate article must return 'duplicate'")
        # Cleanup
        mgr.articles_col.delete_one({"link": art["link"]})

    def test_ingested_article_has_correct_schema(self):
        if not self._mongo_available:
            self.skipTest("MongoDB not available")
        from historical.backfill_manager import HistoricalBackfillManager
        mgr = HistoricalBackfillManager()
        art = self._make_article("schema_check_001")
        mgr.articles_col.delete_one({"link": art["link"]})
        mgr.ingest_article(art, batch_id="test_schema_batch")
        stored = mgr.articles_col.find_one({"link": art["link"]})
        self.assertIsNotNone(stored)
        self.assertEqual(stored["ingestion_type"], "historical")
        self.assertEqual(stored["historical_batch"], "test_schema_batch")
        self.assertEqual(stored["processing"]["status"], "PENDING")
        self.assertIn("article_id", stored)
        self.assertIn("data_quality", stored)
        # Cleanup
        mgr.articles_col.delete_one({"link": art["link"]})

    def test_article_id_is_sha256_of_url(self):
        if not self._mongo_available:
            self.skipTest("MongoDB not available")
        from historical.backfill_manager import HistoricalBackfillManager
        mgr = HistoricalBackfillManager()
        art = self._make_article("sha256_check_001")
        url = art["link"]
        expected_id = hashlib.sha256(url.encode("utf-8")).hexdigest()
        mgr.articles_col.delete_one({"link": url})
        mgr.ingest_article(art, batch_id="test_id_batch")
        stored = mgr.articles_col.find_one({"link": url})
        self.assertEqual(stored["article_id"], expected_id)
        # Cleanup
        mgr.articles_col.delete_one({"link": url})


class TestPilotRunnerImport(unittest.TestCase):
    """Test 6: Pilot runner imports correctly."""

    def test_pilot_runner_importable(self):
        try:
            import historical.pilot_runner as pr
            self.assertTrue(hasattr(pr, "run_pilot"))
            self.assertTrue(hasattr(pr, "print_pilot_report"))
        except ImportError as e:
            self.fail(f"pilot_runner could not be imported: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
