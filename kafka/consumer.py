from kafka import KafkaConsumer
import json
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles"]

# Kafka Consumer
consumer = KafkaConsumer(
    "news-topic",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Waiting for messages...")

for message in consumer:

    article = message.value

    existing = collection.find_one({
        "link": article["link"]
    })

    if existing:
        print("Duplicate skipped:", article["title"])

    else:
        collection.insert_one(article)
        print("News saved:", article["title"])