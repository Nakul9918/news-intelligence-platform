from pprint import pprint

from historical_processor import (

    health_check,

    process_batch,

)

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(
    health_check()
)

print()

print("=" * 60)
print("PROCESS BATCH")
print("=" * 60)

process_batch()

print()

print("=" * 60)
print("HEALTH AFTER")
print("=" * 60)

pprint(
    health_check()
)