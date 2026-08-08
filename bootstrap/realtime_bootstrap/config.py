from datetime import datetime

# Aug 1–7, 2026
START_DATE = datetime(2026, 8, 1)

END_DATE = datetime(
    2026,
    8,
    7,
    23,
    59,
    59
)

SOURCES = [
    "Economic Times",
    "The Hindu",
    "Indian Express",
    "Hindustan Times",
]

INGESTION_TYPE = "realtime"

VERSION = "1.0.0"