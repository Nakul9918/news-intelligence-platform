
"""
Bootstrap Kafka Producer

Workflow

Collectors
      ↓
Merge Articles
      ↓
Remove Duplicates
      ↓
Publish to Kafka
"""

import json
import logging
import time
from config import BOOTSTRAP_FLUSH_INTERVAL
from config import LOG_SEPARATOR


from kafka import KafkaProducer

from bootstrap.collectors.et_collector import (
    collect_et_articles
)

from bootstrap.collectors.thehindu_collector import (
    collect_thehindu_articles
)

from bootstrap.collectors.indianexpress_collector import (
    collect_indianexpress_articles
)

from bootstrap.collectors.hindustantimes_collector import (
    collect_hindustantimes_articles
)

from config import (

    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,

    KAFKA_ACKS,
    KAFKA_RETRIES,
    KAFKA_LINGER_MS,
    KAFKA_BATCH_SIZE,
    KAFKA_COMPRESSION,
    KAFKA_MAX_REQUEST_SIZE,
    KAFKA_REQUEST_TIMEOUT,
    KAFKA_DELIVERY_TIMEOUT,

)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(

    "Bootstrap_Producer"

)

# =====================================================
# Configuration
# =====================================================

PRODUCER_VERSION = "1.0.0"



# =====================================================
# Kafka Producer
# =====================================================

producer = KafkaProducer(

    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

    value_serializer=lambda value: json.dumps(
        value,
        default=str
    ).encode("utf-8"),

    acks=KAFKA_ACKS,

    retries=KAFKA_RETRIES,

    linger_ms=KAFKA_LINGER_MS,

    batch_size=KAFKA_BATCH_SIZE,

    compression_type=KAFKA_COMPRESSION,

    max_request_size=KAFKA_MAX_REQUEST_SIZE,

    request_timeout_ms=KAFKA_REQUEST_TIMEOUT,

    delivery_timeout_ms=KAFKA_DELIVERY_TIMEOUT,

)

# =====================================================
# Collectors
# =====================================================

COLLECTORS = [

    (

        "Economic Times",

        collect_et_articles

    ),

    # (

    #     "The Hindu",

    #     collect_thehindu_articles

    # ),

    # (

    #     "Indian Express",

    #     collect_indianexpress_articles

    # ),

    # (

    #     "Hindustan Times",

    #     collect_hindustantimes_articles

    # )

]

# =====================================================
# Remove Duplicate Articles
# =====================================================

def remove_duplicates(

    articles

):

    """
    Remove duplicate articles using
    article link.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(

        "Removing Duplicate Articles"

    )

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    unique_articles = []

    seen_links = set()

    duplicates = 0

    missing_links = 0

    for article in articles:

        try:

            link = article.get(

                "link"

            )

            # ----------------------------------------
            # Missing Link
            # ----------------------------------------

            if not link:

                missing_links += 1

                continue

            # ----------------------------------------
            # Duplicate Link
            # ----------------------------------------

            if link in seen_links:

                duplicates += 1

                continue

            seen_links.add(

                link

            )

            unique_articles.append(

                article

            )

        except Exception:

            logger.exception(

                "Duplicate Check Failed"

            )

    duration = round(

        time.perf_counter()

        - started,

        3

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        "Duplicate Removal Summary"

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Input Articles      : {len(articles)}"

    )

    logger.info(

        f"Unique Articles     : {len(unique_articles)}"

    )

    logger.info(

        f"Duplicate Articles  : {duplicates}"

    )

    logger.info(

        f"Missing Links       : {missing_links}"

    )

    logger.info(

        f"Processing Time     : {duration:.2f} sec"

    )

    logger.info(LOG_SEPARATOR)

    return (

        unique_articles,

        duplicates

    )
# =====================================================
# Publish Articles
# =====================================================

def publish_articles(

    articles

):

    """
    Publish articles to Kafka.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(

        "Publishing Articles To Kafka"

    )

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    published = 0

    failed = 0

    for article in articles:

        try:

            # ----------------------------------------
            # Remove Non-Serializable Fields
            # ----------------------------------------

            article_to_send = article.copy()

            article_to_send.pop(

                "published_datetime",

                None

            )

            # ----------------------------------------
            # Publish
            # ----------------------------------------

            future = producer.send(

                KAFKA_TOPIC,

                value=article_to_send

            )

            # ----------------------------------------
            # Wait For Acknowledgement
            # ----------------------------------------

            metadata = future.get(

                timeout=30

            )

            published += 1

            # ----------------------------------------
            # Flush Batch
            # ----------------------------------------

            if (

                published % BOOTSTRAP_FLUSH_INTERVAL

                == 0

            ):

                producer.flush()

                logger.info(

                    f"Published : {published}"

                )

                logger.debug(

                    f"Topic      : {metadata.topic}"

                )

                logger.debug(

                    f"Partition  : {metadata.partition}"

                )

                logger.debug(

                    f"Offset     : {metadata.offset}"

                )

        except Exception:

            failed += 1

            logger.exception(

                "Kafka Publish Failed"

            )

    producer.flush()

    duration = round(

        time.perf_counter()

        - started,

        3

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        "Kafka Publish Summary"

    )

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Topic               : {KAFKA_TOPIC}"

    )

    logger.info(

        f"Articles            : {len(articles)}"

    )

    logger.info(

        f"Published           : {published}"

    )

    logger.info(

        f"Failed              : {failed}"

    )

    logger.info(

        f"Processing Time     : {duration:.2f} sec"

    )

    logger.info(LOG_SEPARATOR)

    return (

        published,

        failed

    )
