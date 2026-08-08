from pymongo import MongoClient
from collections import Counter

client = MongoClient("mongodb://localhost:27017")
collection = client["news_db"]["realtime_articles"]

sources = Counter()
ingestion = Counter()
stages = Counter()

total = 0

for doc in collection.find({}, {
    "source": 1,
    "ingestion_type": 1,
    "last_pipeline_stage": 1
}):
    total += 1

    source = doc.get("source")

    if isinstance(source, dict):
        sources[source.get("name")] += 1
    else:
        sources[str(source)] += 1

    ingestion[doc.get("ingestion_type")] += 1
    stages[doc.get("last_pipeline_stage")] += 1

print("TOTAL:", total)
print("SOURCES:", sources)
print("INGESTION:", ingestion)
print("STAGES:", stages)
