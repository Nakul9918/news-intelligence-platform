# Import RSS feed parser library
# Used to read RSS/XML feeds from news websites
import feedparser

# Import JSON library
# Used to save collected news into JSON format
import json

# Import all RSS feed URLs from rss_sources.py
# Example:
# BBC, NDTV, The Hindu, Economic Times
from rss_sources import RSS_SOURCES


# Empty list to store all collected news articles
all_news = []


# Loop through every news source
# source_name = BBC
# rss_url = https://feeds.bbci.co.uk/news/rss.xml
for source_name, rss_url in RSS_SOURCES.items():

    print(f"\nFetching news from {source_name}...\n")

    # Read RSS feed
    feed = feedparser.parse(rss_url)

    # Display total articles available from current source
    print(f"Total Articles Available: {len(feed.entries)}\n")

    # Take first 5 articles from each source
    for article in feed.entries[:5]:

        # Create structured data
        # Dictionary format
        news_item = {
            "source": source_name,

            # Get title
            # If title not available use N/A
            "title": article.get("title", "N/A"),

            # Get article URL
            "link": article.get("link", "N/A"),

            # Get publication date
            "published": article.get("published", "N/A")
        }

        # Store article inside list
        all_news.append(news_item)

        # Print output on screen
        print("Source:", source_name)
        print("Title:", news_item["title"])
        print("Link:", news_item["link"])
        print("Published:", news_item["published"])
        print("-" * 50)


# Open news.json file
# "w" means write mode
# encoding='utf-8' supports special characters
with open("data/news.json", "w", encoding="utf-8") as file:

    # Save list into JSON file
    json.dump(
        all_news,
        file,
        indent=4,
        ensure_ascii=False
    )


# Final statistics
print(f"\nTotal Articles Collected: {len(all_news)}")

print("News saved to data/news.json")