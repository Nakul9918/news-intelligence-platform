def serialize_article(article):

    if article:
        article["id"] = str(article.pop("_id"))

    return article


def serialize_articles(articles):

    return [serialize_article(article) for article in articles]