# =====================================================
# Run Bootstrap
# =====================================================
# =====================================================
# Run Bootstrap
# =====================================================

def run_bootstrap():

    """
    Run complete bootstrap pipeline.
    """

    logger.info(LOG_SEPARATOR)

    logger.info("Bootstrap Collection Started")

    logger.info(LOG_SEPARATOR)

    started = time.perf_counter()

    all_articles = []

    collector_summary = {}

    failed_sources = []

    duplicates = 0

    published = 0

    failed_publish = 0

    try:

        # =================================================
        # Run Collectors
        # =================================================

        for source_name, collector in COLLECTORS:

            logger.info(LOG_SEPARATOR)

            logger.info(

                f"Collecting : {source_name}"

            )

            logger.info(LOG_SEPARATOR)

            collector_started = time.perf_counter()

            try:

                articles = collector()

                collector_time = round(

                    time.perf_counter()

                    - collector_started,

                    3

                )

                collector_summary[source_name] = {

                    "articles": len(articles),

                    "time": collector_time

                }

                all_articles.extend(

                    articles

                )

                logger.info(

                    f"Collected : {len(articles)}"

                )

                logger.info(

                    f"Time      : {collector_time:.2f} sec"

                )

            except Exception:

                failed_sources.append(

                    source_name

                )

                collector_summary[source_name] = {

                    "articles": 0,

                    "time": 0

                }

                logger.exception(

                    f"{source_name} Failed"

                )

        # =================================================
        # Collection Summary
        # =================================================

        logger.info(LOG_SEPARATOR)

        logger.info("Collection Summary")

        logger.info(LOG_SEPARATOR)

        for source, info in collector_summary.items():

            logger.info(

                f"{source:<20}"

                f" : "

                f"{info['articles']} "

                f"articles "

                f"({info['time']:.2f} sec)"

            )

        logger.info("-" * 80)

        logger.info(

            f"Collected Articles : {len(all_articles)}"

        )

        # =================================================
        # Remove Duplicates
        # =================================================

        unique_articles, duplicates = remove_duplicates(

            all_articles

        )

        # =================================================
        # Publish To Kafka
        # =================================================

        published, failed_publish = publish_articles(

            unique_articles

        )

    finally:

        # =================================================
        # Always Close Kafka Producer
        # =================================================

        logger.info("Closing Kafka Producer...")

        producer.flush()

        producer.close()

        logger.info("Kafka Producer Closed")

    # =================================================
    # Final Summary
    # =================================================

    duration = round(

        time.perf_counter()

        - started,

        3

    )

    logger.info(LOG_SEPARATOR)

    logger.info("Bootstrap Summary")

    logger.info(LOG_SEPARATOR)

    logger.info(

        f"Collected Articles : {len(all_articles)}"

    )

    logger.info(

        f"Duplicate Articles : {duplicates}"

    )

    logger.info(

        f"Published          : {published}"

    )

    logger.info(

        f"Publish Failed     : {failed_publish}"

    )

    logger.info(

        f"Failed Collectors  : {len(failed_sources)}"

    )

    logger.info(

        f"Execution Time     : {duration:.2f} sec"

    )

    if failed_sources:

        logger.warning(LOG_SEPARATOR)

        logger.warning("Failed Collectors")

        logger.warning(LOG_SEPARATOR)

        for source in failed_sources:

            logger.warning(source)

    logger.info(LOG_SEPARATOR)

    logger.info("Bootstrap Completed")

    logger.info(LOG_SEPARATOR)