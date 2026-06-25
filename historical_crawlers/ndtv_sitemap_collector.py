import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# =====================================================
# Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "news_db"
COLLECTION_NAME = "historical_urls_ndtv"

SOURCE_NAME = "NDTV"

START_YEAR = 2024
END_YEAR = 2026

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIMEOUT = 30
REQUEST_DELAY = 2

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


# =====================================================
# Fetch Sitemap URLs
# =====================================================

def fetch_urls(year, month):

    sitemap_url = (
        f"https://www.ndtv.com/sitemap.xml"
        f"?yyyy={year}"
        f"&mm={month}"
        f"&sitename=ndtv-news"
        f"&category="
    )

    response = requests.get(
        sitemap_url,
        headers=HEADERS,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "xml"
    )

    return soup.find_all("url")


# =====================================================
# Store URLs
# =====================================================

def store_urls(urls, year, month):

    stored = 0
    failed = 0

    print(f"URLs Found : {len(urls)}")

    for item in urls:

        try:

            article_url = item.loc.text

            published = (
                item.lastmod.text
                if item.lastmod
                else None
            )

            collection.update_one(
                {
                    "link": article_url
                },
                {
                    "$set": {
                        "source": SOURCE_NAME,
                        "link": article_url,
                        "published": published,
                        "year": year,
                        "month": month
                    }
                },
                upsert=True
            )

            stored += 1

            if stored % 500 == 0:
                print(f"Stored {stored} URLs")

        except Exception:
            failed += 1

    return stored, failed


# =====================================================
# Main Function
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    total_stored = 0
    total_failed = 0

    for year in range(START_YEAR, END_YEAR + 1):

        max_month = 12

        if year == END_YEAR:
            max_month = 6

        for month in range(1, max_month + 1):

            print("\n" + "=" * 70)
            print(f"Processing : {year}-{month:02d}")
            print("=" * 70)

            try:

                urls = fetch_urls(
                    year,
                    month
                )

                stored, failed = store_urls(
                    urls,
                    year,
                    month
                )

                total_stored += stored
                total_failed += failed

                time.sleep(REQUEST_DELAY)

            except Exception as e:

                print(e)

    print("\n" + "=" * 70)
    print("Collection Completed Successfully")
    print("=" * 70)
    print(f"Stored : {total_stored}")
    print(f"Failed : {total_failed}")


# =====================================================
# Run Program
# =====================================================

if __name__ == "__main__":
    main()