"""
Realtime Bootstrap Producer

Collects Aug 1-7 articles from all four news sources
and publishes them to Kafka.
"""

import json
import logging
from datetime import datetime

from kafka import KafkaProducer

from bootstrap.realtime_bootstrap.et_loader import (
    collect_august_articles as collect_et_articles
)

from bootstrap.realtime_bootstrap.thehindu_loader import (
    collect_august_articles as collect_thehindu_articles
)

from bootstrap.realtime_bootstrap.indianexpress_loader import (
    collect_august_articles as collect_indianexpress_articles
)

from bootstrap.realtime_bootstrap.hindustantimes_loader import (
    collect_august_articles as collect_hindustantimes_articles
)


# ==========================================================
# Configuration
# ==========================================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "news-topic-v2"


# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("Realtime_Bootstrap_Producer")


# ==========================================================
# JSON Serializer
# ==========================================================

def json_serializer(value):
    """
    Convert article dictionary into JSON bytes.

    datetime objects are converted to ISO format.
    """

    return json.dumps(
        value,
        default=lambda obj: (
            obj.isoformat()
            if isinstance(obj, datetime)
            else str(obj)
        ),
        ensure_ascii=False
    ).encode("utf-8")


# ==========================================================
# Create Kafka Producer
# ==========================================================

def create_producer():

    logger.info("Connecting to Kafka...")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=json_serializer,
        acks="all",
        retries=5,
        linger_ms=5
    )

    logger.info("Kafka connection successful")

    return producer


# ==========================================================
# Publish Articles
# ==========================================================

def publish_articles(producer, articles):

    sent = 0
    failed = 0

    total = len(articles)

    logger.info("=" * 70)
    logger.info("STARTING KAFKA PUBLISH")
    logger.info(f"Total articles: {total}")
    logger.info(f"Topic: {KAFKA_TOPIC}")
    logger.info("=" * 70)

    for index, article in enumerate(articles, start=1):

        try:

            article_id = article.get("article_id")

            future = producer.send(
                KAFKA_TOPIC,
                key=(
                    article_id.encode("utf-8")
                    if article_id
                    else None
                ),
                value=article
            )

            metadata = future.get(timeout=30)

            sent += 1

            if sent % 500 == 0 or sent == total:

                logger.info(
                    f"Progress: {sent}/{total} | "
                    f"Partition: {metadata.partition} | "
                    f"Offset: {metadata.offset}"
                )

        except Exception as e:

            failed += 1

            logger.error(
                f"Failed article {index}: {e}"
            )

    producer.flush()

    logger.info("=" * 70)
    logger.info("KAFKA PUBLISH COMPLETE")
    logger.info(f"Sent   : {sent}")
    logger.info(f"Failed : {failed}")
    logger.info(f"Total  : {total}")
    logger.info("=" * 70)

    return sent, failed


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 70)
    print("REALTIME BOOTSTRAP PRODUCER")
    print("=" * 70)

    # ------------------------------------------------------
    # Collect Economic Times
    # ------------------------------------------------------

    print("\nLoading Economic Times...")

    et_articles = collect_et_articles()

    print(
        f"Economic Times : {len(et_articles)}"
    )

    # ------------------------------------------------------
    # Collect The Hindu
    # ------------------------------------------------------

    print("\nLoading The Hindu...")

    hindu_articles = collect_thehindu_articles()

    print(
        f"The Hindu : {len(hindu_articles)}"
    )

    # ------------------------------------------------------
    # Collect Indian Express
    # ------------------------------------------------------

    print("\nLoading Indian Express...")

    ie_articles = collect_indianexpress_articles()

    print(
        f"Indian Express : {len(ie_articles)}"
    )

    # ------------------------------------------------------
    # Collect Hindustan Times
    # ------------------------------------------------------

    print("\nLoading Hindustan Times...")

    ht_articles = collect_hindustantimes_articles()

    print(
        f"Hindustan Times : {len(ht_articles)}"
    )

    # ------------------------------------------------------
    # Combine
    # ------------------------------------------------------

    all_articles = (
        et_articles
        + hindu_articles
        + ie_articles
        + ht_articles
    )

    print("\n" + "=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)

    print(
        f"Economic Times    : {len(et_articles)}"
    )

    print(
        f"The Hindu         : {len(hindu_articles)}"
    )

    print(
        f"Indian Express    : {len(ie_articles)}"
    )

    print(
        f"Hindustan Times   : {len(ht_articles)}"
    )

    print("-" * 70)

    print(
        f"TOTAL             : {len(all_articles)}"
    )

    print("=" * 70)

    # ------------------------------------------------------
    # Kafka
    # ------------------------------------------------------

    producer = None

    try:

        producer = create_producer()

        sent, failed = publish_articles(
            producer,
            all_articles
        )

        print("\n" + "=" * 70)
        print("FINAL KAFKA RESULT")
        print("=" * 70)

        print(
            f"Articles collected : {len(all_articles)}"
        )

        print(
            f"Messages sent      : {sent}"
        )

        print(
            f"Messages failed    : {failed}"
        )

        print("=" * 70)

    finally:

        if producer is not None:

            producer.flush()
            producer.close()

            logger.info(
                "Kafka producer closed"
            )


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()