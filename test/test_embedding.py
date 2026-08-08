from nlp.embeddings import generate_embedding

text = """
India launches a new AI policy to boost innovation
and strengthen its technology sector.
"""

embedding = generate_embedding(text)

print("Vector Length :", len(embedding))
print("First 10 Values:")
print(embedding[:10])