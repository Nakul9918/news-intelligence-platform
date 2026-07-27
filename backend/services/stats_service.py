from backend.services.database import (
    historical_collection,
    realtime_collection
)

from backend.utils.logger import get_logger

logger = get_logger(__name__)


def get_statistics():

    logger.info("Calculating news statistics")

    historical_count = historical_collection.count_documents({})

    realtime_count = realtime_collection.count_documents({})

    total = historical_count + realtime_count

    logger.info(
        f"Historical={historical_count}, Realtime={realtime_count}, Total={total}"
    )

    return {
        "historical_articles": historical_count,
        "realtime_articles": realtime_count,
        "total_articles": total
    }