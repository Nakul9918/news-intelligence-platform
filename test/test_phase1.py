from nlp.keyword_extractor import (
    nlp,
    yake_extractor,
    clean_phrase,
)

print(type(nlp))
print(type(yake_extractor))

print(clean_phrase("the advanced AI-powered MacBook featuring"))
