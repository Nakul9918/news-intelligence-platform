"""
RSS Crawler

Responsibility:
- Read RSS feeds
- Return news articles
- DO NOT save to JSON
- DO NOT connect to Kafka
"""

import feedparser

from crawler.rss_sources import RSS_SOURCES


def fetch_news():

    all_news = []

    for source_name, rss_url in RSS_SOURCES.items():

        print(f"\nFetching news from {source_name}...")

        feed = feedparser.parse(rss_url)

        print(f"Total Articles: {len(feed.entries)}")

        for article in feed.entries[:5]:

            news_item = {

                "source": source_name,

                "title": article.get("title", "N/A"),

                "link": article.get("link", "N/A"),

                "published": article.get("published", "N/A")

            }

            all_news.append(news_item)

    return all_news


if __name__ == "__main__":

    news = fetch_news()

    print(f"\nCollected {len(news)} articles")