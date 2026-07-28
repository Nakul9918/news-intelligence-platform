from datetime import datetime
from dateutil.relativedelta import relativedelta

from historical_crawlers.common_collector import (
    get_collection,
    download_xml,
    store_urls,
    print_summary
)

from config import SKIP_KEYWORDS

# =====================================================
# MongoDB Collection
# =====================================================

COLLECTION_NAME = "historical_urls_hindustantimes"

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "Hindustan Times"

SITEMAP_INDEX_URL = "https://www.hindustantimes.com/sitemap/index.xml"

HISTORICAL_YEARS = 3

# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    collection = get_collection(COLLECTION_NAME)

    sitemap_index = download_xml(SITEMAP_INDEX_URL)

    sitemaps = sitemap_index.find_all("sitemap")

    print(f"Total Sitemap Files : {len(sitemaps)}")

    cutoff_year = datetime.now().year - HISTORICAL_YEARS

    total_processed = 0
    total_failed = 0

    for sitemap in sitemaps:

        sitemap_url = sitemap.loc.text.strip()

        # Skip unwanted sitemap types
        if any(keyword in sitemap_url.lower() for keyword in SKIP_KEYWORDS):
            continue

        # Skip old years
        year_found = False

        for year in range(cutoff_year, datetime.now().year + 1):

            if str(year) in sitemap_url:
                year_found = True
                break

        if not year_found:
            continue

        print("\nProcessing")
        print(sitemap_url)

        try:

            xml = download_xml(sitemap_url)

            urls = xml.find_all("url")

            print(f"Articles Found : {len(urls)}")

            processed, failed = store_urls(
                urls,
                collection,
                SOURCE_NAME
            )

            total_processed += processed
            total_failed += failed

        except Exception as e:

            print(f"Error : {e}")

    print_summary(
        SOURCE_NAME,
        total_processed,
        total_failed
    )


if __name__ == "__main__":
    main()