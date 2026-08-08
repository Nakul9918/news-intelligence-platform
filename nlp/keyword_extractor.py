

"""
=====================================================
News Keyword Extractor

Project : News Intelligence Platform
Module  : nlp.keyword_extractor

Version : 1.0
=====================================================

Author : CDAC Project

Purpose:
Extract important keywords from cleaned news articles
using spaCy and YAKE.
"""

from __future__ import annotations

import logging
import platform
import time

from datetime import datetime
from typing import Any

import spacy
import yake

# =====================================================
# Module Information
# =====================================================

MODULE_NAME = "News Keyword Extractor"

MODULE_VERSION = "2.0"

# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(__name__)

# =====================================================
# Debug
# =====================================================

DEBUG = False

# =====================================================
# Model Configuration
# =====================================================

SPACY_MODEL = "en_core_web_sm"

YAKE_LANGUAGE = "en"

YAKE_MAX_NGRAM = 3

YAKE_DEDUP_THRESHOLD = 0.90

YAKE_DEDUP_FUNCTION = "seqm"

MAX_KEYWORDS = 10

# =====================================================
# Lazy Loaded Models
# =====================================================

_spacy_model = None

_yake_extractor = None

# =====================================================
# Runtime Metrics
# =====================================================

MODULE_START_TIME = time.time()

TOTAL_REQUESTS = 0

SUCCESSFUL_REQUESTS = 0

FAILED_REQUESTS = 0

TOTAL_PROCESSING_TIME = 0.0

LAST_REQUEST_TIME = None

# =====================================================
# Performance Metrics
# =====================================================

FASTEST_REQUEST = None

SLOWEST_REQUEST = None

# =====================================================
# Cache
# =====================================================

KEYWORD_CACHE = {}

CACHE_HITS = 0

CACHE_MISSES = 0

MAX_CACHE_SIZE = 500

# =====================================================
# Warmup
# =====================================================

MODEL_LOAD_TIME = None

MODEL_WARMED_UP = False

# =====================================================
# Validation
# =====================================================

MIN_INPUT_CHARACTERS = 50

MIN_INPUT_WORDS = 10

# =====================================================
# Module Information
# =====================================================

def module_information() -> dict[str, Any]:
    """
    Return module information.
    """

    return {

        "module": MODULE_NAME,

        "version": MODULE_VERSION,

        "spacy_model": SPACY_MODEL,

        "keyword_engine": "YAKE",

        "device": "CPU",

        "debug": DEBUG,

    }

# =====================================================
# Logger Helpers
# =====================================================

def log_debug(message: str) -> None:

    if DEBUG:

        logger.debug(message)


def log_info(message: str) -> None:

    logger.info(message)


def log_warning(message: str) -> None:

    logger.warning(message)


def log_error(message: str) -> None:

    logger.error(message)
# =====================================================
# Load spaCy Model
# =====================================================

def get_spacy_model():
    """
    Load spaCy model only once.
    """

    global _spacy_model

    if _spacy_model is None:

        log_info(
            "Loading spaCy model..."
        )

        _spacy_model = spacy.load(
            SPACY_MODEL
        )

        log_info(
            "spaCy model loaded."
        )

    return _spacy_model


# =====================================================
# Load YAKE Extractor
# =====================================================

def get_yake_extractor():
    """
    Load YAKE extractor only once.
    """

    global _yake_extractor

    if _yake_extractor is None:

        log_info(
            "Loading YAKE extractor..."
        )

        _yake_extractor = yake.KeywordExtractor(

            lan=YAKE_LANGUAGE,

            n=YAKE_MAX_NGRAM,

            dedupLim=YAKE_DEDUP_THRESHOLD,

            dedupFunc=YAKE_DEDUP_FUNCTION,

            top=MAX_KEYWORDS,

        )

        log_info(
            "YAKE extractor loaded."
        )

    return _yake_extractor


# =====================================================
# Warm-up
# =====================================================

def warmup_model() -> None:
    """
    Load NLP resources before first request.
    """

    global MODEL_LOAD_TIME
    global MODEL_WARMED_UP

    if MODEL_WARMED_UP:

        return

    start = time.perf_counter()

    get_spacy_model()

    get_yake_extractor()

    MODEL_LOAD_TIME = round(

        time.perf_counter()
        - start,

        4,

    )

    MODEL_WARMED_UP = True

    log_info(

        f"Keyword Extractor warmed up in "

        f"{MODEL_LOAD_TIME} sec."

    )
# =====================================================
# Input Validation
# =====================================================

