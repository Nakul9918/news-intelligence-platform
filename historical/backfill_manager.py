"""
============================================================
Historical News Backfill Manager & Controller
News Intelligence Platform
============================================================
Version : 4.0 (Production — Real Sitemap Collectors)
Features:
 - Connects to REAL sitemap collectors (ET, IE, HT, TheHindu).
 - Date-range filtering on collected URLs.
 - Multi-method content extraction (newspaper3k → trafilatura → BS4).
 - Data Quality Gate validation before MongoDB insertion.
 - Resumable checkpointing in MongoDB `news_db.ingestion_state`.
 - Realtime pipeline priority throttling.
 - Shared downstream processing schema with realtime ingestion.
 - Full progress reporting: discovered/valid/duplicate/quarantined/stored/remaining/%.
============================================================
"""

import sys
import os
import time
import argparse
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
    QUARANTINE_COLLECTION_NAME,
    INGESTION_STATE_COLLECTION_NAME,
    HEADERS,
    TIMEOUT,
    BOOTSTRAP_SKIP_KEYWORDS,
)
from qc.quality_gate import evaluate_article_quality

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("BackfillManager")


# =====================================================
# Source Registry
# =====================================================

SOURCE_REGISTRY = {
    "economic_times": {
        "name": "Economic Times",
        "type": "monthly_sitemap",
        "base_url": "https://economictimes.indiatimes.com/etstatic/sitemaps/et/news/{year}-{month_name}-1.xml",
        "country": "India",
        "language": "en",
    },
    "the_hindu": {
        "name": "The Hindu",
        "type": "single_sitemap",
        "sitemap_url": "https://www.thehindu.com/sitemap/update/all.xml",
        "country": "India",
        "language": "en",
    },
    "indian_express": {
        "name": "Indian Express",
        "type": "sitemap_index",
        "sitemap_index_url": "https://indianexpress.com/sitemap.xml",
        "country": "India",
        "language": "en",
    },
    "hindustan_times": {
        "name": "Hindustan Times",
        "type": "sitemap_index",
        "sitemap_index_url": "https://www.hindustantimes.com/sitemap/index.xml",
        "country": "India",
        "language": "en",
    },
}


# =====================================================
# Sitemap URL Discoverer
# =====================================================

def _download_xml(url: str):
    """Download and parse an XML sitemap with retry."""
    import requests
    from bs4 import BeautifulSoup

    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "xml")
        except Exception as e:
            if attempt == 2:
                raise e
            logger.warning(f"Retry {attempt+1}/3 for {url}: {e}")
            time.sleep(2)


def _in_date_range(url: str, pub_date: Optional[str], from_date: datetime, to_date: datetime) -> bool:
    """Return True if the URL's publication date falls within [from_date, to_date]."""
    if pub_date:
        try:
            from dateutil import parser as date_parser
            dt = date_parser.parse(pub_date)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return from_date <= dt <= to_date
        except Exception:
            pass
    # Check if a 4-digit year (e.g. 2023, 2025, 2026) exists in the URL
    import re
    years_in_url = [int(y) for y in re.findall(r'\b(20\d{2})\b', url)]
    if years_in_url:
        return any(from_date.year <= y <= to_date.year for y in years_in_url)
    # If no year in URL and no pub_date, accept as candidate
    return True




def _should_skip_url(url: str) -> bool:
    """Skip non-article URLs."""
    url_lower = url.lower()
    return any(kw in url_lower for kw in BOOTSTRAP_SKIP_KEYWORDS)


