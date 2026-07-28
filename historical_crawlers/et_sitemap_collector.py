from datetime import datetime
from dateutil.relativedelta import relativedelta

from historical_crawlers.common_collector import (
    get_collection,
    download_xml,
    store_urls,
    print_summary
)

# =====================================================
# Configuration
# =====================================================

COLLECTION_NAME = "historical_urls_et"

SOURCE_NAME = "Economic Times"

BASE_URL = (
    "https://economictimes.indiatimes.com/"
    "etstatic/sitemaps/et/news/"
)

# =====================================================
# Generate Last 3 Years Monthly Sitemaps
# =====================================================

def generate_sitemap_urls(years=3):

    sitemap_urls = []

    current = datetime.now().replace(day=1)
    cutoff = current - relativedelta(years=years)

    while current >= cutoff:

        month_name = current.strftime("%B")      # January, February...

        sitemap_urls.append(
            f"{BASE_URL}{current.year}-{month_name}-1.xml"
        )

        current -= relativedelta(months=1)

    return sitemap_urls


# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    collection = get_collection(COLLECTION_NAME)

    total_processed = 0
    total_failed = 0

    sitemap_urls = generate_sitemap_urls()

    print(f"Total Monthly Sitemaps : {len(sitemap_urls)}")

    for sitemap_url in sitemap_urls:

        print(f"\nProcessing : {sitemap_url}")

        try:

            sitemap = download_xml(sitemap_url)

            urls = sitemap.find_all("url")

            print(f"URLs Found : {len(urls)}")

            processed, failed = store_urls(
                urls,
                collection,
                SOURCE_NAME
            )

            total_processed += processed
            total_failed += failed

        except Exception as e:

            print(f"Skipping sitemap : {e}")

    print_summary(
        SOURCE_NAME,
        total_processed,
        total_failed
    )


if __name__ == "__main__":
    main()