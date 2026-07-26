"""
=====================================================
Kafka Consumer

Responsibilities:
1. Read articles from Kafka
2. Check duplicate URLs
3. Pass article to shared processor
=====================================================
"""

from kafka import KafkaConsumer
from pymongo import MongoClient
import json

from pipeline.article_processor import ArticleProcessor

# =====================================================
# MongoDB
# =====================================================

client = MongoClient("mongodb://localhost:27017/")

db = client["news_db"]

collection = db["historical_articles"]

# =====================================================
# Processor
# =====================================================

processor = ArticleProcessor()

# =====================================================
# Kafka Consumer
# =====================================================

consumer = KafkaConsumer(

    "news-topic",

    bootstrap_servers="localhost:9092",

    auto_offset_reset="latest",

    enable_auto_commit=True,

    value_deserializer=lambda m: json.loads(
        m.decode("utf-8")
    )

)

print("=" * 60)
print("Realtime Consumer Started")
print("Waiting for Kafka messages...")
print("=" * 60)

# =====================================================
# Consume Messages
# =====================================================

for message in consumer:

    article = message.value

    print(f"\nReceived : {article.get('title')}")

    # -----------------------------------------------
    # Duplicate Check
    # -----------------------------------------------

    existing = collection.find_one({

        "link": article["link"]

    })

    if existing:

        print("Duplicate skipped.")

        continue

    try:

        extracted_article = processor.extract(article)

        print("\nExtraction Successful")

        print(f"Title   : {extracted_article['title']}")
        print(f"Author  : {extracted_article['authors']}")
        print(f"Content : {len(extracted_article['content'])} characters")

        # MongoDB insertion will be added
        # after NLP integration

    except Exception as e:

        print(f"\nProcessing Failed")

        print(e)