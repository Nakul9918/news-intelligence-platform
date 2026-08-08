from pprint import pprint

from nlp.keyword_extractor import (
    warmup_model,
    batch_extract_keywords,
)

ARTICLES = [

    """
    Apple introduced the new AI-powered MacBook Pro
    with improved battery life.
    """,

    """
    Microsoft announced new Azure AI services
    for enterprise customers.
    """,

    """
    Google released Android 17 with improved
    privacy and AI features.
    """,
]

print("=" * 60)
print("WARMUP")
print("=" * 60)

warmup_model()

print()

print("=" * 60)
print("BATCH KEYWORDS")
print("=" * 60)

results = batch_extract_keywords(
    ARTICLES
)

for index, keywords in enumerate(results, start=1):

    print(f"\nArticle {index}")

    pprint(keywords)