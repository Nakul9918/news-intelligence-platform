from kafka import KafkaProducer
import json

from crawler.rss_crawler import fetch_news


producer = KafkaProducer(

    bootstrap_servers="localhost:9092",

    value_serializer=lambda value: json.dumps(value).encode("utf-8")

)

news_list = fetch_news()

for article in news_list:

    producer.send("news-topic", article)

    print(f"Sent -> {article['title']}")

producer.flush()

print(f"\nTotal {len(news_list)} articles sent to Kafka.")