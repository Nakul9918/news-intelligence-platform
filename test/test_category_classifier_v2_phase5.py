from pprint import pprint

from nlp.category_classifier_v2 import (

    classify_article,

    classify_articles_batch,

    health_check,

)

article = """

Apple introduced a new AI-powered MacBook.

Tim Cook announced the launch.

"""

print("=" * 60)
print("FIRST")
print("=" * 60)

pprint(
    classify_article(article)
)

print()

print("=" * 60)
print("SECOND")
print("=" * 60)

pprint(
    classify_article(article)
)

print()

articles = [

    article,

    article,

    "Hello",

]

print("=" * 60)
print("BATCH")
print("=" * 60)

pprint(
    classify_articles_batch(
        articles
    )
)

print()

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(
    health_check()
)