def collect_urls_for_source(source_key: str, from_date: datetime, to_date: datetime, limit: Optional[int] = None) -> list:
    """
    Discover article URLs for a given source within the date range.
    Returns list of dicts: [{url, published_date, source_name}]
    """
    if source_key not in SOURCE_REGISTRY:
        raise ValueError(f"Unknown source key: '{source_key}'. Valid: {list(SOURCE_REGISTRY.keys())}")

    cfg = SOURCE_REGISTRY[source_key]
    source_name = cfg["name"]
    sitemap_type = cfg["type"]
    discovered = []

    logger.info(f"[{source_name}] Discovering sitemaps ({from_date.date()} → {to_date.date()})...")

    if sitemap_type == "monthly_sitemap":
        # Economic Times: monthly sitemaps
        from dateutil.relativedelta import relativedelta
        MONTH_NAMES = ["January","February","March","April","May","June",
                       "July","August","September","October","November","December"]
        current = from_date.replace(day=1)
        end_month = to_date.replace(day=1)
        while current <= end_month:
            month_name = MONTH_NAMES[current.month - 1]
            sitemap_url = cfg["base_url"].format(year=current.year, month_name=month_name)
            try:
                soup = _download_xml(sitemap_url)
                urls = soup.find_all("url")
                logger.info(f"  Sitemap {sitemap_url}: {len(urls)} URLs found")
                for item in urls:
                    try:
                        url = item.loc.text.strip()
                        pub = item.lastmod.text.strip() if item.lastmod else None
                        if _should_skip_url(url):
                            continue
                        if not _in_date_range(url, pub, from_date, to_date):
                            continue
                        discovered.append({"url": url, "published_date": pub, "source_name": source_name})
                        if limit and len(discovered) >= limit:
                            return discovered
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"  Skipped sitemap {sitemap_url}: {e}")
            current += relativedelta(months=1)

    elif sitemap_type == "single_sitemap":
        # The Hindu: single large sitemap
        try:
            soup = _download_xml(cfg["sitemap_url"])
            urls = soup.find_all("url")
            logger.info(f"  Single sitemap: {len(urls)} URLs found")
            for item in urls:
                try:
                    url = item.loc.text.strip()
                    pub = item.lastmod.text.strip() if item.lastmod else None
                    if _should_skip_url(url):
                        continue
                    if not _in_date_range(url, pub, from_date, to_date):
                        continue
                    discovered.append({"url": url, "published_date": pub, "source_name": source_name})
                    if limit and len(discovered) >= limit:
                        return discovered
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Failed to download sitemap for {source_name}: {e}")

    elif sitemap_type == "sitemap_index":
        # Indian Express / Hindustan Times: index of sitemaps
        try:
            index_soup = _download_xml(cfg["sitemap_index_url"])
            sitemaps = index_soup.find_all("sitemap")
            logger.info(f"  Sitemap index has {len(sitemaps)} sub-sitemaps")
            for sm in sitemaps:
                try:
                    sm_url = sm.loc.text.strip()
                    if _should_skip_url(sm_url):
                        continue
                    # Inspect sub-sitemap if year is in URL or if it's a news/post sitemap
                    year_found = any(str(y) in sm_url for y in range(from_date.year, to_date.year + 1))
                    is_news_sm = any(kw in sm_url.lower() for kw in ["news", "post", "article", "latest", "update"])
                    if not (year_found or is_news_sm):
                        continue

                    sub_soup = _download_xml(sm_url)
                    urls = sub_soup.find_all("url")
                    for item in urls:
                        try:
                            url = item.loc.text.strip()
                            pub = item.lastmod.text.strip() if item.lastmod else None
                            if _should_skip_url(url):
                                continue
                            if not _in_date_range(url, pub, from_date, to_date):
                                continue
                            discovered.append({"url": url, "published_date": pub, "source_name": source_name})
                            if limit and len(discovered) >= limit:
                                return discovered
                        except Exception:
                            continue
                except Exception as e:
                    logger.warning(f"  Skipped sub-sitemap: {e}")
        except Exception as e:
            logger.error(f"Failed to download sitemap index for {source_name}: {e}")

    logger.info(f"[{source_name}] Total URLs discovered in date range: {len(discovered)}")
    return discovered


# =====================================================
# Article Content Extractor
# =====================================================

