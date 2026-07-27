from fastapi import APIRouter, Query

from backend.models.news_model import NewsResponse
from backend.services.historical_service import get_latest_news

router = APIRouter()


@router.get(
    "/latest",
    response_model=list[NewsResponse],
    summary="Get Latest News",
    description="Retrieve the latest historical news articles."
)
def latest_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    skip = (page - 1) * limit

    return get_latest_news(
        skip=skip,
        limit=limit
    )