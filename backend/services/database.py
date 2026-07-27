from pymongo import MongoClient

from backend.config import (
    DATABASE_NAME,
    HISTORICAL_COLLECTION,
    MONGO_URI,
    REALTIME_COLLECTION,
)

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

historical_collection = db[HISTORICAL_COLLECTION]

realtime_collection = db[REALTIME_COLLECTION]