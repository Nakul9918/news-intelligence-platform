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

COLLECTION_NAME = "historical_articles"

SITEMAP_URL = (
    "https://indianexpress.com/"
    "sitemap.xml?yyyy=2026&mm=06&dd=01"
)

# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    collection = get_collection(COLLECTION_NAME)

    sitemap = download_xml(SITEMAP_URL)

    urls = sitemap.find_all("url")

    print(f"Total URLs Found : {len(urls)}")

    processed, failed = store_urls(
        urls=urls,
        collection=collection,
        source_name=SOURCE_NAME
    )

    print_summary(
        SOURCE_NAME,
        processed,
        failed
    )


if __name__ == "__main__":
    main()
