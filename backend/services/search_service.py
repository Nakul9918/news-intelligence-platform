from backend.services.historical_service import search_news


def search_articles(query, skip=0, limit=20):
    """
    Search historical news articles.

    Later this function will be replaced with
    Elasticsearch search without changing routes.
    """

    return search_news(
        query=query,
        skip=skip,
        limit=limit
    )