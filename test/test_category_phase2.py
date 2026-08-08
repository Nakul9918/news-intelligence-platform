# test_category_phase2.py

from nlp.category_classifier import (
    is_valid_input,
    preprocess_text,
)

article = """
Apple unveiled its latest AI-powered MacBook,
introducing new machine learning features
for developers and businesses.
"""

print(is_valid_input(article))

clean = preprocess_text(article)

print(clean)
print(len(clean))