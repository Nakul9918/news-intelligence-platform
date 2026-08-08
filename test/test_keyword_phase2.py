from nlp.keyword_extractor import *

text = """
Apple introduced a new AI-powered MacBook
featuring an advanced Neural Engine
for machine learning workloads.
"""

doc = nlp(text)

print(extract_named_entities(doc))
print()

print(extract_noun_chunks(doc))
print()

print(filter_candidates(build_candidate_pool(doc)))