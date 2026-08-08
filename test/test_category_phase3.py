from pprint import pprint

from nlp.category_classifier import classify_article

articles = [

    """
    Apple announced a new AI chip for future MacBooks
    with improved machine learning performance.
    """,

    """
    The Indian cricket team defeated Australia
    by 6 wickets in the final match.
    """,

    """
    Parliament passed the new education bill
    after a lengthy discussion.
    """,

    """
    Scientists discovered a new exoplanet
    that may support life.
    """,
]

for article in articles:

    print("-" * 70)

    pprint(
        classify_article(article)
    )