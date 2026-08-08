from pprint import pprint

from nlp.category_classifier import (
    classify_article,
    health_check,
)

article = """
Apple introduced a new AI-powered MacBook.
Tim Cook announced the launch in California.
"""

print("=" * 60)
print("FIRST CALL")
print("=" * 60)

pprint(
    classify_article(article)
)

print()

print("=" * 60)
print("SECOND CALL")
print("=" * 60)

pprint(
    classify_article(article)
)

print()

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(
    health_check()
)