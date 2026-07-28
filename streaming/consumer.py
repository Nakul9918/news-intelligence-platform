"""
Kafka Consumer

Workflow:
Kafka Topic
    ↓
Receive Article
    ↓
Check Duplicate
    ↓
Store Raw Article in MongoDB
    ↓
Run Realtime NLP Pipeline
"""
print("Consumer file started")
import json
from datetime import datetime, UTC

from kafka import KafkaConsumer
from pymongo import MongoClient

from realtime_pipeline.realtime_nlp_pipeline import process_article


# =====================================================
# MongoDB Configuration
# =====================================================

client = MongoClient("mongodb://localhost:27017/")

db = client["news_db"]

collection = db["realtime_articles"]


# =====================================================
# Kafka Consumer Configuration
# =====================================================

consumer = KafkaConsumer(
    "news-topic-v2",
    bootstrap_servers="localhost:9092",
    group_id="news-consumer-group-v2",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)


# =====================================================
# Consumer Started
# =====================================================

print("=" * 70)
print("Kafka Consumer Started")
print("Waiting for news articles...")
print("=" * 70)


# =====================================================
# Main Consumer Loop
# =====================================================

try:

    for message in consumer:

        article = message.value

        print("\n" + "=" * 70)
        print(f"Received : {article.get('title')}")
        print("=" * 70)

        # -------------------------------------------------
        # Duplicate Check
        # -------------------------------------------------

        if collection.find_one({"link": article["link"]}):

            print("Duplicate article. Skipping...")

            continue

        # -------------------------------------------------
        # Build MongoDB Document
        # -------------------------------------------------

        document = {

            "title": article.get("title"),

            "link": article.get("link"),

            "description": article.get("description"),

            "source": article.get("source"),

            "published": article.get("published"),

            "created_at": datetime.now(UTC),

            "updated_at": datetime.now(UTC),

            "processing": {

                "status": "PENDING",

                "completed": False,

                "started_at": datetime.now(UTC),

                "completed_at": None,

                "error": None

            }

        }

        # -------------------------------------------------
        # Insert Raw Article
        # -------------------------------------------------

        result = collection.insert_one(document)

        article_id = str(result.inserted_id)

        print(f"Saved to MongoDB : {article_id}")

        # -------------------------------------------------
        # Run NLP Pipeline
        # -------------------------------------------------

        print("\nStarting Realtime NLP Pipeline...")

        success = process_article(article_id)

        if success:

            collection.update_one(

                {

                    "_id": result.inserted_id

                },

                {

                    "$set": {

                        "processing.completed_at": datetime.now(UTC)

                    }

                }

            )

            print("Realtime NLP Pipeline Completed")

        else:

            print("Realtime NLP Pipeline Failed")


# =====================================================
# Stop Consumer
# =====================================================

except KeyboardInterrupt:

    print("\nConsumer stopped by user.")


except Exception as e:

    print(f"\nConsumer Error : {e}")


finally:

    consumer.close()

    client.close()

    print("\nKafka Consumer Closed.")