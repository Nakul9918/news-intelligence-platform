import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_urls_et"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

index_url = "https://economictimes.indiatimes.com/etstatic/sitemaps/et/news/sitemap-index.xml"

response = requests.get(index_url, headers=headers)

soup = BeautifulSoup(response.text, "xml")

sitemaps = soup.find_all("sitemap")

print("Total sitemap files:", len(sitemaps))

for sm in sitemaps[:10]:   # first 10 files for testing

    sitemap_url = sm.loc.text

    print("Processing:", sitemap_url)

    r = requests.get(
        sitemap_url,
        headers=headers,
        timeout=60
    )

    sitemap_soup = BeautifulSoup(
        r.text,
        "xml"
    )

    urls = sitemap_soup.find_all("url")

    print("URLs:", len(urls))

    for item in urls:

        collection.update_one(
            {"link": item.loc.text},
            {
                "$set": {
                    "source": "ET",
                    "link": item.loc.text,
                    "published": item.lastmod.text
                }
            },
            upsert=True
        )

print("Done")
