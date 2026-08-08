"""
Project Configuration
News Intelligence Platform
"""
# =====================================================
# MongoDB Configuration
# =====================================================

MONGO_URI = "mongodb://127.0.0.1:27017"

DATABASE_NAME = "news_db"

# =====================================================
# Collections
# =====================================================

REALTIME_COLLECTION_NAME = "realtime_articles"

# =====================================================
# Kafka Configuration
# =====================================================

KAFKA_BOOTSTRAP_SERVERS = "127.0.0.1:9092"

KAFKA_TOPIC = "news-topic-v2"

KAFKA_CONSUMER_GROUP = "news-consumer-group-v2"

AUTO_OFFSET_RESET = "earliest"

ENABLE_AUTO_COMMIT = True


# =====================================================
# Realtime Producer Configuration
# =====================================================

# Check RSS every 1 hour
RSS_CHECK_INTERVAL = 3600

# Retry if producer fails
PRODUCER_RETRY_DELAY = 60


# =====================================================
# Elasticsearch Configuration
# =====================================================

ELASTICSEARCH_HOST = "http://127.0.0.1:9200"

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

# Number of articles processed by workers in one run

BATCH_SIZE = 100

# =====================================================
# Historical Collection Configuration
# =====================================================

# Bootstrap Date Range

BOOTSTRAP_START_DATE = "2026-08-01"

BOOTSTRAP_END_DATE = "2026-08-07"

MAX_ARTICLES_PER_MONTH = 500
# =====================================================
# Skip Unwanted Sitemap Types
# =====================================================

BOOTSTRAP_SKIP_KEYWORDS = [
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

PROCESS_BATCH_SIZE = 20


# =====================================================
# Collections
# =====================================================

COLLECTIONS = [
    REALTIME_COLLECTION_NAME
]
# =====================================================
# Logging Configuration
# =====================================================

LOG_SEPARATOR = "=" * 80
SMALL_SEPARATOR = "-" * 80

# =====================================================
# Bootstrap Producer Configuration
# =====================================================

BOOTSTRAP_FLUSH_INTERVAL = 500

# =====================================================
# Bootstrap Configuration
# =====================================================

SITEMAP_SKIP_KEYWORDS = [
    "liveblog",
    "video",
    "photos",
    "today",
    "yesterday",
    "category",
    "news-sitemap",
    "webstories",
    "horoscope",
    "aboutsitemap",
    "section",
]

# =====================================================
# Kafka Producer Configuration
# =====================================================

KAFKA_ACKS = "all"

KAFKA_RETRIES = 5

KAFKA_LINGER_MS = 10

KAFKA_BATCH_SIZE = 32768

KAFKA_COMPRESSION = "gzip"

KAFKA_MAX_REQUEST_SIZE = 10485760

KAFKA_REQUEST_TIMEOUT = 30000

KAFKA_DELIVERY_TIMEOUT = 120000


# =====================================================
# Pipeline Configuration
# =====================================================

PIPELINE_VERSION = "1.0.0"

SCHEMA_VERSION = "1.0.0"

CONSUMER_VERSION = "1.0.0"

ENVIRONMENT = "production"


# =====================================================
# Model Configuration
# =====================================================

MODEL_NAME = "facebook/bart-large-mnli"

MAX_CHUNK_LENGTH = 450

MAX_CLASSIFICATION_CHUNKS = 10

CATEGORIES = [

    "Politics",

    "Business",

    "Technology",

    "Sports",

    "Health",

    "Entertainment",

    "Science",

    "Education",

    "World",

    "Crime"

]