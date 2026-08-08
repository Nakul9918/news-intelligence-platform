from pprint import pprint

from nlp.keyword_extractor import (
    warmup_model,
    extract_keywords,
)

ARTICLE = """
Apple introduced the new AI-powered MacBook Pro during WWDC 2026
in California. The company announced better battery life,
faster processors and improved iCloud integration.
"""

print("=" * 60)
print("WARMUP")
print("=" * 60)

warmup_model()

print()

print("=" * 60)
print("KEYWORDS")
print("=" * 60)

pprint(
    extract_keywords(
        ARTICLE
    )
)