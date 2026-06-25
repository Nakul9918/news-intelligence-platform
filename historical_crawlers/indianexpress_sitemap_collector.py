from common_collector import (
    get_collection,
    download_xml,
    store_urls,
    print_summary
)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "Indian Express"

COLLECTION_NAME = "historical_urls_indianexpress"

SITEMAP_INDEX_URL = "https://indianexpress.com/sitemap.xml"

SITEMAP_LIMIT = 1

# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    collection = get_collection(
        COLLECTION_NAME
    )

    sitemap_index = download_xml(
        SITEMAP_INDEX_URL
    )

    sitemaps = sitemap_index.find_all(
        "sitemap"
    )

    print(
        f"Total Sitemap Files : {len(sitemaps)}"
    )

    if SITEMAP_LIMIT:
        sitemaps = sitemaps[:SITEMAP_LIMIT]

    total_processed = 0
    total_failed = 0

    for sitemap in sitemaps:

        sitemap_url = sitemap.loc.text

        print("\nProcessing")
        print(sitemap_url)

        xml = download_xml(
            sitemap_url
        )

        urls = xml.find_all(
            "url"
        )

        processed, failed = store_urls(
            urls,
            collection,
            SOURCE_NAME
        )

        total_processed += processed
        total_failed += failed

    print_summary(
        SOURCE_NAME,
        total_processed,
        total_failed
    )


if __name__ == "__main__":
    main()