

"""
Economic Times Bootstrap Collector

Downloads monthly Economic Times sitemap files,
filters articles by bootstrap date range,
and returns standardized article documents.
"""

import logging
import time


from bootstrap.common_collector import (
    collect_articles,
    filter_articles_by_date
)

from bootstrap.config import (
    BOOTSTRAP_START_DATE,
    BOOTSTRAP_END_DATE,
    LOG_SEPARATOR
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(

    "ET_Collector"

)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "Economic Times"

BASE_URL = (

    "https://economictimes.indiatimes.com/"

    "etstatic/sitemaps/et/news/"

)

COLLECTOR_VERSION = "1.0.0"

# =====================================================
# Generate Bootstrap Sitemap URLs
# =====================================================

def generate_sitemap_urls():

    """
    Generate monthly sitemap URLs
    between bootstrap start and end dates.
    """

    sitemap_urls = []

    current = BOOTSTRAP_START_DATE.replace(

        day=1

    )

    end_month = BOOTSTRAP_END_DATE.replace(

        day=1

    )

    while current <= end_month:

        month_name = current.strftime(

            "%B"

        )

        sitemap_urls.append(

            f"{BASE_URL}"

            f"{current.year}-"

            f"{month_name}-1.xml"

        )

        # ----------------------------------------
        # Next Month
        # ----------------------------------------

        if current.month == 12:

            current = current.replace(

                year=current.year + 1,

                month=1

            )

        else:

            current = current.replace(

                month=current.month + 1

            )

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Generated {len(sitemap_urls)} sitemap URLs"

    )

    logger.info(LOG_SEPARATOR)

    return sitemap_urls
# =====================================================
# Collect Economic Times Articles
# =====================================================

def collect_et_articles():

    """
    Bootstrap Economic Times articles.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(f"{SOURCE_NAME} Bootstrap Collection Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    sitemap_urls = generate_sitemap_urls()

    all_articles = []

    total_processed = 0

    total_filtered = 0

    total_failed_sitemaps = 0

    # =================================================
    # Process Every Sitemap
    # =================================================

    for index, sitemap_url in enumerate(

        sitemap_urls,

        start=1

    ):

        logger.info(LOG_SEPARATOR)

        logger.info(

            f"Sitemap {index}/{len(sitemap_urls)}"

        )

        logger.info(

            sitemap_url

        )

        logger.info(LOG_SEPARATOR)

        try:

            # ----------------------------------------
            # Collect Articles
            # ----------------------------------------

            articles = collect_articles(

                sitemap_url,

                SOURCE_NAME

            )

            total_processed += len(

                articles

            )

            # ----------------------------------------
            # Filter Bootstrap Range
            # ----------------------------------------

            filtered_articles = filter_articles_by_date(

                articles,

                BOOTSTRAP_START_DATE,

                BOOTSTRAP_END_DATE,

            )
            total_filtered += len(

                filtered_articles

            )

            all_articles.extend(

                filtered_articles

            )

            logger.info(

                f"Collected : {len(articles)}"

            )

            logger.info(

                f"Filtered  : {len(filtered_articles)}"

            )

        except Exception:

            total_failed_sitemaps += 1

            logger.exception(

                f"Failed Sitemap : {sitemap_url}"

            )

    # =================================================
    # Summary
    # =================================================

    duration = round(

        time.perf_counter()

        - started,

        3

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        "Economic Times Bootstrap Summary"

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Source              : {SOURCE_NAME}"

    )

    logger.info(

        f"Sitemaps            : {len(sitemap_urls)}"

    )

    logger.info(

        f"Collected           : {total_processed}"

    )

    logger.info(

        f"Bootstrap Articles  : {total_filtered}"

    )

    logger.info(

        f"Failed Sitemaps     : {total_failed_sitemaps}"

    )

    logger.info(

        f"Processing Time     : {duration:.2f} sec"

    )

    logger.info(LOG_SEPARATOR)

   

    return all_articles
# =====================================================
# Main
# =====================================================

def main():

    logger.info(LOG_SEPARATOR)

    logger.info("Economic Times Bootstrap Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    try:

        # ----------------------------------------
        # Collect Articles
        # ----------------------------------------

        articles = collect_et_articles()

        duration = round(

            time.perf_counter()

            - started,

            3

        )

        logger.info(LOG_SEPARATOR)

        logger.info("Economic Times Bootstrap Completed")

        logger.info(LOG_SEPARATOR)

        logger.info(

            f"Source              : {SOURCE_NAME}"

        )

        logger.info(

            f"Collected Articles  : {len(articles)}"

        )

        logger.info(

            f"Collector Version   : {COLLECTOR_VERSION}"

        )

        logger.info(

            f"Execution Time      : {duration:.2f} sec"

        )

        logger.info(LOG_SEPARATOR)

    except KeyboardInterrupt:

        logger.warning("=" * 70)

        logger.warning(

            "Bootstrap Interrupted By User"

        )

        logger.warning("=" * 70)

    except Exception:

        logger.exception(

            "Bootstrap Failed"

        )

        raise


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":

    main()
