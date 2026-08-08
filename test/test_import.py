from pprint import pprint

from nlp.category_classifier import classify_articles_batch

articles = [

    """
    Apple launched a new AI-powered MacBook.
    Tim Cook announced the launch.
    """,

    """
    Microsoft announced a partnership with OpenAI.
    """,

    "",

    "Hello",

    """
    Google introduced Gemini AI.
    Sundar Pichai presented new features.
    """

]

result = classify_articles_batch(
    articles
)

print("=" * 60)
print("BATCH RESULT")
print("=" * 60)

pprint(result)

print()

print("Processed :", result["processed"])
print("Failed    :", result["failed"])
print("Total     :", result["total_articles"])