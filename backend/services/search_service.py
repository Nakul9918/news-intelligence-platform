"""
Search Service

Current:
    Uses MongoDB Full Text Search.

Future:
    Can be replaced by Elasticsearch
    without changing any route code.
"""

from backend.services.historical_service import search_news


def search_articles(query, skip=0, limit=20):
    """
    Search historical news articles.

    Parameters
    ----------
    query : str
        Search keyword.

    skip : int
        Number of records to skip.

    limit : int
        Maximum number of records.

    Returns
    -------
    list
        Matching historical articles.
    """

    return search_news(
        query=query,
        skip=skip,
        limit=limit
    )