from fastapi import FastAPI

from backend.exceptions.handlers import register_exception_handlers

from backend.routes.news import router as news_router
from backend.routes.search import router as search_router
from backend.routes.category import router as category_router
from backend.routes.source import router as source_router
from backend.routes.latest import router as latest_router
from backend.routes.sentiment import router as sentiment_router
from backend.routes.keyword import router as keyword_router
from backend.routes.stats import router as stats_router


app = FastAPI(
    title="News Intelligence API",
    description="""
    REST API for the Intelligent Real-Time News Analytics Platform.

    Features:
    - Historical News
    - Real-time News
    - Full-text Search
    - Category Filtering
    - Source Filtering
    - Sentiment Analysis
    - Keyword Search
    - Statistics Dashboard
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register Global Exception Handlers
register_exception_handlers(app)

# Register Routes
app.include_router(news_router, tags=["Historical News"])
app.include_router(search_router, tags=["Search"])
app.include_router(category_router, tags=["Category"])
app.include_router(source_router, tags=["Source"])
app.include_router(latest_router, tags=["Latest"])
app.include_router(sentiment_router, tags=["Sentiment"])
app.include_router(keyword_router, tags=["Keyword"])
app.include_router(stats_router, tags=["Statistics"])