from pprint import pprint

from nlp.keyword_extractor import (
    warmup_model,
    get_spacy_model,
    build_candidate_pool,
    filter_candidates,
    select_keywords,
)

ARTICLE = """
Apple introduced the new AI-powered MacBook Pro during WWDC 2026
in California. The company announced better battery life,
faster processors and improved iCloud integration.
"""

warmup_model()

nlp = get_spacy_model()

doc = nlp(ARTICLE)

candidates = build_candidate_pool(doc)

candidates = filter_candidates(candidates)

print("=" * 60)
print("FINAL KEYWORDS")
print("=" * 60)

pprint(
    select_keywords(
        candidates,
        ARTICLE,
    )
)