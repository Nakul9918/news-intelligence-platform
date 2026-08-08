

"""
=====================================================
News Sentiment Analyzer

Project : News Intelligence Platform
Module  : nlp.sentiment

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
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

# =====================================================
# Module Information
# =====================================================

MODULE_NAME = "Sentiment Analyzer"

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

MODEL_NAME = (
    "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# =====================================================
# Device Configuration
# =====================================================

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

DEVICE_NAME = (
    "GPU"
    if DEVICE == "cuda"
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

PREDICTION_CACHE = {}

CACHE_HITS = 0

CACHE_MISSES = 0

MAX_CACHE_SIZE = 500

# =====================================================
# Validation
# =====================================================

MIN_INPUT_CHARACTERS = 20

MIN_INPUT_WORDS = 3

# =====================================================
# Labels
# =====================================================

LABELS = [

    "Negative",

    "Neutral",

    "Positive",

]

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
            "Loading sentiment tokenizer..."
        )

        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME
        )

        log_info(
            "Sentiment tokenizer loaded."
        )

    return _tokenizer


# =====================================================
# Load Model
# =====================================================

def get_model():
    """
    Load sentiment model only once.
    """

    global _model

    if _model is None:

        log_info(
            "Loading sentiment model..."
        )

        start = time.perf_counter()

        _model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                MODEL_NAME
            )
        )

        _model.to(
            DEVICE
        )

        _model.eval()

        elapsed = round(

            time.perf_counter()
            - start,

            4,

        )

        log_info(

            f"Sentiment model loaded "

            f"in {elapsed} sec."

        )

    return _model


# =====================================================
# Input Validation
# =====================================================

def is_valid_input(
    text: str,
) -> bool:
    """
    Validate input text.
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
    Normalize input text.
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
    Convert text into tensors.
    """

    tokenizer = get_tokenizer()

    return tokenizer(

        text,

        truncation=True,

        padding="longest",

        max_length=512,

        return_tensors="pt",

    )


# =====================================================
# Success Response
# =====================================================

def build_success_response(

    label: str,

    score: float,

) -> dict[str, Any]:
    """
    Standard response.
    """

    return {

        "label": label,

        "score": round(

            score,

            4,

        ),

    }


# =====================================================
# Error Response
# =====================================================

def build_error_response() -> dict[str, Any]:
    """
    Error response.
    """

    return {

        "label": "",

        "score": 0.0,

    }
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
# Predict Sentiment
# =====================================================

def predict_sentiment(
    text: str,
) -> dict[str, Any]:
    """
    Predict article sentiment.
    """

    if not is_valid_input(text):

        update_metrics(
            success=False,
            processing_time=0.0,
        )
        update_performance_metrics(
            0.0
        )

        return build_error_response()

    start = time.perf_counter()

    try:

        text = preprocess_text(text)

        model = get_model()

        inputs = tokenize_text(text)

        inputs = {

            key: value.to(DEVICE)

            for key, value in inputs.items()

        }

        with torch.no_grad():

            outputs = model(**inputs)

        probabilities = torch.softmax(

            outputs.logits,

            dim=1,

        )

        score, prediction = torch.max(

            probabilities,

            dim=1,

        )

        label = LABELS[

            prediction.item()

        ]

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


        return build_success_response(

            label,

            score.item(),

        )

    except Exception:

        logger.exception(

            "Sentiment prediction failed."

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

    return build_error_response()
# =====================================================
# Public API
# =====================================================

def analyze_sentiment(
    text: str,
) -> dict[str, Any]:
    """
    Public API used by the realtime pipeline.
    """

    return predict_sentiment(text)
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

        "model": {

            "name": MODEL_NAME,

            "loaded": _model is not None,

            "device": DEVICE_NAME,

            "labels": len(LABELS),

        },

        "system": system_information(),

    }


# =====================================================
# Public Exports
# =====================================================

__all__ = [

    "warmup_model",

"reset_runtime_metrics",

"reset_cache",

"reset_module",

"module_statistics",

]
# =====================================================
# Performance Metrics
# =====================================================

FASTEST_REQUEST = None

SLOWEST_REQUEST = None


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
# Model Warm-up
# =====================================================

MODEL_LOAD_TIME = None

MODEL_WARMED_UP = False


def warmup_model() -> None:
    """
    Load model before first request.
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

        f"Model warm-up completed in "

        f"{MODEL_LOAD_TIME} sec."

    )


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

    global FASTEST_REQUEST
    global SLOWEST_REQUEST

    TOTAL_REQUESTS = 0

    SUCCESSFUL_REQUESTS = 0

    FAILED_REQUESTS = 0

    TOTAL_PROCESSING_TIME = 0.0

    LAST_REQUEST_TIME = None

    FASTEST_REQUEST = None

    SLOWEST_REQUEST = None

    log_info(
        "Runtime metrics reset."
    )


# =====================================================
# Reset Cache
# =====================================================

def reset_cache() -> None:
    """
    Clear prediction cache.
    """

    global CACHE_HITS
    global CACHE_MISSES

    PREDICTION_CACHE.clear()

    CACHE_HITS = 0

    CACHE_MISSES = 0

    log_info(
        "Prediction cache cleared."
    )


# =====================================================
# Reset Module
# =====================================================

def reset_module() -> None:
    """
    Reset runtime and cache.
    """

    reset_runtime_metrics()

    reset_cache()

    log_info(
        "Module reset completed."
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
            PREDICTION_CACHE
        ),

        "cache_limit": MAX_CACHE_SIZE,

        "cache_hits": CACHE_HITS,

        "cache_misses": CACHE_MISSES,

        "runtime_requests": TOTAL_REQUESTS,

        "successful_requests": SUCCESSFUL_REQUESTS,

        "failed_requests": FAILED_REQUESTS,

    }