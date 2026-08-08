from nlp.content_cleaner import clean_content

sample = """
Advertisement

Prime Minister Narendra Modi visited Mumbai.

Read More

https://example.com
"""

result = clean_content(sample)

print("Result:")
print(repr(result))