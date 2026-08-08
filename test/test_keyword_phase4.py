from pprint import pprint

from nlp.keyword_extractor import (
    warmup_model,
    get_spacy_model,
    extract_named_entities,
    extract_noun_chunks,
    build_candidate_pool,
    filter_candidates,
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

nlp = get_spacy_model()

doc = nlp(ARTICLE)

print()

print("=" * 60)
print("NAMED ENTITIES")
print("=" * 60)

pprint(
    extract_named_entities(doc)
)

print()

print("=" * 60)
print("NOUN CHUNKS")
print("=" * 60)

pprint(
    extract_noun_chunks(doc)
)

print()

print("=" * 60)
print("CANDIDATE POOL")
print("=" * 60)

candidates = build_candidate_pool(
    doc
)

pprint(candidates)

print()

print("=" * 60)
print("FILTERED")
print("=" * 60)

pprint(
    filter_candidates(
        candidates
    )
)