"""
Temporal Analytics Engine Test
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from pymongo import MongoClient

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME

def parse_any_timestamp(ts):
    if not ts:
        return None
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)
    if isinstance(ts, str):
        ts_clean = ts.strip()
        try:
            return datetime.fromisoformat(ts_clean.replace(" ", "T"))
        except Exception:
            try:
                from dateutil import parser
                return parser.parse(ts_clean).astimezone(timezone.utc)
            except Exception:
                return None
    return None

def test_engine():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    coll = client[DATABASE_NAME][REALTIME_COLLECTION_NAME]
    
    print("Testing Temporal Analytics Engine on MongoDB collection...")
    print(f"Total documents: {coll.count_documents({})}")
    
    # 1. Fetch sample date range
    dates = []
    for doc in coll.find({}, {"published_date": 1, "created_at": 1, "updated_at": 1}).limit(500):
        dt = parse_any_timestamp(doc.get("published_date")) or parse_any_timestamp(doc.get("created_at")) or parse_any_timestamp(doc.get("updated_at"))
        if dt:
            dates.append(dt)
            
    print(f"Parsed {len(dates)} valid timestamps.")
    if dates:
        min_d = min(dates)
        max_d = max(dates)
        print(f"Min Date: {min_d.isoformat()} | Max Date: {max_d.isoformat()}")

    client.close()

if __name__ == "__main__":
    test_engine()
