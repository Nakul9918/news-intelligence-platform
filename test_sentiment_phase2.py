from pprint import pprint

from nlp.sentiment import (

    analyze_sentiment,

    health_check,

    warmup_model,

    module_statistics,

)

article = """
Apple introduced a new AI powered MacBook.
The company expects strong quarterly sales.
"""

print("=" * 60)
print("WARMUP")
print("=" * 60)

warmup_model()

print()

print("=" * 60)
print("SENTIMENT")
print("=" * 60)

pprint(
    analyze_sentiment(article)
)

print()

print("=" * 60)
print("STATISTICS")
print("=" * 60)

pprint(
    module_statistics()
)

print()

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(
    health_check()
)