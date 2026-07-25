from nlp.ner import extract_entities

text = """
Apple CEO Tim Cook visited India on Monday to announce
a new AI product worth $10 million.
"""

entities = extract_entities(text)

print(entities)