import urllib.request
import json
from pymongo import MongoClient

print("=== INFRASTRUCTURE AUDIT ===")

# 1. MongoDB
try:
    client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client['news_db']
    count = db['realtime_articles'].count_documents({})
    indexes = list(db['realtime_articles'].list_indexes())
    print(f"[PASS] MongoDB: Connected (DB: news_db, Collection: realtime_articles, Count: {count})")
    print(f"       Indexes: {[idx['name'] for idx in indexes]}")
except Exception as e:
    print(f"[FAIL] MongoDB: {e}")

# 2. Kafka
try:
    from kafka import KafkaAdminClient
    admin = KafkaAdminClient(bootstrap_servers='localhost:9092', request_timeout_ms=2000)
    topics = admin.list_topics()
    print(f"[PASS] Kafka: Broker active on 9092. Topics: {topics}")
except Exception as e:
    print(f"[FAIL] Kafka: {e}")

# 3. Elasticsearch
try:
    req = urllib.request.urlopen('http://localhost:9200', timeout=2)
    es_info = json.loads(req.read().decode('utf-8'))
    print(f"[PASS] Elasticsearch: Active (Version {es_info.get('version', {}).get('number')})")
    
    # Check index mapping & document count
    req_index = urllib.request.urlopen('http://localhost:9200/news_articles/_count', timeout=2)
    count_data = json.loads(req_index.read().decode('utf-8'))
    print(f"       Index 'news_articles' doc count: {count_data.get('count')}")
except Exception as e:
    print(f"[FAIL] Elasticsearch: {e}")

# 4. FastAPI Backend
try:
    req = urllib.request.urlopen('http://localhost:8000/health', timeout=2)
    health = json.loads(req.read().decode('utf-8'))
    print(f"[PASS] FastAPI Server: Listening on port 8000. Health: {health}")
except Exception as e:
    print(f"[FAIL] FastAPI Server: {e}")

# 5. Streamlit Dashboard
try:
    req = urllib.request.urlopen('http://localhost:8501', timeout=2)
    print(f"[PASS] Streamlit Dashboard: Listening on port 8501 (HTTP {req.status})")
except Exception as e:
    print(f"[FAIL] Streamlit Dashboard: {e}")
