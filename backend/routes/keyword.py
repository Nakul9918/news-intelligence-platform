from fastapi import APIRouter, Path, Query

from backend.models.news_model import NewsResponse
from backend.services.historical_service import get_news_by_keyword

router = APIRouter()


@router.get(
    "/keyword/{keyword}",
    response_model=list[NewsResponse],
    summary="Get News by Keyword",
    description="Retrieve historical news articles filtered by keyword."
)
def keyword_news(
    keyword: str = Path(..., description="Keyword to search"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    skip = (page - 1) * limit

    return get_news_by_keyword(
        keyword=keyword,
        skip=skip,
        limit=limit
    )