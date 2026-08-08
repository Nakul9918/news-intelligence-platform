"""
Bootstrap Configuration

Contains all bootstrap-specific configuration.
"""

from datetime import datetime

# =====================================================
# Bootstrap Date Range
# =====================================================

BOOTSTRAP_START_DATE = datetime(
    2026,
    5,
    1
)

BOOTSTRAP_END_DATE = datetime(
    2026,
    6,
    6,
    23,
    59,
    59
)

# =====================================================
# Bootstrap Sources
# =====================================================

BOOTSTRAP_SOURCES = [

    "Economic Times",

    "The Hindu",

    "Indian Express",

    "Hindustan Times",

]

# =====================================================
# Logging
# =====================================================

LOG_SEPARATOR = "=" * 70

SMALL_SEPARATOR = "-" * 70

# =====================================================
# Bootstrap Version
# =====================================================

BOOTSTRAP_VERSION = "1.0.0"

COLLECTOR_VERSION = "1.0.0"