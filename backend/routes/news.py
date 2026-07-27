from fastapi import APIRouter, Query

from backend.models.news_model import NewsResponse
from backend.services.historical_service import (
    get_all_news,
    get_news_by_id,
)

router = APIRouter()


@router.get(
    "/news",
    response_model=list[NewsResponse],
    summary="Get Historical News"
)
def news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    skip = (page - 1) * limit

    return get_all_news(
        skip=skip,
        limit=limit
    )


@router.get(
    "/news/{news_id}",
    response_model=NewsResponse,
    summary="Get Historical News by ID"
)
def get_news(news_id: str):
    return get_news_by_id(news_id)