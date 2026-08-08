from pprint import pprint

from nlp.ner import (
    extract_entities,
    extract_entities_batch,
    health_check,
)

print("=" * 70)
print("NER HEALTH CHECK")
print("=" * 70)

pprint(health_check())


print("\n" + "=" * 70)
print("TEST 1 : VALID ARTICLE")
print("=" * 70)

article = """
Apple introduced its latest AI-powered MacBook during an event in California.

Microsoft partnered with OpenAI.

Elon Musk attended the event.
"""

pprint(extract_entities(article))


print("\n" + "=" * 70)
print("TEST 2 : EMPTY STRING")
print("=" * 70)

pprint(extract_entities(""))


print("\n" + "=" * 70)
print("TEST 3 : SHORT TEXT")
print("=" * 70)

pprint(extract_entities("Hello"))


print("\n" + "=" * 70)
print("TEST 4 : BATCH PROCESSING")
print("=" * 70)

articles = [

    """
    Apple launched a new MacBook in California.
    Elon Musk attended.
    """,

    """
    Microsoft announced new AI services.
    Satya Nadella introduced them.
    """,

    """
    Google unveiled Gemini in New York.
    Sundar Pichai presented it.
    """

]

batch = extract_entities_batch(articles)

for index, entities in enumerate(batch, start=1):

    print(f"\nArticle {index}")

    pprint(entities)


print("\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)