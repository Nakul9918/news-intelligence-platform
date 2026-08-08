


"""
=====================================================
News Summarizer

Project : News Intelligence Platform
Module  : nlp.summarizer

Version : 2.0
=====================================================
"""

from __future__ import annotations

import logging
import platform
import time

from datetime import datetime
from typing import Any

import torch

from transformers import (
    BartForConditionalGeneration,
    BartTokenizer,
)

# =====================================================
# Module Information
# =====================================================

MODULE_NAME = "News Summarizer"

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

MODEL_NAME = "facebook/bart-large-cnn"

# =====================================================
# Summary Configuration
# =====================================================

MAX_INPUT_LENGTH = 1024

MIN_SUMMARY_LENGTH = 30

MAX_SUMMARY_LENGTH = 150

NUM_BEAMS = 4

LENGTH_PENALTY = 2.0

EARLY_STOPPING = True

# =====================================================
# Device Configuration
# =====================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

DEVICE_NAME = (
    "GPU"
    if DEVICE.type == "cuda"
    else "CPU"
)

# =====================================================
# Lazy Model
# =====================================================

_model = None

_tokenizer = None

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

SUMMARY_CACHE = {}

CACHE_HITS = 0

CACHE_MISSES = 0

MAX_CACHE_SIZE = 500

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

        "model": MODEL_NAME,

        "device": DEVICE_NAME,

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
# Load Tokenizer
# =====================================================

def get_tokenizer():
    """
    Load tokenizer only once.
    """

    global _tokenizer

    if _tokenizer is None:

        log_info(
            "Loading summarizer tokenizer..."
        )

        _tokenizer = BartTokenizer.from_pretrained(
            MODEL_NAME
        )

        log_info(
            "Summarizer tokenizer loaded."
        )

    return _tokenizer


# =====================================================
# Load Model
# =====================================================

def get_model():
    """
    Load model only once.
    """

    global _model

    if _model is None:

        log_info(
            "Loading summarizer model..."
        )

        _model = BartForConditionalGeneration.from_pretrained(
            MODEL_NAME
        )

        _model.to(DEVICE)

        _model.eval()

        log_info(
            "Summarizer model loaded."
        )

    return _model
# =====================================================
# Input Validation
# =====================================================

