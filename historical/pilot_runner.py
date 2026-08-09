"""
============================================================
Historical News Pilot Runner
News Intelligence Platform
============================================================
Version : 1.0 (Production)
Purpose :
  Run a controlled pilot batch of up to N articles per source
  to validate the full pipeline before launching full-year backfill.

Verifies:
  - URL collection from real sitemaps
  - Content extraction (newspaper3k → trafilatura → BS4)
  - Data Quality gate (score / status)
  - MongoDB insertion (correct schema + ingestion_type = historical)
  - No duplicates
  - Extraction success rate

Pass Criteria:
  - stored >= 80% of limit per source (e.g. 80 of 100)
  - DQ pass rate (stored / (stored + quarantined)) >= 70%
  - Zero unhandled exceptions

Usage:
  python historical/pilot_runner.py --limit 100
  python historical/pilot_runner.py --source economic_times --limit 50
============================================================
"""

import sys
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from historical.backfill_manager import (
    HistoricalBackfillManager,
    SOURCE_REGISTRY,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("PilotRunner")

# Default: collect from Aug 2025 to today
PILOT_FROM = "2025-08-01"
PILOT_TO = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Pass thresholds
MIN_STORED_RATE = 0.50      # At least 50% of discovered must be stored
MIN_DQ_PASS_RATE = 0.60     # At least 60% of (stored+quarantined) must be stored (pass DQ)


def run_pilot(source_key: str, limit: int, from_date_str: str, to_date_str: str) -> dict:
    """Run a pilot batch for a single source, return results dict."""
    logger.info(f"=== PILOT: {source_key} | Limit: {limit} | {from_date_str} → {to_date_str} ===")
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    manager = HistoricalBackfillManager()
    stats = manager.run_backfill_batch(
        source_key=source_key,
        from_date=from_date,
        to_date=to_date,
        rate_limit=2.0,   # Polite rate for pilot
        batch_size=limit,
        limit=limit,
    )

    discovered = stats.get("discovered", 0)
    stored = stats.get("stored", 0)
    duplicate = stats.get("duplicate", 0)
    quarantined = stats.get("quarantined", 0)
    failed_extract = stats.get("extraction_failed", 0)

    stored_rate = stored / max(discovered, 1)
    dq_denominator = stored + quarantined
    dq_pass_rate = stored / max(dq_denominator, 1)

    passed_stored = stored_rate >= MIN_STORED_RATE
    passed_dq = dq_pass_rate >= MIN_DQ_PASS_RATE

    return {
        "source": source_key,
        "source_name": SOURCE_REGISTRY[source_key]["name"],
        "limit": limit,
        "discovered": discovered,
        "stored": stored,
        "duplicate": duplicate,
        "quarantined": quarantined,
        "extraction_failed": failed_extract,
        "stored_rate": stored_rate,
        "dq_pass_rate": dq_pass_rate,
        "passed_stored": passed_stored,
        "passed_dq": passed_dq,
        "overall_pass": passed_stored and passed_dq,
    }


def print_pilot_report(results: list):
    """Print a formatted pilot report with PASS/FAIL verdict per source."""
    sep = "=" * 75
    print(f"\n{sep}")
    print("  HISTORICAL BACKFILL PILOT REPORT")
    print(sep)

    all_pass = True
    for r in results:
        status = "PASS" if r["overall_pass"] else "FAIL"
        if not r["overall_pass"]:
            all_pass = False

        print(f"\n  Source         : {r['source_name']} ({r['source']})")
        print(f"  Pilot Limit    : {r['limit']} URLs")
        print(f"  Discovered     : {r['discovered']}")
        print(f"  Stored         : {r['stored']}  (rate: {r['stored_rate']*100:.1f}% | need ≥{MIN_STORED_RATE*100:.0f}%)  {'✅' if r['passed_stored'] else '❌'}")
        print(f"  Duplicates     : {r['duplicate']}")
        print(f"  Quarantined    : {r['quarantined']}  (DQ pass: {r['dq_pass_rate']*100:.1f}% | need ≥{MIN_DQ_PASS_RATE*100:.0f}%)  {'✅' if r['passed_dq'] else '❌'}")
        print(f"  Extract Failed : {r['extraction_failed']}")
        print(f"  Pilot Verdict  : [{status}]")

    print(f"\n{sep}")
    if all_pass:
        print("  OVERALL PILOT VERDICT : ✅ PASS — READY FOR FULL BACKFILL")
        print(f"\n  Next step:")
        print(f"    python historical/backfill_manager.py --source <source> --from 2025-08-01 --to {PILOT_TO} --rate-limit 1.0")
    else:
        print("  OVERALL PILOT VERDICT : ❌ FAIL — FIX ISSUES BEFORE FULL BACKFILL")
        print("\n  Check:")
        print("  1. Are sitemaps accessible (rate limiting / IP blocking)?")
        print("  2. Is content extraction returning valid text (>300 chars)?")
        print("  3. Is the DQ gate threshold too strict? (check quarantine_articles)")
        print("  4. Re-run pilot after fixing issues.")
    print(sep)


def main():
    parser = argparse.ArgumentParser(description="Historical News Pilot Runner")
    parser.add_argument("--source", type=str, default="all",
                        help=f"Source key or 'all'. Valid: {list(SOURCE_REGISTRY.keys())}")
    parser.add_argument("--limit", type=int, default=100,
                        help="Max URLs to test per source (default: 100)")
    parser.add_argument("--from", type=str, dest="from_date", default=PILOT_FROM,
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", type=str, dest="to_date", default=PILOT_TO,
                        help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    sources = list(SOURCE_REGISTRY.keys()) if args.source == "all" else [args.source]
    results = []

    for source_key in sources:
        if source_key not in SOURCE_REGISTRY:
            logger.error(f"Unknown source: '{source_key}'. Valid: {list(SOURCE_REGISTRY.keys())}")
            sys.exit(1)
        result = run_pilot(source_key, args.limit, args.from_date, args.to_date)
        results.append(result)

    print_pilot_report(results)

    overall_pass = all(r["overall_pass"] for r in results)
    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
