from nlp.keyword_extractor import extract_keywords

text = """
Artificial Intelligence is transforming healthcare,
education and finance.
Machine learning and deep learning are rapidly
changing the software industry.
"""

keywords = extract_keywords(text)

print()

print("Keywords")

print("----------------")

for keyword in keywords:

    print(keyword)