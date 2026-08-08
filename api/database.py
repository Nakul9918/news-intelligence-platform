"""
MongoDB Connection
"""

from pymongo import MongoClient

from api.config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION,
    HISTORICAL_COLLECTION
)

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

realtime_collection = db[REALTIME_COLLECTION]

historical_collection = db[HISTORICAL_COLLECTION]