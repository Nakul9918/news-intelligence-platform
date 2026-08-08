from pprint import pprint

from nlp.category_classifier import (
    health_check,
    classify_article,
    classify_articles_batch,
)

print("=" * 60)
print("HEALTH CHECK")
print("=" * 60)

pprint(health_check())

print()

article = """
Apple introduced a new AI-powered MacBook.
Tim Cook announced the launch.
"""

print("=" * 60)
print("SINGLE ARTICLE")
print("=" * 60)

pprint(classify_article(article))

print()

articles = [

    article,

    "Hello",

    "",

]

print("=" * 60)
print("BATCH")
print("=" * 60)

pprint(classify_articles_batch(articles))

print()

print("=" * 60)
print("HEALTH AFTER PROCESSING")
print("=" * 60)

pprint(health_check())


