"""
Common Sentiment Utilities

Reusable sentiment analysis functions.
"""

# =====================================================
# Standard Library
# =====================================================

import logging

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
    "CommonSentiment"
)

# =====================================================
# Configuration
# =====================================================

MODEL_NAME = (
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

DEFAULT_LABEL = ""

DEFAULT_SCORE = 0.0

DEFAULT_LANGUAGE = "en"

MIN_CONTENT_LENGTH = 30

# =====================================================
# Load Sentiment Model
# =====================================================

logger.info(LOG_SEPARATOR)

logger.info(
    "Loading Sentiment Model..."
)

logger.info(LOG_SEPARATOR)

SENTIMENT_MODEL = pipeline(

    task="sentiment-analysis",

    model=MODEL_NAME,

)

logger.info(
    "Sentiment Model Loaded Successfully."
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
    sentiment analysis.
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
# Predict Sentiment
# =====================================================

def predict_sentiment(
    text
):
    """
    Predict article sentiment.
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

        prediction = SENTIMENT_MODEL(
            text,
            truncation=True,
            max_length=512,
        )[0]

    except Exception as error:

        logger.exception(
            f"Sentiment Prediction Failed : {error}"
        )

        return {

            "label": DEFAULT_LABEL,

            "score": DEFAULT_SCORE,

            "model": MODEL_NAME,

        }

    label = prediction.get(
        "label",
        DEFAULT_LABEL,
    ).upper()

    label_map = {
        "POSITIVE": "Positive",
        "NEGATIVE": "Negative",
        "NEUTRAL": "Neutral",
    }

    label = label_map.get(
        label,
        DEFAULT_LABEL,
    )

    score = round(

        float(

            prediction.get(
                "score",
                DEFAULT_SCORE,
            )

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
    sentiment
):
    """
    Build standard sentiment result.
    """

    return {

        "label": sentiment.get(
            "label",
            DEFAULT_LABEL
        ),

        "score": sentiment.get(
            "score",
            DEFAULT_SCORE
        ),

        "model": sentiment.get(
            "model",
            MODEL_NAME
        ),

    }


# =====================================================
# Health Check
# =====================================================

def sentiment_health():
    """
    Display sentiment model information.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Sentiment Model Health"
    )

    logger.info(LOG_SEPARATOR)

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
    f"Library            : Transformers"
)

    logger.info(LOG_SEPARATOR)


# =====================================================
# Self Test
# =====================================================

if __name__ == "__main__":

    sentiment_health()

    sample_text = """
    Virat Kohli played an outstanding match.
    Royal Challengers Bengaluru won the IPL
    final with an excellent performance.
    """

    sentiment = predict_sentiment(
        sample_text
    )

    result = build_result(
        sentiment
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Sentiment Test"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Label : {result['label']}"
    )

    logger.info(
        f"Score : {result['score']}"
    )

    logger.info(
        f"Model : {result['model']}"
    )

    logger.info(LOG_SEPARATOR)