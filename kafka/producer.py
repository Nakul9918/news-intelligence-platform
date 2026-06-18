from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

with open("data/news.json", "r", encoding="utf-8") as file:
    news_list = json.load(file)

for news in news_list:
    producer.send("news-topic", news)

producer.flush()

print(f"{len(news_list)} articles sent to Kafka")