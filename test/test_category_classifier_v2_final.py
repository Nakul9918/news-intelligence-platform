from pprint import pprint

from nlp.category_classifier import (
    classify_article,
    classify_articles_batch,
    health_check,
)

article = """
Apple has introduced a new AI-powered MacBook with improved performance.
The company announced new machine learning features during its annual event.
"""

print("=" * 60)
print("SINGLE ARTICLE")
print("=" * 60)

result = classify_article(article)
pprint(result)

print()

print("=" * 60)
print("CACHE TEST")
print("=" * 60)

result = classify_article(article)
pprint(result)

print()

print("=" * 60)
print("INVALID INPUT")
print("=" * 60)

result = classify_article("")
pprint(result)

print()

print("=" * 60)
print("HIGH THRESHOLD")
print("=" * 60)

result = classify_article(article, 0.99)
pprint(result)

print()

print("=" * 60)
print("BATCH TEST")
print("=" * 60)

batch = classify_articles_batch([
    article,
    article,
    "",
])

pprint(batch)

print()

print("=" * 60)
print("HEALTH CHECK")
print("=" * 60)

pprint(health_check())