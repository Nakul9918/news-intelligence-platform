from pprint import pprint

from historical_processor import (

    load_batch,

    health_check,

)

print("="*60)
print("HEALTH")
print("="*60)

pprint(health_check())

print()

print("="*60)
print("BATCH")
print("="*60)

articles = load_batch()

print(len(articles))