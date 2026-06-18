import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_urls_ndtv"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

for year in [2024, 2025, 2026]:

    max_month = 12

    if year == 2026:
        max_month = 6

    for month in range(1, max_month + 1):

        print(f"\nProcessing {year}-{month}")

        sitemap_url = (
            f"https://www.ndtv.com/sitemap.xml"
            f"?yyyy={year}"
            f"&mm={month}"
            f"&sitename=ndtv-news"
            f"&category="
        )

        try:

            response = requests.get(
                sitemap_url,
                headers=headers,
                timeout=30
            )

            print("Status:", response.status_code)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(
                response.text,
                "xml"
            )

            urls = soup.find_all("url")

            print(
                "Found URLs:",
                len(urls)
            )

            for item in urls:

                article_url = item.loc.text
                published = item.lastmod.text

                collection.update_one(
                    {"link": article_url},
                    {
                        "$set": {
                            "source": "NDTV",
                            "link": article_url,
                            "published": published,
                            "year": year,
                            "month": month
                        }
                    },
                    upsert=True
                )

            time.sleep(2)

        except Exception as e:
            print(e)

print("\nCompleted")