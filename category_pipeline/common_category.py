"""
Common Category Utilities

Reusable news category classification
functions.
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
    "CommonCategory"
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

CATEGORY_LABELS = [

    "Politics",

    "Business",

    "Sports",

    "Technology",

    "Entertainment",

    "Health",

    "Science",

    "World",
    "Crime"
"Education",
"Environment",
"Finance",

]

# =====================================================
# Load Category Model
# =====================================================

logger.info(LOG_SEPARATOR)

logger.info(
    "Loading Category Model..."
)

logger.info(LOG_SEPARATOR)

CATEGORY_MODEL = pipeline(

    task="zero-shot-classification",

    model=MODEL_NAME,

)

logger.info(
    "Category Model Loaded Successfully."
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
    category classification.
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
# Predict Category
# =====================================================

def predict_category(
    text
):
    """
    Predict article category.
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
    # normalize once and truncate to model input limit
    text = text[:4000]

    try:

        prediction = CATEGORY_MODEL(

            text,

            CATEGORY_LABELS,

            truncation=True,

            max_length=512,

        )

    except Exception as error:

        logger.exception(
            f"Category Prediction Failed : {error}"
        )

        return {

            "label": DEFAULT_LABEL,

            "score": DEFAULT_SCORE,

            "model": MODEL_NAME,

        }

    label = prediction.get(
        "labels",
        [DEFAULT_LABEL]
    )[0]

    score = round(
        float(
            prediction.get(
                "scores",
                [DEFAULT_SCORE]
            )[0]
        ),
        4
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
    category
):
    """
    Build standard category result.
    """

    return {

        "label": category.get(
            "label",
            DEFAULT_LABEL
        ),

        "score": category.get(
            "score",
            DEFAULT_SCORE
        ),

        "model": category.get(
            "model",
            MODEL_NAME
        ),

    }


# =====================================================
# Health Check
# =====================================================

def category_health():
    """
    Display category model information.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Category Model Health"
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
        f"Categories         : {len(CATEGORY_LABELS)}"
    )

    logger.info(LOG_SEPARATOR)

    for category in CATEGORY_LABELS:

        logger.info(
            f" - {category}"
        )

    logger.info(LOG_SEPARATOR)


# =====================================================
# Self Test
# =====================================================

if __name__ == "__main__":

    category_health()

    sample_text = """
    Virat Kohli scored a brilliant
    century during the IPL final and
    Royal Challengers Bengaluru won
    their first championship.
    """

    category = predict_category(
        sample_text
    )

    result = build_result(
        category
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Category Test"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Category : {result['label']}"
    )

    logger.info(
        f"Score    : {result['score']}"
    )

    logger.info(
        f"Model    : {result['model']}"
    )

    logger.info(LOG_SEPARATOR)