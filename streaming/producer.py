from kafka import KafkaProducer
from pymongo import MongoClient

from crawler.rss_crawler import fetch_news

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
    RSS_CHECK_INTERVAL,
)

import json
import time

# ==========================================================
# MongoDB
# ==========================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

realtime_collection = db[REALTIME_COLLECTION_NAME]

# ==========================================================
# Kafka Producer
# ==========================================================

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("=" * 70)
print("Realtime Kafka Producer Started")
print("=" * 70)

# ==========================================================
# Main Loop
# ==========================================================

while True:

    try:

        print("\n" + "=" * 70)
        print("Fetching Latest RSS Articles...")
        print("=" * 70)

        articles = fetch_news()

        rss_articles = len(articles)

        new_articles = 0
        duplicate_articles = 0

        for article in articles:

            if realtime_collection.find_one(
                {
                    "link": article["link"]
                }
            ):

                duplicate_articles += 1
                continue

            producer.send(
                KAFKA_TOPIC,
                article,
            )

            new_articles += 1

        producer.flush()

        print("\n" + "=" * 70)
        print("Producer Summary")
        print("=" * 70)
        print(f"RSS Articles       : {rss_articles}")
        print(f"New Articles       : {new_articles}")
        print(f"Duplicates Skipped : {duplicate_articles}")
        print("=" * 70)

        print(f"\nSleeping for {RSS_CHECK_INTERVAL} seconds...\n")

        time.sleep(RSS_CHECK_INTERVAL)

    except KeyboardInterrupt:

        print("\nProducer stopped by user.")
        break

    except Exception as e:

        print("\nProducer Error")
        print(e)

        print("\nRetrying in 60 seconds...\n")

        time.sleep(60)

# ==========================================================
# Shutdown
# ==========================================================

producer.close()

client.close()

print("=" * 70)
print("Producer Closed")
print("=" * 70)