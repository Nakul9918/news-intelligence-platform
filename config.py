# =====================================================
# MongoDB Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "news_db"

# Main collection used by the complete pipeline
COLLECTION_NAME = "historical_articles"


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

# Collect only these years
ALLOWED_YEARS = [
    "2024",
    "2025",
    "2026"
]

# Maximum articles to collect from each month
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

# Number of documents processed in one batch
PROCESS_BATCH_SIZE = 5


# =====================================================
# Collections to Process
# =====================================================

# We are using a single unified collection for the
# complete NLP pipeline.

COLLECTIONS = [
    "historical_articles"
]