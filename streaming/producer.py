from kafka import KafkaProducer
from crawler.rss_crawler import fetch_news
import json

print("=" * 60)
print("Kafka Producer Started")
print("=" * 60)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("Connected to Kafka")
print("=" * 60)

articles = fetch_news()

print(f"\nFetched {len(articles)} articles.\n")

for article in articles:
    producer.send("news-topic-v2", article)

producer.flush()
producer.close()

print("=" * 60)
print(f"Successfully sent {len(articles)} articles to Kafka.")
print("=" * 60)