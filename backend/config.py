import os

from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = os.getenv("DATABASE_NAME")

HISTORICAL_COLLECTION = os.getenv("HISTORICAL_COLLECTION")

REALTIME_COLLECTION = os.getenv("REALTIME_COLLECTION")

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")