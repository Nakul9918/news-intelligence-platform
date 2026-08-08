


"""
The Hindu Bootstrap Collector

Downloads The Hindu sitemap,
filters bootstrap articles,
and returns standardized MongoDB documents.
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

    "TheHindu_Collector"

)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "The Hindu"

SITEMAP_URL = (

    "https://www.thehindu.com/sitemap/update/all.xml"

)

COLLECTOR_VERSION = "1.0.0"

logger.info(LOG_SEPARATOR)

logger.info(f"{SOURCE_NAME} Collector Initialized")

logger.info(f"Sitemap : {SITEMAP_URL}")

logger.info(LOG_SEPARATOR)
filtered_articles = filter_articles_by_date(
    articles,

    BOOTSTRAP_START_DATE,
    
    BOOTSTRAP_END_DATE,
)
# =====================================================
# Collect The Hindu Articles
# =====================================================

def collect_thehindu_articles():

    """
    Bootstrap The Hindu articles.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(f"{SOURCE_NAME} Bootstrap Collection Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    all_articles = []

    total_processed = 0

    total_filtered = 0

    total_failed = 0

    try:

        # ----------------------------------------
        # Collect Articles
        # ----------------------------------------

        articles = collect_articles(

            SITEMAP_URL,

            SOURCE_NAME

        )

        total_processed = len(

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

        total_filtered = len(

            filtered_articles

        )

        all_articles.extend(

            filtered_articles

        )

        logger.info(

            f"Collected : {total_processed}"

        )

        logger.info(

            f"Filtered  : {total_filtered}"

        )

    except Exception:

        total_failed += 1

        logger.exception(

            "The Hindu Collection Failed"

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

        "The Hindu Bootstrap Summary"

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Source              : {SOURCE_NAME}"

    )

    logger.info(

        f"Collected           : {total_processed}"

    )

    logger.info(

        f"Bootstrap Articles  : {total_filtered}"

    )

    logger.info(

        f"Failed Collections  : {total_failed}"

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

    logger.info("The Hindu Bootstrap Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    try:

        # ----------------------------------------
        # Collect Articles
        # ----------------------------------------

        articles = collect_thehindu_articles()

        duration = round(

            time.perf_counter()

            - started,

            3

        )

        logger.info(LOG_SEPARATOR)

        logger.info("The Hindu Bootstrap Completed")

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