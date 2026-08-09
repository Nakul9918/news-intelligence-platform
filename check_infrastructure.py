"""
Infrastructure Health Check Helper for start_project.ps1
"""

import sys
import site

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

from pymongo import MongoClient
from kafka import KafkaAdminClient
from elasticsearch import Elasticsearch

def main():
    res = {}
    try:
        m = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
        m.admin.command('ping')
        res["mongo"] = True
    except Exception:
        res["mongo"] = False

    try:
        k = KafkaAdminClient(bootstrap_servers='localhost:9092', request_timeout_ms=2000)
        k.close()
        res["kafka"] = True
    except Exception:
        res["kafka"] = False

    try:
        es = Elasticsearch('http://127.0.0.1:9200')
        res["es"] = es.ping()
        es.close()
    except Exception:
        res["es"] = False

    print(f"MONGO={'OK' if res['mongo'] else 'FAIL'}")
    print(f"KAFKA={'OK' if res['kafka'] else 'FAIL (Direct DB Persistence Fallback Active)'}")
    print(f"ES={'OK' if res['es'] else 'FAIL (Mongo Vector & Keyword Fallback Active)'}")

    # MongoDB is mandatory; Kafka & ES have automatic fallback layers
    if not res["mongo"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

