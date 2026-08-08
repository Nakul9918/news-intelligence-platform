import os
import json
import feedparser
from datetime import datetime

# ==========================================================
# RSS Sources
# ==========================================================

RSS_SOURCES = {
    "Economic Times": [
        "https://economictimes.indiatimes.com/rssfeedsdefault.cms"
    ],

    "The Hindu": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://www.thehindu.com/business/feeder/default.rss"
    ],

    "Indian Express": [
        "https://indianexpress.com/section/india/feed/",
        "https://indianexpress.com/section/business/feed/"
    ],

    "Hindustan Times": [
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
        "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml"
    ]
}


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

# ==========================================================
# Fetch News
# ==========================================================

def fetch_news():

    all_news = []
    seen_links = set()

    print("=" * 60)
    print("Fetching Latest News...")
    print("=" * 60)

    for source_name, urls in RSS_SOURCES.items():

        print(f"\nSource : {source_name}")

        for url in urls:

            try:
                feed = feedparser.parse(url, request_headers=HEADERS)

                if not feed.entries:
                    print(f"No entries found in feed : {url}")
                    continue

                print(f"Fetched {len(feed.entries)} articles")

                for entry in feed.entries:

                    link = entry.get("link", "").strip()

                    if not link:
                        continue

                    if link in seen_links:
                        continue

                    seen_links.add(link)

                    import hashlib
                    article_id = hashlib.sha256(link.encode("utf-8")).hexdigest()
                    now_str = datetime.utcnow().isoformat()

                    article = {
                        "article_id": article_id,
                        "link": link,
                        "source": {
                            "name": source_name,
                            "country": "India",
                            "language": "en",
                            "type": "rss"
                        },
                        "title": entry.get("title", "").strip(),
                        "description": entry.get("summary", "").strip(),
                        "content": "",
                        "clean_content": "",
                        "authors": ["Unknown"],
                        "language": "en",
                        "published_date": entry.get("published", ""),
                        "published_datetime": now_str,
                        "created_at": now_str,
                        "updated_at": now_str,
                        "fetched_at": now_str,
                        "last_pipeline_update": now_str,
                        "ingestion_type": "realtime",
                        "processing": {
                            "status": "PENDING",
                            "stage": "ingested",
                            "retry_count": 0
                        }
                    }

                    all_news.append(article)

            except Exception as e:
                print(f"Error while reading {url}")
                print(e)

    # ==========================================================
    # Save Backup JSON
    # ==========================================================

    os.makedirs("data", exist_ok=True)

    with open("data/news.json", "w", encoding="utf-8") as file:
        json.dump(
            all_news,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print(f"Total Articles Collected : {len(all_news)}")
    print("Backup saved to data/news.json")
    print("=" * 60)

    return all_news


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    news = fetch_news()

    print(f"\nCollected {len(news)} articles.")