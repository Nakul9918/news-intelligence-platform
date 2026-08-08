"""
Common Keyword Utilities

Reusable keyword extraction functions
using YAKE.
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import re

# =====================================================
# Third Party Libraries
# =====================================================

import yake

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
    "CommonKeyword"
)

# =====================================================
# Configuration
# =====================================================

DEFAULT_LANGUAGE = "en"

MAX_KEYWORDS = 10

NGRAM_SIZE = 3

DEDUPLICATION_THRESHOLD = 0.90

WINDOW_SIZE = 1

REMOVE_NUMBERS = True

MIN_CONTENT_LENGTH = 30

DEFAULT_KEYWORDS = []


# =====================================================
# Normalize Text
# =====================================================

def normalize_text(
    text
):
    """
    Normalize article text before
    keyword extraction.
    """

    if not text:

        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    if REMOVE_NUMBERS:

        text = re.sub(
            r"\d+",
            "",
            text
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
# Create YAKE Extractor
# =====================================================

def build_keyword_extractor():
    """
    Build YAKE keyword extractor.
    """

    return yake.KeywordExtractor(

        lan=DEFAULT_LANGUAGE,

        n=NGRAM_SIZE,

        dedupLim=DEDUPLICATION_THRESHOLD,

        windowsSize=WINDOW_SIZE,

        top=MAX_KEYWORDS,

        features=None,

    )
# =====================================================
# Extract Keywords
# =====================================================

def extract_keywords(
    text
):
    """
    Extract keywords from cleaned article.
    """

    if not has_content(
        text
    ):

        return DEFAULT_KEYWORDS

    text = normalize_text(
        text
    )

    extractor = build_keyword_extractor()

    try:

        keyword_scores = extractor.extract_keywords(
            text
        )

    except Exception as error:

        logger.exception(
            f"Keyword Extraction Failed : {error}"
        )

        return DEFAULT_KEYWORDS

    keywords = []

    seen = set()

    for keyword, score in keyword_scores:

        keyword = normalize_text(
            keyword
        )
        keyword = keyword.strip(
            ".,!?;:-()[]{}\"'"
        )

        if not keyword:

            continue

        if len(keyword.split()) == 1 and len(keyword) < 3:

            continue

        lower_keyword = keyword.lower()

        if lower_keyword in seen:

            continue

        seen.add(
            lower_keyword
        )

        keywords.append(
            keyword
        )

    return keywords


# =====================================================
# Build Result
# =====================================================

def build_result(
    keywords,
    processing_time
):
    """
    Standard keyword result.
    """

    return {

    "keywords": keywords,

    "keyword_count": len(keywords),

    "processing_time": processing_time,

    "model": "yake",

}
# =====================================================
# Health Check
# =====================================================

def keyword_health():
    """
    Display keyword extractor configuration.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Keyword Extractor Health"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
    f"Library             : YAKE"
    )

    logger.info(
        f"Language            : {DEFAULT_LANGUAGE}"
    )

    logger.info(
        f"Max Keywords        : {MAX_KEYWORDS}"
    )

    logger.info(
        f"N-Gram Size         : {NGRAM_SIZE}"
    )

    logger.info(
        f"Dedup Threshold     : {DEDUPLICATION_THRESHOLD}"
    )

    logger.info(
        f"Window Size         : {WINDOW_SIZE}"
    )

    logger.info(
        f"Remove Numbers      : {REMOVE_NUMBERS}"
    )

    logger.info(
        f"Minimum Length      : {MIN_CONTENT_LENGTH}"
    )

    logger.info(LOG_SEPARATOR)


# =====================================================
# Self Test
# =====================================================

if __name__ == "__main__":

    keyword_health()

    sample_text = """
    Virat Kohli scored a brilliant century
    in the IPL final against Punjab Kings.
    Royal Challengers Bengaluru won their
    first IPL title in Ahmedabad.
    """

    extracted_keywords = extract_keywords(
        sample_text
    )

    result = build_result(
        extracted_keywords,
        0.001
    )

    logger.info(LOG_SEPARATOR)

    logger.info("Keyword Extraction Test")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Keywords : {result['keywords']}"
    )

    logger.info(
        f"Count    : {result['keyword_count']}"
    )

    logger.info(
        f"Time     : {result['processing_time']} sec"
    )

    logger.info(LOG_SEPARATOR)