def is_valid_input(
    text: str,
) -> bool:
    """
    Validate article before summarization.
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
# Tokenization
# =====================================================

def tokenize_text(
    text: str,
):
    """
    Convert article into tensors.
    """

    tokenizer = get_tokenizer()

    return tokenizer(

        text,

        max_length=MAX_INPUT_LENGTH,

        truncation=True,

        padding="longest",

        return_tensors="pt",

    )
# =====================================================
# Cache
# =====================================================

def get_cached_summary(
    text: str,
) -> str | None:
    """
    Return cached summary if available.
    """

    global CACHE_HITS
    global CACHE_MISSES

    summary = SUMMARY_CACHE.get(text)

    if summary is None:

        CACHE_MISSES += 1

        return None

    CACHE_HITS += 1

    return summary


def store_summary(
    text: str,
    summary: str,
) -> None:
    """
    Store summary in cache.
    """

    if len(SUMMARY_CACHE) >= MAX_CACHE_SIZE:

        SUMMARY_CACHE.pop(
            next(iter(SUMMARY_CACHE))
        )

    SUMMARY_CACHE[text] = summary


def clear_summary_cache() -> None:
    """
    Clear summary cache.
    """

    global CACHE_HITS
    global CACHE_MISSES

    SUMMARY_CACHE.clear()

    CACHE_HITS = 0

    CACHE_MISSES = 0
# =====================================================
# Update Runtime Metrics
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
# Update Performance Metrics
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
# Generate Summary
# =====================================================

def generate_summary(
    text: str,
    min_length: int = MIN_SUMMARY_LENGTH,
    max_length: int = MAX_SUMMARY_LENGTH,
) -> str:
    """
    Generate article summary.
    """

    if not is_valid_input(text):

        update_metrics(
            success=False,
            processing_time=0.0,
        )

        update_performance_metrics(
            0.0,
        )

        return ""

    start = time.perf_counter()

    try:

        text = preprocess_text(text)
        cached = get_cached_summary(text)

        if cached is not None:

            return cached

        model = get_model()

        tokenizer = get_tokenizer()

        inputs = tokenize_text(text)

        inputs = {

            key: value.to(DEVICE)

            for key, value in inputs.items()

        }

        with torch.no_grad():

            summary_ids = model.generate(

                inputs["input_ids"],

                attention_mask=inputs[
                    "attention_mask"
                ],

                max_length=max_length,

                min_length=min_length,

                num_beams=NUM_BEAMS,

                length_penalty=LENGTH_PENALTY,

                early_stopping=EARLY_STOPPING,

            )

        summary = tokenizer.decode(

            summary_ids[0],

            skip_special_tokens=True,

            clean_up_tokenization_spaces=True,

        ).strip()

        processing_time = round(

            time.perf_counter()
            - start,

            4,

        )

        update_metrics(

            success=True,

            processing_time=processing_time,

        )

        update_performance_metrics(

            processing_time,

        )
        store_summary(
        text,
        summary,
)

        return summary

    except Exception:

        logger.exception(

            "Failed to generate summary."

        )

        processing_time = round(

            time.perf_counter()
            - start,

            4,

        )

        update_metrics(

            success=False,

            processing_time=processing_time,

        )

        update_performance_metrics(

            processing_time,

        )

        return ""
# =====================================================
# Batch Summarization
# =====================================================

def generate_summaries(
    articles: list[str],
    min_length: int = MIN_SUMMARY_LENGTH,
    max_length: int = MAX_SUMMARY_LENGTH,
) -> list[str]:
    """
    Generate summaries for multiple articles.

    Parameters
    ----------
    articles : list[str]

    Returns
    -------
    list[str]
    """

    summaries = []

    if not articles:

        return summaries

    for article in articles:

        summary = generate_summary(

            article,

            min_length=min_length,

            max_length=max_length,

        )

        summaries.append(summary)

    return summaries
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
# Reset Runtime Metrics
# =====================================================

def reset_runtime_metrics() -> None:
    """
    Reset runtime statistics.
    """

    global TOTAL_REQUESTS
    global SUCCESSFUL_REQUESTS
    global FAILED_REQUESTS
    global TOTAL_PROCESSING_TIME
    global LAST_REQUEST_TIME

    TOTAL_REQUESTS = 0

    SUCCESSFUL_REQUESTS = 0

    FAILED_REQUESTS = 0

    TOTAL_PROCESSING_TIME = 0.0

    LAST_REQUEST_TIME = None

# =====================================================
# Reset Performance Metrics
# =====================================================

def reset_performance_metrics() -> None:
    """
    Reset performance statistics.
    """

    global FASTEST_REQUEST
    global SLOWEST_REQUEST

    FASTEST_REQUEST = None

    SLOWEST_REQUEST = None

# =====================================================
# Reset Module
# =====================================================

def reset_module() -> None:
    """
    Reset module runtime data.
    """

    reset_runtime_metrics()

    reset_performance_metrics()

    clear_summary_cache()

# =====================================================
# Warm-up
# =====================================================

MODEL_LOAD_TIME = None

MODEL_WARMED_UP = False
# =====================================================
# Warm-up
# =====================================================

def warmup_model() -> None:
    """
    Load tokenizer and model before first request.
    """

    global MODEL_LOAD_TIME
    global MODEL_WARMED_UP

    if MODEL_WARMED_UP:

        return

    start = time.perf_counter()

    get_tokenizer()

    get_model()

    MODEL_LOAD_TIME = round(

        time.perf_counter()
        - start,

        4,

    )

    MODEL_WARMED_UP = True

    log_info(

        f"Summarizer warmed up in "

        f"{MODEL_LOAD_TIME} sec."

    )

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

        "model_loaded": _model is not None,

        "model_warmed_up": MODEL_WARMED_UP,

        "model_load_time": MODEL_LOAD_TIME,

        "cache_entries": len(
            SUMMARY_CACHE
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

        "torch": torch.__version__,

    }

# =====================================================
# Module Status
# =====================================================

def module_status() -> str:
    """
    Return module health status.
    """

    if _model is None:

        return "not_loaded"

    if not MODEL_WARMED_UP:

        return "warming_up"

    return "healthy"

# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Return module health.
    """

    return {

        "status": module_status(),

        "module": module_information(),

        "statistics": module_statistics(),

        "runtime": runtime_statistics(),

        "performance": performance_statistics(),

        "model": {

            "name": MODEL_NAME,

            "loaded": _model is not None,

            "device": DEVICE_NAME,

        },

        "system": system_information(),

    }


# =====================================================
# Public Exports
# =====================================================
__all__ = [

    "generate_summary",

    "generate_summaries",

    "warmup_model",

    "health_check",

    "module_information",

    "module_statistics",

    "runtime_statistics",

    "performance_statistics",

    "module_status",

    "clear_summary_cache",

    "reset_runtime_metrics",

    "reset_performance_metrics",

    "reset_module",

]