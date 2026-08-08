

"""
Hindustan Times Bootstrap Collector
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import time

# =====================================================
# Common Collector
# =====================================================

from bootstrap.common_collector import (
    download_xml,
    collect_articles,
    filter_articles_by_date,
)

# =====================================================
# Bootstrap Configuration
# =====================================================

from bootstrap.config import (
    BOOTSTRAP_START_DATE,
    BOOTSTRAP_END_DATE,
    LOG_SEPARATOR,
    SMALL_SEPARATOR,
)

# =====================================================
# Logging
# =====================================================

logger = logging.getLogger(
    "HindustanTimesCollector"
)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "Hindustan Times"

SITEMAP_INDEX_URL = (
    "https://www.hindustantimes.com/sitemap/index.xml"
)

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

    "section",

}

# =====================================================
# Validate Sitemap
# =====================================================

def is_valid_sitemap(
    sitemap_url
):
    """
    Validate Hindustan Times sitemap.
    """

    if not sitemap_url:

        return False

    url = sitemap_url.lower()

    for keyword in SKIP_KEYWORDS:

        if keyword in url:

            logger.debug(
                f"Skipped Sitemap : {url}"
            )

            return False

    return True

# =====================================================
# Collect Hindustan Times Articles
# =====================================================

def collect_hindustantimes_articles():
    """
    Bootstrap Hindustan Times articles.

    Returns
    -------
    list
        Filtered bootstrap articles.
    """

    logger.info(LOG_SEPARATOR)
    logger.info(f"{SOURCE_NAME} Bootstrap Collection Started")
    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    all_articles = []

    total_collected = 0

    total_filtered = 0

    total_failed_sitemaps = 0

    valid_sitemap_count = 0

    # =================================================
    # Download Sitemap Index
    # =================================================

    sitemap_index = download_xml(
        SITEMAP_INDEX_URL
    )

    if sitemap_index is None:

        logger.error(
            "Unable to download sitemap index."
        )

        return []

    sitemaps = sitemap_index.find_all(
        "sitemap"
    )

    logger.info(
        f"Total Sitemap Files : {len(sitemaps)}"
    )

    # =================================================
    # Process Every Sitemap
    # =================================================

    for sitemap in sitemaps:

        sitemap_url = None

        try:

            loc = sitemap.find("loc")

            if loc is None:

                continue

            sitemap_url = loc.text.strip()

            # ------------------------------------------
            # Validate Sitemap
            # ------------------------------------------

            if not is_valid_sitemap(
                sitemap_url
            ):

                continue

            valid_sitemap_count += 1

            logger.info(SMALL_SEPARATOR)

            logger.info(
                f"Sitemap {valid_sitemap_count}"
            )

            logger.info(
                sitemap_url
            )

            logger.info(SMALL_SEPARATOR)

            # ------------------------------------------
            # Collect Articles
            # ------------------------------------------

            articles = collect_articles(

                sitemap_url,

                SOURCE_NAME,

            )

            total_collected += len(
                articles
            )

            # ------------------------------------------
            # Filter Bootstrap Date Range
            # ------------------------------------------

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

        time.perf_counter() - started,

        3

    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"{SOURCE_NAME} Bootstrap Summary"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Valid Sitemaps      : {valid_sitemap_count}"
    )

    logger.info(
        f"Collected Articles  : {total_collected}"
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
    """
    Run Hindustan Times bootstrap collector.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"{SOURCE_NAME} Bootstrap Started"
    )

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    try:

        articles = collect_hindustantimes_articles()

        duration = round(

            time.perf_counter() - started,

            3

        )

        logger.info(LOG_SEPARATOR)

        logger.info(
            "Bootstrap Completed Successfully"
        )

        logger.info(LOG_SEPARATOR)

        logger.info(
            f"Collected Articles : {len(articles)}"
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

    finally:

        logger.info(LOG_SEPARATOR)

        logger.info(
            "Hindustan Times Collector Finished"
        )

        logger.info(LOG_SEPARATOR)


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":

    main()