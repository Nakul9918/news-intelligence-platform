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

logger = logging.getLogger("Realtime_ET_Loader")


# ==========================================================
# Economic Times
# ==========================================================

SOURCE_NAME = "Economic Times"

BASE_URL = (
    "https://economictimes.indiatimes.com/"
    "etstatic/sitemaps/et/news/"
)


# ==========================================================
# Generate Monthly Sitemap URLs
# ==========================================================

def generate_sitemap_urls():

    urls = []

    current = START_DATE.replace(day=1)
    end_month = END_DATE.replace(day=1)

    while current <= end_month:

        month_name = current.strftime("%B")

        url = (
            f"{BASE_URL}"
            f"{current.year}-"
            f"{month_name}-1.xml"
        )

        urls.append(url)

        if current.month == 12:

            current = current.replace(
                year=current.year + 1,
                month=1
            )

        else:

            current = current.replace(
                month=current.month + 1
            )

    return urls


# ==========================================================
# Collect Aug 1–7 Articles
# ==========================================================

def collect_august_articles():

    logger.info("=" * 70)
    logger.info("Economic Times Aug 1–7 Collection")
    logger.info("=" * 70)

    started = time.perf_counter()

    sitemap_urls = generate_sitemap_urls()

    all_articles = []

    for sitemap_url in sitemap_urls:

        logger.info("-" * 70)
        logger.info(f"Sitemap: {sitemap_url}")

        try:

            articles = collect_articles(
                sitemap_url,
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

            all_articles.extend(filtered)

        except Exception:

            logger.exception(
                f"Failed sitemap: {sitemap_url}"
            )

    duration = time.perf_counter() - started

    logger.info("=" * 70)
    logger.info("ET COLLECTION COMPLETE")
    logger.info(f"Total Aug 1–7 articles: {len(all_articles)}")
    logger.info(f"Time: {duration:.2f} sec")
    logger.info("=" * 70)

    return all_articles


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    articles = collect_august_articles()

    print()
    print("=" * 70)
    print("FINAL ET RESULT")
    print("=" * 70)
    print("Articles:", len(articles))
    print("=" * 70)