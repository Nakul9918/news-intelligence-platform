"""
Project Configuration
News Intelligence Platform
"""

# =====================================================
# MongoDB Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "news_db"

# Collections
COLLECTION_NAME = "historical_articles"
REALTIME_COLLECTION_NAME = "realtime_articles"


# =====================================================
# Kafka Configuration
# =====================================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

KAFKA_TOPIC = "news-topic-v2"

KAFKA_CONSUMER_GROUP = "news-consumer-group-v2"


# =====================================================
# Realtime Producer Configuration
# =====================================================

# Check RSS every 1 hour
RSS_CHECK_INTERVAL = 3600


# =====================================================
# Elasticsearch Configuration
# =====================================================

ELASTICSEARCH_HOST = "http://localhost:9200"

ELASTICSEARCH_INDEX = "news_articles"


# =====================================================
# HTTP Request Configuration
# =====================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 60

MAX_RETRIES = 3


# =====================================================
# MongoDB Batch Configuration
# =====================================================

BATCH_SIZE = 500


# =====================================================
# Historical Collection Configuration
# =====================================================

ALLOWED_YEARS = [
    "2024",
    "2025",
    "2026"
]

MAX_ARTICLES_PER_MONTH = 500


# =====================================================
# Skip Unwanted Sitemap Types
# =====================================================

SKIP_KEYWORDS = [
    "photo",
    "photos",
    "video",
    "videos",
    "liveblog",
    "live-blog",
    "webstory",
    "webstories",
    "topic",
    "static",
    "section",
    "education-static",
    "telugu",
    "bangla",
    "hindi",
    "urdu",
    "podcast"
]


# =====================================================
# Supported News Sources
# =====================================================

SUPPORTED_SOURCES = [
    "Economic Times",
    "The Hindu",
    "Indian Express",
    "Hindustan Times"
]


# =====================================================
# Historical Processing Configuration
# =====================================================

PROCESS_BATCH_SIZE = 5


# =====================================================
# Collections
# =====================================================

COLLECTIONS = [
    COLLECTION_NAME
]

REALTIME_COLLECTIONS = [
    REALTIME_COLLECTION_NAME
]