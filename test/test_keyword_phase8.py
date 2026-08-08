from pprint import pprint

from nlp.keyword_extractor import (
    warmup_model,
    extract_keywords,
    runtime_statistics,
    performance_statistics,
    module_statistics,
)

ARTICLE = """
Apple introduced the new AI-powered MacBook Pro during WWDC 2026.
The company announced better battery life,
faster processors and improved iCloud integration.
"""

warmup_model()

extract_keywords(ARTICLE)

print("=" * 60)
print("RUNTIME")
print("=" * 60)

pprint(runtime_statistics())

print()

print("=" * 60)
print("PERFORMANCE")
print("=" * 60)

pprint(performance_statistics())

print()

print("=" * 60)
print("MODULE")
print("=" * 60)

pprint(module_statistics())