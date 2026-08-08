from pprint import pprint

from nlp.embeddings import (
    health_check,
    extract_embedding,
    extract_embeddings_batch,
)

print("=" * 70)
print("EMBEDDING HEALTH CHECK")
print("=" * 70)

pprint(health_check())


print("\n" + "=" * 70)
print("TEST 1 : VALID ARTICLE")
print("=" * 70)

article = """
Apple introduced a new AI-powered MacBook
with improved machine learning performance.
"""

embedding = extract_embedding(article)

print(type(embedding))
print(len(embedding))


print("\n" + "=" * 70)
print("TEST 2 : EMPTY STRING")
print("=" * 70)

print(extract_embedding(""))


print("\n" + "=" * 70)
print("TEST 3 : SHORT TEXT")
print("=" * 70)

print(extract_embedding("Hello"))


print("\n" + "=" * 70)
print("TEST 4 : BATCH")
print("=" * 70)

articles = [

    """
    Apple launched a MacBook.
    """,

    """
    Microsoft announced AI services.
    """,

    """
    Google introduced Gemini AI.
    """

]

embeddings = extract_embeddings_batch(
    articles
)

print(type(embeddings))
print(len(embeddings))

for index, embedding in enumerate(
    embeddings,
    start=1,
):

    print(
        f"Article {index}: {len(embedding)}"
    )


print("\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)