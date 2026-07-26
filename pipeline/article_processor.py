"""
=========================================================
Shared Article Processor

Used by:
1. Historical Pipeline
2. Realtime Kafka Consumer

Responsibilities:
- Download article
- Parse article
- Return extracted data

NLP processing will be added incrementally.
=========================================================
"""

from newspaper import Article


class ArticleProcessor:

    def extract(self, article):

        print(f"\nDownloading article...")

        news = Article(article["link"])

        news.download()

        news.parse()

        extracted_article = {

            "source": article.get("source"),

            "link": article.get("link"),

            "published": article.get("published"),

            "title": news.title,

            "authors": news.authors,

            "content": news.text

        }

        print("Article extracted successfully.")

        return extracted_article