from nlp.sentiment import (
    is_valid_input,
    preprocess_text,
    tokenize_text,
)

article = """
India's economy showed strong growth this quarter,
with exports increasing and inflation remaining stable.
"""

print(is_valid_input(article))

clean = preprocess_text(article)

print(clean)

tokens = tokenize_text(clean)

print(tokens["input_ids"].shape)