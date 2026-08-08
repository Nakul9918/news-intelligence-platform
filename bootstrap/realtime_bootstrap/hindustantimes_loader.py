"""
Hindustan Times Realtime Bootstrap Loader

Collects Hindustan Times articles for Aug 1-7, 2026.
"""

import logging
import time

from bootstrap.common_collector import (
    collect_articles,
    filter_articles_by_date,
)

from bootstrap.realtime_bootstrap.config import (
    START_DATE,
    END_DATE,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(
    "Realtime_HindustanTimes_Loader"
)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "Hindustan Times"

SITEMAP_URL = (
    "https://www.hindustantimes.com/sitemap/august-2026.xml"
)

# =====================================================
# Collect Articles
# =====================================================

def collect_august_articles():

    logger.info("=" * 70)
    logger.info("Hindustan Times Aug 1-7 Collection")
    logger.info("=" * 70)

    started = time.perf_counter()

    try:

        # ---------------------------------------------
        # Collect from August sitemap
        # ---------------------------------------------

        articles = collect_articles(
            SITEMAP_URL,
            SOURCE_NAME
        )

        logger.info(
            f"Collected from sitemap: {len(articles)}"
        )

        # ---------------------------------------------
        # Filter Aug 1-7
        # ---------------------------------------------

        filtered_articles = filter_articles_by_date(
            articles,
            START_DATE,
            END_DATE
        )

        logger.info(
            f"Aug 1-7 articles: {len(filtered_articles)}"
        )

        # ---------------------------------------------
        # Summary
        # ---------------------------------------------

        duration = round(
            time.perf_counter() - started,
            3
        )

        logger.info("=" * 70)
        logger.info(
            "HINDUSTAN TIMES COLLECTION COMPLETE"
        )
        logger.info(
            f"Total Aug 1-7 articles: "
            f"{len(filtered_articles)}"
        )
        logger.info(
            f"Time: {duration:.2f} sec"
        )
        logger.info("=" * 70)

        return filtered_articles

    except Exception:

        logger.exception(
            "Hindustan Times collection failed"
        )

        return []


# =====================================================
# Main
# =====================================================

def main():

    articles = collect_august_articles()

    print(
        f"\n# Articles: {len(articles)}"
    )


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":

    main()