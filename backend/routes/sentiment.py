from fastapi import APIRouter, Path, Query

from backend.models.news_model import NewsResponse
from backend.services.historical_service import get_news_by_sentiment

router = APIRouter()


@router.get(
    "/sentiment/{sentiment}",
    response_model=list[NewsResponse],
    summary="Get News by Sentiment",
    description="Retrieve historical news articles filtered by sentiment."
)
def sentiment_news(
    sentiment: str = Path(..., description="Sentiment value"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):

    skip = (page - 1) * limit

    return get_news_by_sentiment(
        sentiment=sentiment,
        skip=skip,
        limit=limit
    )