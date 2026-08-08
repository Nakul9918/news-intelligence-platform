import logging
import time

from bootstrap.common_collector import (
    collect_articles,
    filter_articles_by_date
)

from bootstrap.realtime_bootstrap.config import (
    START_DATE,
    END_DATE
)

# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("Realtime_TheHindu_Loader")


# ==========================================================
# The Hindu
# ==========================================================

SOURCE_NAME = "The Hindu"

SITEMAP_URL = (
    "https://www.thehindu.com/sitemap/googlenews/all/all.xml"
)


# ==========================================================
# Collect Aug 1–7 Articles
# ==========================================================

def collect_august_articles():

    logger.info("=" * 70)
    logger.info("The Hindu Aug 1–7 Collection")
    logger.info("=" * 70)

    started = time.perf_counter()

    try:

        articles = collect_articles(
            SITEMAP_URL,
            SOURCE_NAME
        )

        logger.info(
            f"Collected from sitemap: {len(articles)}"
        )

        filtered = filter_articles_by_date(
            articles,
            START_DATE,
            END_DATE
        )

        logger.info(
            f"Aug 1–7 articles: {len(filtered)}"
        )

    except Exception:

        logger.exception(
            "The Hindu collection failed"
        )

        filtered = []

    duration = time.perf_counter() - started

    logger.info("=" * 70)
    logger.info("THE HINDU COLLECTION COMPLETE")
    logger.info(f"Total Aug 1–7 articles: {len(filtered)}")
    logger.info(f"Time: {duration:.2f} sec")
    logger.info("=" * 70)

    return filtered


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    articles = collect_august_articles()

    print()
    print("=" * 70)
    print("FINAL THE HINDU RESULT")
    print("=" * 70)
    print("Articles:", len(articles))
    print("=" * 70)