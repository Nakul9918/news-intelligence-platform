from fastapi import APIRouter, Query

from backend.models.news_model import NewsResponse
from backend.services.search_service import search_articles

router = APIRouter()


@router.get(
    "/search",
    response_model=list[NewsResponse],
    summary="Search News"
)
def search(
    query: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    skip = (page - 1) * limit

    return search_articles(
        query=query,
        skip=skip,
        limit=limit
    )