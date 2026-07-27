from fastapi import APIRouter

from backend.models.stats_model import StatsResponse
from backend.services.stats_service import get_statistics

router = APIRouter()


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Statistics"
)
def statistics():

    return get_statistics()