def is_valid_input(
    text: str,
) -> bool:
    """
    Validate article before keyword extraction.
    """

    if not text:

        return False

    text = text.strip()

    if len(text) < MIN_INPUT_CHARACTERS:

        return False

    if len(text.split()) < MIN_INPUT_WORDS:

        return False

    return True


# =====================================================
# Text Preprocessing
# =====================================================

def preprocess_text(
    text: str,
) -> str:
    """
    Normalize article text.
    """

    if not text:

        return ""

    text = " ".join(
        text.split()
    )

    return text.strip()


# =====================================================
# Phrase Cleaning
# =====================================================

def clean_phrase(
    phrase: str,
) -> str:
    """
    Clean extracted keyword phrase.
    """

    if not phrase:

        return ""

    phrase = phrase.strip()

    phrase = " ".join(
        phrase.split()
    )

    return phrase


# =====================================================
# Phrase Validation
# =====================================================

MIN_KEYWORD_LENGTH = 2

MAX_KEYWORD_WORDS = 6
STOP_PHRASES = {
    "said",
    "says",
    "today",
    "yesterday",
    "tomorrow",
    "news",
    "the company",
    "this company",
    "the government",
    "this government",
    "officials",
    "authorities",
    "sources",
    "report",
    "statement",
}

def is_valid_phrase(
    phrase: str,
) -> bool:
    """
    Validate extracted phrase.
    """

    if not phrase:

        return False

    phrase = clean_phrase(
        phrase
    )

    if len(phrase) < MIN_KEYWORD_LENGTH:

        return False

    if len(
        phrase.split()
    ) > MAX_KEYWORD_WORDS:

        return False

    if phrase.lower() in STOP_PHRASES:

        return False

    return True
# =====================================================
# Named Entity Configuration
# =====================================================

VALID_ENTITY_TYPES = {

    "PERSON",

    "ORG",

    "PRODUCT",

    "GPE",

    "LOC",

    "EVENT",

    "WORK_OF_ART",

}

# =====================================================
# Named Entity Extraction
# =====================================================

def extract_named_entities(
    doc,
) -> list[str]:
    """
    Extract named entities.
    """

    entities = []

    seen = set()

    for entity in doc.ents:

        if entity.label_ not in VALID_ENTITY_TYPES:

            continue

        phrase = clean_phrase(
            entity.text
        )

        if not is_valid_phrase(
            phrase
        ):

            continue

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        entities.append(
            phrase
        )

    return entities


# =====================================================
# Noun Chunk Extraction
# =====================================================

def extract_noun_chunks(
    doc,
) -> list[str]:
    """
    Extract noun chunks.
    """

    chunks = []

    seen = set()

    for chunk in doc.noun_chunks:

        phrase = clean_phrase(
            chunk.text
        )

        if not is_valid_phrase(
            phrase
        ):

            continue

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        chunks.append(
            phrase
        )

    return chunks


# =====================================================
# Candidate Pool Builder
# =====================================================

def build_candidate_pool(
    doc,
) -> list[str]:
    """
    Build candidate keyword pool.
    """

    candidates = []

    seen = set()

    for phrase in extract_named_entities(
        doc
    ):

        key = phrase.lower()

        seen.add(key)

        candidates.append(
            phrase
        )

    for phrase in extract_noun_chunks(
        doc
    ):

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        candidates.append(
            phrase
        )

    return candidates


# =====================================================
# Candidate Filter
# =====================================================

def filter_candidates(
    candidates: list[str],
) -> list[str]:
    """
    Remove invalid or duplicate candidates.
    """

    cleaned = []

    seen = set()

    for phrase in candidates:

        phrase = clean_phrase(
            phrase
        )

        if not is_valid_phrase(
            phrase
        ):

            continue

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        cleaned.append(
            phrase
        )

    return cleaned
# =====================================================
# YAKE Scoring
# =====================================================

def score_candidates(
    text: str,
) -> dict[str, float]:
    """
    Score candidate phrases using YAKE.
    Lower score means higher importance.
    """

    extractor = get_yake_extractor()

    scores = {}

    try:

        keywords = extractor.extract_keywords(
            text
        )

        for phrase, score in keywords:

            phrase = clean_phrase(
                phrase
            )

            if not is_valid_phrase(
                phrase
            ):

                continue

            scores[
                phrase.lower()
            ] = score

    except Exception:

        logger.exception(
            "YAKE scoring failed."
        )

    return scores


# =====================================================
# Rank Keywords
# =====================================================

