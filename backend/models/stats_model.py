from pydantic import BaseModel


class StatsResponse(BaseModel):
    historical_articles: int
    realtime_articles: int
    total_articles: int