

"""
Indian Express Bootstrap Collector

Downloads Indian Express sitemap index,
filters valid sitemap files,
collects bootstrap articles,
and returns standardized MongoDB documents.
"""

import logging
import time
from datetime import datetime

from bootstrap.common_collector import (
    collect_articles,
    filter_articles_by_date,
    download_xml,
    print_summary,
)
from bootstrap.config import (

    BOOTSTRAP_START_DATE,

    BOOTSTRAP_END_DATE,

    LOG_SEPARATOR,

)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(

    "IndianExpress_Collector"

)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "Indian Express"

SITEMAP_INDEX_URL = (

    "https://indianexpress.com/sitemap.xml"

)

HISTORICAL_YEARS = 3

COLLECTOR_VERSION = "1.0.0"

SKIP_KEYWORDS = {

    "liveblog",

    "video",

    "photos",

    "today",

    "yesterday",

    "category",

    "news-sitemap",

    "webstories",

    "horoscope",

    "aboutsitemap",

    "section"

}

logger.info(LOG_SEPARATOR)

logger.info(f"{SOURCE_NAME} Collector Initialized")

logger.info(f"Sitemap Index : {SITEMAP_INDEX_URL}")

logger.info(LOG_SEPARATOR)

# =====================================================
# Validate Sitemap
# =====================================================

def is_valid_sitemap(

    sitemap_url

):

    """
    Validate Indian Express sitemap.
    """

    if not sitemap_url:

        return False

    url = sitemap_url.lower()

    # ----------------------------------------
    # Skip Unwanted Sitemap
    # ----------------------------------------

    if any(

        keyword in url

        for keyword in SKIP_KEYWORDS

    ):

        return False

    # ----------------------------------------
    # Historical Years
    # ----------------------------------------

    current_year = datetime.now().year

    cutoff_year = (

        current_year

        - HISTORICAL_YEARS

    )

    valid = any(

        str(year) in url

        for year in range(

            cutoff_year,

            current_year + 1

        )

    )

    if not valid:

        logger.debug(

            f"Ignored Sitemap : {url}"

        )

    return valid
# =====================================================
# Collect Indian Express Articles
# =====================================================

def collect_indianexpress_articles():

    """
    Bootstrap Indian Express articles.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(f"{SOURCE_NAME} Bootstrap Collection Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    all_articles = []

    total_processed = 0

    total_filtered = 0

    total_failed_sitemaps = 0

    # =================================================
    # Download Sitemap Index
    # =================================================

    sitemap_index = download_xml(

        SITEMAP_INDEX_URL

    )

    sitemaps = sitemap_index.find_all(

        "sitemap"

    )

    logger.info(

        f"Total Sitemap Files : {len(sitemaps)}"

    )

    valid_sitemap_count = 0

    # =================================================
    # Process Every Sitemap
    # =================================================

    for sitemap in sitemaps:

        try:

            sitemap_url = sitemap.loc.text.strip()

            # ----------------------------------------
            # Validate Sitemap
            # ----------------------------------------

            if not is_valid_sitemap(

                sitemap_url

            ):

                continue

            valid_sitemap_count += 1

            logger.info(LOG_SEPARATOR)

            logger.info(

                f"Sitemap {valid_sitemap_count}"

            )

            logger.info(

                sitemap_url

            )

            logger.info(LOG_SEPARATOR)

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
            # Filter Bootstrap Articles
            # ----------------------------------------

            filtered_articles = filter_articles_by_date(
            articles,
            BOOTSTRAP_START_DATE,
            BOOTSTRAP_END_DATE
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

        "Indian Express Bootstrap Summary"

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Source              : {SOURCE_NAME}"

    )

    logger.info(

        f"Valid Sitemaps      : {valid_sitemap_count}"

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

    print_summary(

        SOURCE_NAME,

        total_filtered,

        total_failed_sitemaps

    )

    return all_articles
# =====================================================
# Main
# =====================================================

def main():

    logger.info(LOG_SEPARATOR)

    logger.info("Indian Express Bootstrap Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    try:

        # ----------------------------------------
        # Collect Articles
        # ----------------------------------------

        articles = collect_indianexpress_articles()

        duration = round(

            time.perf_counter()

            - started,

            3

        )

        logger.info(LOG_SEPARATOR)

        logger.info("Indian Express Bootstrap Completed")

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

        logger.warning(LOG_SEPARATOR)

        logger.warning(

            "Bootstrap Interrupted By User"

        )

        logger.warning(LOG_SEPARATOR)

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
