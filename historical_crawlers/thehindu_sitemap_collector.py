from common_collector import (
    get_collection,
    download_xml,
    store_urls,
    print_summary
)

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "The Hindu"

COLLECTION_NAME = "historical_urls_thehindu"

SITEMAP_URL = (
    "https://www.thehindu.com/"
    "sitemap/googlenews/all/all.xml"
)

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

    sitemap = download_xml(
        SITEMAP_URL
    )

    urls = sitemap.find_all(
        "url"
    )

    print(
        f"Total URLs Found : {len(urls)}"
    )

    processed, failed = store_urls(
        urls,
        collection,
        SOURCE_NAME
    )

    print_summary(
        SOURCE_NAME,
        processed,
        failed
    )


if __name__ == "__main__":
    main()