from pprint import pprint

from nlp.category_classifier import (

    classify_article,

    health_check,

)

article = """
Apple introduced a new AI-powered MacBook.
Tim Cook announced the launch.
"""

print("=" * 60)
print("ARTICLE 1")
print("=" * 60)

classify_article(article)

print("=" * 60)
print("ARTICLE 2")
print("=" * 60)

classify_article(article)

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(
    health_check()
)