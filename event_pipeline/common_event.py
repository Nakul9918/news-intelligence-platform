"""
Common Event Detection Utilities

Reusable event detection functions.
"""

# =====================================================
# Standard Library
# =====================================================

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
# =====================================================
# Third Party Libraries
# =====================================================

from transformers import pipeline

# =====================================================
# Project Configuration
# =====================================================

from config import (
    LOG_SEPARATOR,
)

# =====================================================
# Logging
# =====================================================

logger = logging.getLogger(
    "CommonEvent"
)

# =====================================================
# Configuration
# =====================================================

MODEL_NAME = (
    "facebook/bart-large-mnli"
)

DEFAULT_LABEL = ""

DEFAULT_SCORE = 0.0

DEFAULT_LANGUAGE = "en"

MIN_CONTENT_LENGTH = 30

EVENT_LABELS = [

    "Election",

    "War",

    "Conflict",

    "Terror Attack",

    "Earthquake",

    "Flood",

    "Cyclone",

    "Pandemic",

    "Government Policy",

    "Parliament",

    "Company Earnings",

    "IPO",

    "Acquisition",

    "Merger",

    "Layoffs",

    "Product Launch",

    "Cyber Attack",

    "Stock Market",

    "Sports Tournament",

    "Award",

    "Crime",

    "Court Judgment",

    "Diplomatic Meeting",

    "Trade Agreement",

]

# =====================================================
# Load Event Model
# =====================================================

logger.info(LOG_SEPARATOR)

logger.info(
    "Loading Event Detection Model..."
)

logger.info(LOG_SEPARATOR)

EVENT_MODEL = pipeline(

    task="zero-shot-classification",

    model=MODEL_NAME,

)

logger.info(
    "Event Detection Model Loaded Successfully."
)

logger.info(LOG_SEPARATOR)

# =====================================================
# Normalize Text
# =====================================================

def normalize_text(
    text
):
    """
    Normalize article text before
    event detection.
    """

    if not text:

        return ""

    text = str(
        text
    )

    text = " ".join(
        text.split()
    )

    return text.strip()


# =====================================================
# Validate Content
# =====================================================

def has_content(
    text
):
    """
    Validate cleaned content.
    """

    if text is None:

        return False

    text = normalize_text(
        text
    )

    if len(text) < MIN_CONTENT_LENGTH:

        return False

    return True


# =====================================================
# Predict Event
# =====================================================

def predict_event(
    text
):
    """
    Predict article event.
    """

    if not has_content(
        text
    ):

        return {

            "label": DEFAULT_LABEL,

            "score": DEFAULT_SCORE,

            "model": MODEL_NAME,

        }

    text = normalize_text(
        text
    )

    try:

        prediction = EVENT_MODEL(

            text,

            EVENT_LABELS,

            truncation=True,

            max_length=512,

        )

    except Exception as error:

        logger.exception(
            f"Event Prediction Failed : {error}"
        )

        return {

            "label": DEFAULT_LABEL,

            "score": DEFAULT_SCORE,

            "model": MODEL_NAME,

        }

    label = prediction["labels"][0]

    score = round(

        float(
            prediction["scores"][0]
        ),

        4,

    )

    return {

        "label": label,

        "score": score,

        "model": MODEL_NAME,

    }

# =====================================================
# Build Result
# =====================================================

def build_result(
    event
):
    """
    Build standard event result.
    """

    return {

        "label": event.get(
            "label",
            DEFAULT_LABEL
        ),

        "score": event.get(
            "score",
            DEFAULT_SCORE
        ),

        "model": event.get(
            "model",
            MODEL_NAME
        ),

    }


# =====================================================
# Health Check
# =====================================================

def event_health():
    """
    Display event model information.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Event Detection Model Health"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Library            : Transformers"
    )

    logger.info(
        f"Model              : {MODEL_NAME}"
    )

    logger.info(
        f"Language           : {DEFAULT_LANGUAGE}"
    )

    logger.info(
        f"Minimum Length     : {MIN_CONTENT_LENGTH}"
    )

    logger.info(
        f"Events             : {len(EVENT_LABELS)}"
    )

    logger.info(LOG_SEPARATOR)

    for event in EVENT_LABELS:

        logger.info(
            f" - {event}"
        )

    logger.info(LOG_SEPARATOR)


# =====================================================
# Self Test
# =====================================================

if __name__ == "__main__":

    event_health()

    sample_text = """
    Microsoft announced that it has
    acquired an AI startup for
    2 billion dollars to strengthen
    its cloud business.
    """

    event = predict_event(
        sample_text
    )

    result = build_result(
        event
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Event Detection Test"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Event : {result['label']}"
    )

    logger.info(
        f"Score : {result['score']}"
    )

    logger.info(
        f"Model : {result['model']}"
    )

    logger.info(LOG_SEPARATOR)