def extract_article_content(url: str, published_date: Optional[str], source_cfg: dict) -> Optional[dict]:
    """
    Extract full article content from a URL using the 3-method cascade
    (newspaper3k → trafilatura → BS4) from historical_crawlers/extractor.py.
    Returns a raw article dict ready for DQ gate, or None if extraction fails.
    """
    try:
        from historical_crawlers.extractor import extract_article
        result = extract_article(url)
        if not result:
            return None
        return {
            "link": url,
            "title": result.get("title", ""),
            "authors": result.get("authors", ["Unknown"]),
            "content": result.get("content", ""),
            "clean_content": result.get("content", ""),
            "description": result.get("title", ""),
            "published_date": published_date,
            "language": source_cfg.get("language", "en"),
            "source": {
                "name": source_cfg["name"],
                "country": source_cfg.get("country", "India"),
                "language": source_cfg.get("language", "en"),
                "type": "historical_sitemap",
            },
            "extraction_method": result.get("method", "unknown"),
        }
    except Exception as e:
        logger.warning(f"Content extraction failed for {url}: {e}")
        return None


# =====================================================
# Backfill Manager
# =====================================================

class HistoricalBackfillManager:

    def __init__(self, mongo_uri=MONGO_URI, db_name=DATABASE_NAME):
        self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.articles_col = self.db[REALTIME_COLLECTION_NAME]
        self.quarantine_col = self.db[QUARANTINE_COLLECTION_NAME]
        self.state_col = self.db[INGESTION_STATE_COLLECTION_NAME]

    def get_checkpoint(self, batch_id: str) -> dict:
        """Retrieve existing checkpoint for batch ID."""
        doc = self.state_col.find_one({"batch_id": batch_id})
        if doc:
            return doc
        return {
            "batch_id": batch_id,
            "status": "NOT_STARTED",
            "processed_urls": [],
            "stats": {
                "discovered": 0,
                "valid": 0,
                "duplicate": 0,
                "quarantined": 0,
                "extraction_failed": 0,
                "stored": 0,
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

    def save_checkpoint(self, checkpoint: dict):
        """Save updated checkpoint to MongoDB."""
        checkpoint["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.state_col.update_one(
            {"batch_id": checkpoint["batch_id"]},
            {"$set": checkpoint},
            upsert=True
        )

    def check_realtime_backpressure(self, max_pending: int = 50000) -> bool:
        """Check if realtime pipeline is busy; throttle if pending articles > max_pending."""
        try:
            pending_count = self.articles_col.count_documents({"processing.status": "PENDING"})
            if pending_count > max_pending:
                logger.warning(f"[THROTTLE] Realtime pipeline backpressure ({pending_count} pending > limit {max_pending}). Pausing historical backfill...")
                return True
        except Exception as e:
            logger.warning(f"Could not check pipeline backpressure: {e}")
        return False


    def ingest_article(self, raw_article: dict, batch_id: str) -> str:
        """
        Run DQ gate, then insert into MongoDB.
        Returns: 'stored', 'duplicate', or 'quarantined'
        """
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()

        link = raw_article.get("link", "")
        title = raw_article.get("title", "")
        content = raw_article.get("content", "")

        # Generate canonical article_id
        article_id = hashlib.sha256(link.encode("utf-8")).hexdigest()

        # Duplicate check
        existing = self.articles_col.find_one({"$or": [{"article_id": article_id}, {"link": link}]})
        if existing:
            return "duplicate"

        # Data Quality Gate — include article_id so it doesn't fail DQ on that field
        dq_article = {**raw_article, "article_id": article_id}
        dq_result = evaluate_article_quality(dq_article)
        if dq_result.get("quality_status") == "QUARANTINED":
            quarantine_doc = {**raw_article, "article_id": article_id, "data_quality": dq_result,
                             "ingestion_type": "historical", "historical_batch": batch_id,
                             "quarantined_at": now_iso}
            self.quarantine_col.insert_one(quarantine_doc)
            return "quarantined"


        # Build standardized schema document
        source_obj = raw_article.get("source", {})
        if isinstance(source_obj, str):
            source_obj = {"name": source_obj, "country": "India", "language": "en", "type": "historical_sitemap"}

        doc = {
            "article_id": article_id,
            "link": link,
            "source": source_obj,
            "title": title,
            "description": raw_article.get("description", ""),
            "authors": raw_article.get("authors", ["Unknown"]),
            "language": raw_article.get("language", "en"),
            "published_date": raw_article.get("published_date", now_iso),
            "published_datetime": raw_article.get("published_date", now_iso),
            "created_at": now_utc,
            "updated_at": now_utc,
            "fetched_at": now_utc,
            "content": content,
            "clean_content": raw_article.get("clean_content", content),
            "keywords": [],
            "entities": [],
            "sentiment": {},
            "category": {},
            "summary": {"text": "", "model": ""},
            "embedding": [],
            "data_quality": dq_result,
            "ingestion_type": "historical",
            "historical_batch": batch_id,
            "collection_timestamp": now_iso,
            "extraction_method": raw_article.get("extraction_method", ""),
            "processing": {
                "status": "PENDING",
                "stage": "ingested",
                "retry_count": 0
            },
            "status": {
                "ingested": True,
                "content_extracted": bool(content and len(content) > 100),
                "content_cleaned": False,
                "nlp_completed": False
            }
        }

        try:
            self.articles_col.insert_one(doc)
            return "stored"
        except DuplicateKeyError:
            return "duplicate"

    def run_backfill_batch(self, source_key: str, from_date: datetime, to_date: datetime,
                           rate_limit: float = 10.0, batch_size: int = 500,
                           limit: Optional[int] = None) -> dict:
        """
        Full end-to-end historical backfill for a source + date range.
        1. Discover URLs from real sitemaps.
        2. Resume from checkpoint if interrupted.
        3. Extract content for each URL.
        4. Run DQ gate and store in MongoDB.
        5. Print live progress.
        """
        batch_id = f"{source_key}_{from_date.strftime('%Y%m%d')}_to_{to_date.strftime('%Y%m%d')}"
        if limit:
            batch_id = f"{batch_id}_pilot{limit}"

        checkpoint = self.get_checkpoint(batch_id)
        processed_set = set(checkpoint.get("processed_urls", []))
        stats = checkpoint.get("stats", {
            "discovered": 0, "valid": 0, "duplicate": 0,
            "quarantined": 0, "extraction_failed": 0, "stored": 0
        })

        logger.info(f"=== Backfill Batch: {batch_id} ===")
        if processed_set:
            logger.info(f"Resuming from checkpoint: {len(processed_set)} already processed")

        # Step 1: Discover URLs
        if not checkpoint.get("all_urls"):
            logger.info(f"Discovering URLs for {source_key}...")
            url_records = collect_urls_for_source(source_key, from_date, to_date, limit=limit)
            checkpoint["all_urls"] = url_records
            checkpoint["status"] = "URL_DISCOVERY_DONE"
            self.save_checkpoint(checkpoint)
        else:
            url_records = checkpoint["all_urls"]
            logger.info(f"Using cached URL list from checkpoint: {len(url_records)} URLs")

        stats["discovered"] = len(url_records)

        if not url_records:
            logger.warning(f"No URLs discovered for {source_key} in date range. Check sitemap access.")
            return stats

        source_cfg = SOURCE_REGISTRY.get(source_key, {})
        delay = 1.0 / max(rate_limit, 0.5)
        total = len(url_records)
        remaining = [r for r in url_records if r["url"] not in processed_set]

        logger.info(f"Total URLs: {total} | Remaining to process: {len(remaining)}")
        logger.info(f"Rate limit: {rate_limit}/s | Delay: {delay:.2f}s per article")

        for idx, record in enumerate(remaining):
            url = record["url"]
            published_date = record.get("published_date")

            # Throttle if realtime pipeline is backed up (threshold raised to 50000 to prevent blocking historical ingest)
            while self.check_realtime_backpressure(max_pending=50000):
                time.sleep(5)


            # Extract content
            raw_article = extract_article_content(url, published_date, source_cfg)

            if raw_article is None:
                stats["extraction_failed"] = stats.get("extraction_failed", 0) + 1
                processed_set.add(url)
            else:
                outcome = self.ingest_article(raw_article, batch_id)
                processed_set.add(url)

                if outcome == "stored":
                    stats["stored"] += 1
                    stats["valid"] += 1
                elif outcome == "duplicate":
                    stats["duplicate"] += 1
                elif outcome == "quarantined":
                    stats["quarantined"] += 1

            # Checkpoint every 25 items
            if (idx + 1) % 25 == 0 or idx == len(remaining) - 1:
                checkpoint["processed_urls"] = list(processed_set)
                checkpoint["stats"] = stats
                checkpoint["status"] = "COMPLETED" if idx == len(remaining) - 1 else "IN_PROGRESS"
                self.save_checkpoint(checkpoint)

                done = len(processed_set)
                pct = (done / total) * 100.0 if total else 100.0
                remaining_count = total - done
                logger.info(
                    f"Progress [{batch_id}]: {done}/{total} ({pct:.1f}%) | "
                    f"Stored: {stats['stored']} | Dupes: {stats['duplicate']} | "
                    f"Quarantined: {stats['quarantined']} | Failed Extract: {stats.get('extraction_failed', 0)} | "
                    f"Remaining: {remaining_count}"
                )

            time.sleep(delay)

        checkpoint["status"] = "COMPLETED"
        self.save_checkpoint(checkpoint)

        _print_final_report(batch_id, stats, total)
        return stats


def _print_final_report(batch_id: str, stats: dict, total: int):
    """Print final backfill report."""
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"HISTORICAL BACKFILL COMPLETED: {batch_id}")
    print(sep)
    print(f"  Total Discovered     : {stats['discovered']}")
    print(f"  Stored (Valid)       : {stats['stored']}")
    print(f"  Duplicates Skipped   : {stats['duplicate']}")
    print(f"  Quarantined (DQ Fail): {stats['quarantined']}")
    print(f"  Extraction Failed    : {stats.get('extraction_failed', 0)}")
    if stats['discovered'] > 0:
        pct = (stats['stored'] / stats['discovered']) * 100
        print(f"  Success Rate         : {pct:.1f}%")
    print(sep)


# =====================================================
# CLI Entry Point
# =====================================================

def main():
    parser = argparse.ArgumentParser(description="Historical News Backfill Controller")
    parser.add_argument("--source", type=str, required=True,
                        help=f"News source key. Valid: {list(SOURCE_REGISTRY.keys())} or 'all'")
    parser.add_argument("--from", type=str, dest="from_date", default="2025-08-01",
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", type=str, dest="to_date",
                        default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("--rate-limit", type=float, default=1.0,
                        help="Max articles extracted per second (default: 1.0 to be polite)")
    parser.add_argument("--batch-size", type=int, default=500,
                        help="Batch size per checkpoint cycle")
    parser.add_argument("--limit", type=int, default=None,
                        help="Hard limit on URLs to process (for pilot runs)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from existing checkpoint (default behavior)")

    args = parser.parse_args()

    try:
        from_date = datetime.strptime(args.from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        to_date = datetime.strptime(args.to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        sys.exit(1)

    manager = HistoricalBackfillManager()

    sources = list(SOURCE_REGISTRY.keys()) if args.source == "all" else [args.source]
    for source_key in sources:
        if source_key not in SOURCE_REGISTRY:
            logger.error(f"Unknown source: '{source_key}'. Valid sources: {list(SOURCE_REGISTRY.keys())}")
            sys.exit(1)
        manager.run_backfill_batch(
            source_key=source_key,
            from_date=from_date,
            to_date=to_date,
            rate_limit=args.rate_limit,
            batch_size=args.batch_size,
            limit=args.limit,
        )


if __name__ == "__main__":
    main()
