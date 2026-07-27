from fastapi import APIRouter, Path, Query

from backend.models.news_model import NewsResponse
from backend.services.historical_service import get_news_by_source

router = APIRouter()


@router.get(
    "/source/{source}",
    response_model=list[NewsResponse],
    summary="Get News by Source",
    description="Retrieve historical news articles filtered by source."
)
def source_news(
    source: str = Path(..., description="News source"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    skip = (page - 1) * limit

    return get_news_by_source(
        source=source,
        skip=skip,
        limit=limit
    )