def rank_keywords(
    candidates: list[str],
    scores: dict[str, float],
) -> list[str]:
    """
    Rank keyword candidates using YAKE scores.
    """

    ranked = []

    for phrase in candidates:

        score = scores.get(
            phrase.lower(),
            9999.0,
        )

        ranked.append(
            (
                score,
                phrase,
            )
        )

    ranked.sort(
        key=lambda item: item[0]
    )

    return [
        phrase
        for _, phrase in ranked
    ]


# =====================================================
# Remove Overlapping Keywords
# =====================================================

def remove_overlapping_keywords(
    keywords: list[str],
) -> list[str]:
    """
    Remove overlapping keyword phrases.
    """

    final_keywords = []

    seen = set()

    for keyword in keywords:

        keyword_lower = keyword.lower()

        overlap = False

        for existing in seen:

            if (
                keyword_lower in existing
                or
                existing in keyword_lower
            ):

                overlap = True

                break

        if overlap:

            continue

        seen.add(
            keyword_lower
        )

        final_keywords.append(
            keyword
        )

    return final_keywords


# =====================================================
# Final Keyword Selection
# =====================================================

def select_keywords(
    candidates: list[str],
    text: str,
) -> list[str]:
    """
    Select final ranked keywords.
    """

    scores = score_candidates(
        text
    )

    ranked = rank_keywords(
        candidates,
        scores,
    )

    ranked = remove_overlapping_keywords(
        ranked
    )

    return ranked[
        :MAX_KEYWORDS
    ]
# =====================================================
# Keyword Extraction
# =====================================================

def extract_keywords(
    text: str,
) -> list[str]:
    """
    Extract keywords from a news article.
    """

    global CACHE_HITS
    global CACHE_MISSES

    # -------------------------------------------------
    # Input Validation
    # -------------------------------------------------

    if not is_valid_input(text):

        update_metrics(
            success=False,
            processing_time=0.0,
        )

        update_performance_metrics(
            0.0,
        )

        return []

    start = time.perf_counter()

    try:

        # Preprocess
        text = preprocess_text(text)

        # Cache
        cache_key = text.lower()

        if cache_key in KEYWORD_CACHE:

            CACHE_HITS += 1

            processing_time = round(
                time.perf_counter() - start,
                4,
            )

            update_metrics(
                success=True,
                processing_time=processing_time,
            )

            update_performance_metrics(
                processing_time,
            )

            return KEYWORD_CACHE[cache_key]

        CACHE_MISSES += 1

        # NLP
        nlp = get_spacy_model()

        doc = nlp(text)

        candidates = build_candidate_pool(doc)

        candidates = filter_candidates(candidates)

        keywords = select_keywords(
            candidates,
            text,
        )

        # Cache Store
        if len(KEYWORD_CACHE) >= MAX_CACHE_SIZE:

            oldest = next(iter(KEYWORD_CACHE))

            del KEYWORD_CACHE[oldest]

        KEYWORD_CACHE[cache_key] = keywords

        processing_time = round(
            time.perf_counter() - start,
            4,
        )

        update_metrics(
            success=True,
            processing_time=processing_time,
        )

        update_performance_metrics(
            processing_time,
        )

        return keywords

    except Exception:

        logger.exception(
            "Keyword extraction failed."
        )

        processing_time = round(
            time.perf_counter() - start,
            4,
        )

        update_metrics(
            success=False,
            processing_time=processing_time,
        )

        update_performance_metrics(
            processing_time,
        )

        return []

# =====================================================
# Runtime Metrics
# =====================================================

def update_metrics(
    success: bool,
    processing_time: float,
) -> None:
    """
    Update runtime statistics.
    """

    global TOTAL_REQUESTS
    global SUCCESSFUL_REQUESTS
    global FAILED_REQUESTS
    global TOTAL_PROCESSING_TIME
    global LAST_REQUEST_TIME

    TOTAL_REQUESTS += 1

    if success:

        SUCCESSFUL_REQUESTS += 1

    else:

        FAILED_REQUESTS += 1

    TOTAL_PROCESSING_TIME += processing_time

    LAST_REQUEST_TIME = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
# =====================================================
# Performance Metrics
# =====================================================

def update_performance_metrics(
    processing_time: float,
) -> None:
    """
    Update performance statistics.
    """

    global FASTEST_REQUEST
    global SLOWEST_REQUEST

    if FASTEST_REQUEST is None:

        FASTEST_REQUEST = processing_time

    elif processing_time < FASTEST_REQUEST:

        FASTEST_REQUEST = processing_time

    if SLOWEST_REQUEST is None:

        SLOWEST_REQUEST = processing_time

    elif processing_time > SLOWEST_REQUEST:

        SLOWEST_REQUEST = processing_time
