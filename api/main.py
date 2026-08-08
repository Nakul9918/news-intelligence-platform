"""
FastAPI Main Application
"""

from fastapi import FastAPI

from api.routes import router


app = FastAPI(

    title="News Intelligence Platform API",

    version="1.0.0",

    description="Realtime News Intelligence Platform"

)

app.include_router(router)