from pprint import pprint

from nlp.keyword_extractor import *

ARTICLE = """
Apple introduced the new AI-powered MacBook Pro during WWDC.
The company announced better battery life,
faster processors and improved iCloud integration.
"""

print("=" * 60)
print("WARMUP")
print("=" * 60)

warmup_model()

print()

print("=" * 60)
print("EXTRACTION")
print("=" * 60)

pprint(extract_keywords(ARTICLE))

print()

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(health_check())

print()

print("=" * 60)
print("RESET")
print("=" * 60)

reset_module()

pprint(module_statistics())

print()

print("All tests completed successfully.")