# =====================================================
# Batch Keyword Extraction
# =====================================================

def batch_extract_keywords(
    articles: list[str],
) -> list[list[str]]:
    """
    Extract keywords from multiple articles.
    """

    results = []

    for article in articles:

        keywords = extract_keywords(
            article
        )

        results.append(
            keywords
        )

    return results
# =====================================================
# Runtime Statistics
# =====================================================

def runtime_statistics() -> dict[str, Any]:
    """
    Return runtime statistics.
    """

    average = 0.0

    if TOTAL_REQUESTS > 0:

        average = round(

            TOTAL_PROCESSING_TIME
            / TOTAL_REQUESTS,

            4,

        )

    return {

        "total_requests": TOTAL_REQUESTS,

        "successful_requests": SUCCESSFUL_REQUESTS,

        "failed_requests": FAILED_REQUESTS,

        "average_processing_time": average,

        "last_request": LAST_REQUEST_TIME,

    }
# =====================================================
# Performance Statistics
# =====================================================

def performance_statistics() -> dict[str, Any]:
    """
    Return performance statistics.
    """

    success_rate = 0.0

    failure_rate = 0.0

    if TOTAL_REQUESTS > 0:

        success_rate = round(

            SUCCESSFUL_REQUESTS
            / TOTAL_REQUESTS,

            4,

        )

        failure_rate = round(

            FAILED_REQUESTS
            / TOTAL_REQUESTS,

            4,

        )

    return {

        "fastest_request": FASTEST_REQUEST,

        "slowest_request": SLOWEST_REQUEST,

        "success_rate": success_rate,

        "failure_rate": failure_rate,

        "uptime_seconds": round(

            time.time()
            - MODULE_START_TIME,

            2,

        ),

    }
# =====================================================
# Module Statistics
# =====================================================

def module_statistics() -> dict[str, Any]:
    """
    Return module statistics.
    """

    return {

        "module": MODULE_NAME,

        "version": MODULE_VERSION,

        "model_loaded": (

            _spacy_model is not None

            and

            _yake_extractor is not None

        ),

        "model_warmed_up": MODEL_WARMED_UP,

        "model_load_time": MODEL_LOAD_TIME,

        "cache_entries": len(
            KEYWORD_CACHE
        ),

        "cache_limit": MAX_CACHE_SIZE,

        "cache_hits": CACHE_HITS,

        "cache_misses": CACHE_MISSES,

        "runtime_requests": TOTAL_REQUESTS,

        "successful_requests": SUCCESSFUL_REQUESTS,

        "failed_requests": FAILED_REQUESTS,

    }
# =====================================================
# System Information
# =====================================================

def system_information() -> dict[str, Any]:
    """
    Return system information.
    """

    return {

        "platform": platform.system(),

        "platform_release": platform.release(),

        "python": platform.python_version(),

        "spacy": spacy.__version__,

        "yake": yake.__version__,

    }
# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Return module health.
    """

    return {

        "status": "healthy",

        "module": module_information(),

        "statistics": module_statistics(),

        "runtime": runtime_statistics(),

        "performance": performance_statistics(),

        "system": system_information(),

    }
# =====================================================
# Reset Module
# =====================================================

def reset_module() -> None:
    """
    Reset runtime statistics and cache.
    """

    global TOTAL_REQUESTS
    global SUCCESSFUL_REQUESTS
    global FAILED_REQUESTS
    global TOTAL_PROCESSING_TIME
    global LAST_REQUEST_TIME

    global FASTEST_REQUEST
    global SLOWEST_REQUEST

    global CACHE_HITS
    global CACHE_MISSES

    KEYWORD_CACHE.clear()

    TOTAL_REQUESTS = 0
    SUCCESSFUL_REQUESTS = 0
    FAILED_REQUESTS = 0
    TOTAL_PROCESSING_TIME = 0.0
    LAST_REQUEST_TIME = None

    FASTEST_REQUEST = None
    SLOWEST_REQUEST = None

    CACHE_HITS = 0
    CACHE_MISSES = 0
# =====================================================
# Public Exports
# =====================================================
__all__ = [

    "warmup_model",

    "extract_keywords",

    "batch_extract_keywords",

    "runtime_statistics",

    "performance_statistics",

    "module_statistics",

    "health_check",

    "reset_module",

]