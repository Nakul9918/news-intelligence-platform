from pprint import pprint

from nlp.keyword_extractor import extract_keywords

article = """
Apple introduced a new AI-powered MacBook
featuring an advanced Neural Engine
for machine learning workloads.

The MacBook provides better battery life
and AI inference.
"""

result = extract_keywords(article)

pprint(result)