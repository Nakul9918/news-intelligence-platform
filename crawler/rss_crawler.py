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
                feed = feedparser.parse(url)

                if feed.bozo:
                    print(f"Skipping invalid feed : {url}")
                    continue

                print(f"Fetched {len(feed.entries)} articles")

                for entry in feed.entries:

                    link = entry.get("link", "").strip()

                    if not link:
                        continue

                    if link in seen_links:
                        continue

                    seen_links.add(link)

                    article = {
                        "source": source_name,
                        "title": entry.get("title", "").strip(),
                        "link": link,
                        "summary": entry.get("summary", "").strip(),
                        "published": entry.get("published", ""),
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
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