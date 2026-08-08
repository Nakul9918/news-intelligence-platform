import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

DATABASE_NAME = os.getenv("DATABASE_NAME", "news_db")

HISTORICAL_COLLECTION = os.getenv(
    "HISTORICAL_COLLECTION",
    "historical_articles"
)

REALTIME_COLLECTION = os.getenv(
    "REALTIME_COLLECTION",
    "realtime_articles"
)

ELASTICSEARCH_URL = os.getenv(
    "ELASTICSEARCH_URL",
    "http://localhost:9200"
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")