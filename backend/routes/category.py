from fastapi import APIRouter, Path, Query

from backend.models.news_model import NewsResponse
from backend.services.historical_service import get_news_by_category

router = APIRouter()


@router.get(
    "/category/{category}",
    response_model=list[NewsResponse],
    summary="Get News by Category",
    description="Retrieve historical news articles filtered by category."
)
def category_news(
    category: str = Path(..., description="News category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of records per page")
):

    skip = (page - 1) * limit

    return get_news_by_category(
        category=category,
        skip=skip,
        limit=limit
    )