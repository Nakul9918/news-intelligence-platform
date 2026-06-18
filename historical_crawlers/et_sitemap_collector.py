import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]

collection = db["historical_urls_et"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ET Sitemap Index
index_url = "https://economictimes.indiatimes.com/etstatic/sitemaps/et/news/sitemap-index.xml"

response = requests.get(index_url, headers=headers)

if response.status_code != 200:
    print("Failed to access sitemap index")
    exit()

soup = BeautifulSoup(response.text, "xml")

sitemaps = soup.find_all("sitemap")

print("Total sitemap files available:", len(sitemaps))

# Only first sitemap for testing
for sm in sitemaps[:1]:

    sitemap_url = sm.loc.text

    print("\nProcessing:", sitemap_url)

    try:

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

        print("URLs Found:", len(urls))

        count = 0

        for item in urls:

            try:

                article_url = item.loc.text

                published = (
                    item.lastmod.text
                    if item.lastmod
                    else None
                )

                collection.update_one(
                    {"link": article_url},
                    {
                        "$set": {
                            "source": "Economic Times",
                            "link": article_url,
                            "published": published
                        }
                    },
                    upsert=True
                )

                count += 1

                if count % 1000 == 0:
                    print(f"Stored {count} URLs")

            except Exception:
                pass

        print(f"\nCompleted Sitemap")
        print(f"Total Stored: {count}")

    except Exception as e:

        print("Error:", e)

print("\nET Collection Completed Successfully")