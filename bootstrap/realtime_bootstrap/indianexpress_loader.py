import logging
import time

import requests
from bs4 import BeautifulSoup

from bootstrap.common_collector import (
    collect_articles,
    filter_articles_by_date,
)

from bootstrap.realtime_bootstrap.config import (
    START_DATE,
    END_DATE,
)


# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(
    "Realtime_IndianExpress_Loader"
)


# ==========================================================
# Configuration
# ==========================================================

SOURCE_NAME = "Indian Express"

BASE_SITEMAP_URL = (
    "https://indianexpress.com/"
    "sitemap.xml?yyyy=2026&mm=08&dd={:02d}"
)


# ==========================================================
# Get Aug 1–7 Sitemap URLs
# ==========================================================

def get_august_sitemaps():

    return [
        BASE_SITEMAP_URL.format(day)
        for day in range(1, 8)
    ]


# ==========================================================
# Download Daily Sitemap
# ==========================================================

def download_daily_sitemap(url):

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.content,
        "xml"
    )


# ==========================================================
# Collect Aug 1–7 Articles
# ==========================================================

def collect_august_articles():

    logger.info("=" * 70)
    logger.info(
        "Indian Express Aug 1–7 Collection"
    )
    logger.info("=" * 70)

    started = time.perf_counter()

    all_articles = []

    sitemap_urls = get_august_sitemaps()

    for day, sitemap_url in enumerate(
        sitemap_urls,
        start=1
    ):

        logger.info("-" * 70)
        logger.info(
            f"Processing Aug {day} Sitemap"
        )
        logger.info(
            sitemap_url
        )
        logger.info("-" * 70)

        try:

            soup = download_daily_sitemap(
                sitemap_url
            )

            url_count = len(
                soup.find_all("url")
            )

            logger.info(
                f"URLs in sitemap: {url_count}"
            )

            # ------------------------------------------------
            # Use the existing common collector logic
            # ------------------------------------------------

            articles = collect_articles(
                sitemap_url,
                SOURCE_NAME
            )

            logger.info(
                f"Collected: {len(articles)}"
            )

            filtered = filter_articles_by_date(
                articles,
                START_DATE,
                END_DATE
            )

            logger.info(
                f"Aug 1–7 filtered: {len(filtered)}"
            )

            all_articles.extend(
                filtered
            )

        except Exception:

            logger.exception(
                f"Failed Aug {day} sitemap"
            )

    duration = (
        time.perf_counter()
        - started
    )

    logger.info("=" * 70)
    logger.info(
        "INDIAN EXPRESS COLLECTION COMPLETE"
    )
    logger.info("=" * 70)

    logger.info(
        f"Total Aug 1–7 articles: "
        f"{len(all_articles)}"
    )

    logger.info(
        f"Time: {duration:.2f} sec"
    )

    logger.info("=" * 70)

    return all_articles


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    articles = collect_august_articles()

    print()
    print("=" * 70)
    print("FINAL INDIAN EXPRESS RESULT")
    print("=" * 70)
    print(
        "Articles:",
        len(articles)
    )
    print("=" * 70)