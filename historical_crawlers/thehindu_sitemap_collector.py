from historical_crawlers.common_collector import (
    get_collection,
    download_xml,
    store_urls,
    print_summary
)

# =====================================================
# MongoDB Collection
# =====================================================

COLLECTION_NAME = "historical_urls_thehindu"

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "The Hindu"

SITEMAP_URL = "https://www.thehindu.com/sitemap/update/all.xml"

# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    collection = get_collection(COLLECTION_NAME)

    try:

        print(f"Downloading sitemap...")
        print(SITEMAP_URL)

        sitemap = download_xml(SITEMAP_URL)

        urls = sitemap.find_all("url")

        print(f"\nTotal URLs Found : {len(urls)}")

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

    except Exception as e:

        print("\n" + "=" * 70)
        print(f"Error while processing {SOURCE_NAME}")
        print("=" * 70)
        print(e)


if __name__ == "__main__":
    main()