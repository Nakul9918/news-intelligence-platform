# """
# =====================================================
# News Category Classifier
# Project : News Intelligence Platform
# Module  : nlp.category_classifier
# Version : 4.0 (Production)
# =====================================================
# """

# from __future__ import annotations

# import logging
# import time
# from typing import Any

# import torch
# from transformers import pipeline

# # =====================================================
# # Logger
# # =====================================================

# logger = logging.getLogger(__name__)

# # =====================================================
# # Production Configuration
# # =====================================================

# DEBUG_MODE = False

# ENABLE_CONSOLE_LOGS = True

# ENABLE_PERFORMANCE_LOGS = True

# ENABLE_CACHE_LOGS = True

# ENABLE_ERROR_LOGS = True

# ENABLE_BATCH_LOGS = True

# MODULE_NAME = "Category Classifier"

# MODULE_VERSION = "2.0"

# LOG_PREFIX = "[CATEGORY]"


# # =====================================================
# # Logging Helpers
# # =====================================================

# def log_debug(
#     message: str,
# ) -> None:
#     """
#     Debug logger.
#     """

#     if DEBUG_MODE:

#         logger.info(

#             "%s %s",

#             LOG_PREFIX,

#             message,

#         )


# def log_info(
#     message: str,
# ) -> None:
#     """
#     Info logger.
#     """

#     if ENABLE_CONSOLE_LOGS:

#         logger.info(

#             "%s %s",

#             LOG_PREFIX,

#             message,

#         )


# def log_warning(
#     message: str,
# ) -> None:
#     """
#     Warning logger.
#     """

#     logger.warning(

#         "%s %s",

#         LOG_PREFIX,

#         message,

#     )


# def log_error(
#     message: str,
# ) -> None:
#     """
#     Error logger.
#     """

#     if ENABLE_ERROR_LOGS:

#         logger.exception(

#             "%s %s",

#             LOG_PREFIX,

#             message,

#         )


# # =====================================================
# # Module Information
# # =====================================================

# def module_information() -> dict[str, Any]:
#     """
#     Return module information.
#     """

#     return {

#         "module": MODULE_NAME,

#         "version": MODULE_VERSION,

#         "model": MODEL_NAME,

#         "device": DEVICE_NAME,

#         "debug": DEBUG_MODE,

#     }
# # =====================================================
# # Debug
# # =====================================================

# DEBUG = False

# # =====================================================
# # Model Configuration
# # =====================================================

# MODEL_NAME = "facebook/bart-large-mnli"

# # =====================================================
# # Device Configuration
# # =====================================================

# DEVICE = 0 if torch.cuda.is_available() else -1

# DEVICE_NAME = "GPU" if DEVICE == 0 else "CPU"

# # =====================================================
# # Lazy Model
# # =====================================================

# _classifier = None
# # =====================================================
# # Device Configuration
# # =====================================================

# DEVICE = 0 if torch.cuda.is_available() else -1

# DEVICE_NAME = (
#     "GPU"
#     if DEVICE == 0
#     else "CPU"
# )

# logger.info(
#     "Category Classifier Device : %s",
#     DEVICE_NAME,
# )

# # =====================================================
# # Category Labels
# # =====================================================

# CANDIDATE_LABELS = [

#     "Politics and Government",

#     "Business and Finance",

#     "Technology and Artificial Intelligence",

#     "Sports",

#     "Entertainment and Media",

#     "Health and Medicine",

#     "Science and Research",

#     "World News",

#     "Education",

#     "Environment and Climate",

#     "Crime and Law",

# ]

# # =====================================================
# # Label Mapping
# # =====================================================

# CATEGORY_MAPPING = {

#     "Politics and Government":
#         "Politics",

#     "Business and Finance":
#         "Business",

#     "Technology and Artificial Intelligence":
#         "Technology",

#     "Sports":
#         "Sports",

#     "Entertainment and Media":
#         "Entertainment",

#     "Health and Medicine":
#         "Health",

#     "Science and Research":
#         "Science",

#     "World News":
#         "World",

#     "Education":
#         "Education",

#     "Environment and Climate":
#         "Environment",

#     "Crime and Law":
#         "Crime",

# }

# # =====================================================
# # Configuration
# # =====================================================

# DEFAULT_CONFIDENCE_THRESHOLD = 0.40

# TOP_K = 3

# HYPOTHESIS_TEMPLATE = (
#     "This news article is about {}."
# )

# MIN_INPUT_CHARACTERS = 20

# MIN_INPUT_WORDS = 3

# MAX_INPUT_CHARACTERS = 1500

# # =====================================================
# # Runtime Metrics
# # =====================================================

# TOTAL_REQUESTS = 0

# SUCCESSFUL_REQUESTS = 0

# FAILED_REQUESTS = 0

# TOTAL_PROCESSING_TIME = 0.0

# LAST_REQUEST_TIME = None

# def get_classifier():
#     """
#     Load the Hugging Face classifier only once.
#     """

#     global _classifier

#     print("A. Entered get_classifier")

#     if _classifier is None:

#         print("B. _classifier is None")

#         log_info(
#             "Loading category classification model..."
#         )

#         start_time = time.perf_counter()

#         print("C. Before pipeline()")

#         _classifier = pipeline(
#             task="zero-shot-classification",
#             model=MODEL_NAME,
#             device=DEVICE,
#         )

#         print("D. After pipeline()")

#         load_time = round(
#             time.perf_counter() - start_time,
#             4,
#         )

#         print("E. Load time =", load_time)

#         log_info(
#             f"Model loaded successfully in {load_time} sec."
#         )

#     else:

#         print("F. Using existing model")

#     print("G. Returning classifier")

#     return _classifier
# # =====================================================
# # Validation
# # =====================================================

# def is_valid_input(
#     text: str,
# ) -> bool:
#     """
#     Validate input article.
#     """

#     if not isinstance(
#         text,
#         str,
#     ):
#         return False

#     text = text.strip()

#     if not text:
#         return False

#     if len(text) < MIN_INPUT_CHARACTERS:
#         return False

#     if len(text.split()) < MIN_INPUT_WORDS:
#         return False

#     return True


# # =====================================================
# # Text Preprocessing
# # =====================================================

# def preprocess_text(
#     text: str,
# ) -> str:
#     """
#     Clean article text.
#     """

#     text = " ".join(
#         text.split()
#     )

#     if len(text) > MAX_INPUT_CHARACTERS:

#         text = text[
#             :MAX_INPUT_CHARACTERS
#         ]

#     return text.strip()


# # =====================================================
# # Threshold Normalization
# # =====================================================

# def normalize_threshold(
#     threshold: float,
# ) -> float:
#     """
#     Normalize confidence threshold.
#     """

#     if not isinstance(
#         threshold,
#         (int, float),
#     ):

#         logger.warning(
#             "Invalid confidence threshold. Using default."
#         )

#         return DEFAULT_CONFIDENCE_THRESHOLD

#     threshold = float(
#         threshold
#     )

#     if threshold < 0.0:

#         return 0.0

#     if threshold > 1.0:

#         return 1.0

#     return threshold


# # =====================================================
# # Build Top Categories
# # =====================================================

# def build_top_categories(
#     labels: list[str],
#     scores: list[float],
# ) -> list[dict[str, Any]]:
#     """
#     Convert Hugging Face output into a
#     standardized list of top categories.
#     """

#     top_categories = []

#     for label, score in zip(

#         labels[:TOP_K],

#         scores[:TOP_K],

#     ):

#         top_categories.append(

#             {

#                 "label": CATEGORY_MAPPING.get(

#                     label,

#                     label,

#                 ),

#                 "score": round(

#                     float(score),

#                     4,

#                 ),

#             }

#         )

#     return top_categories


# # =====================================================
# # Build Success Response
# # =====================================================

# def build_success_response(

#     category: str,

#     confidence: float,

#     top_categories: list[dict[str, Any]],

#     processing_time: float,

# ) -> dict[str, Any]:
#     """
#     Return standardized success response.
#     """

#     return {

#         "success": True,

#         "category": category,

#         "score": confidence,

#         "top_categories": top_categories,

#         "processing_time": processing_time,

#         "model": MODEL_NAME,

#         "message": "Classification successful.",

#     }


# # =====================================================
# # Build Error Response
# # =====================================================

# def build_error_response(
#     message: str,
# ) -> dict[str, Any]:
#     """
#     Return standardized error response.
#     """

#     return {

#         "success": False,

#         "category": "",

#         "score": 0.0,

#         "top_categories": [],

#         "processing_time": 0.0,

#         "model": MODEL_NAME,

#         "message": message,

#     }
# # =====================================================
# # Runtime Metrics
# # =====================================================
# # =====================================================
# # Update Runtime Metrics
# # =====================================================

# def update_metrics(
#     success: bool,
#     processing_time: float,
# ) -> None:
#     """
#     Update runtime statistics.
#     """

#     global TOTAL_REQUESTS
#     global SUCCESSFUL_REQUESTS
#     global FAILED_REQUESTS
#     global TOTAL_PROCESSING_TIME
#     global LAST_REQUEST_TIME

#     TOTAL_REQUESTS += 1

#     if success:

#         SUCCESSFUL_REQUESTS += 1

#         TOTAL_PROCESSING_TIME += processing_time

#     else:

#         FAILED_REQUESTS += 1

#     LAST_REQUEST_TIME = time.strftime(
#         "%Y-%m-%d %H:%M:%S"
#     )

#     update_performance_metrics(
#         processing_time
#     )
# # =====================================================
# # Runtime Statistics
# # =====================================================

# def runtime_statistics() -> dict[str, Any]:
#     """
#     Return runtime statistics.
#     """

#     average_processing_time = 0.0

#     if SUCCESSFUL_REQUESTS > 0:

#         average_processing_time = round(

#             TOTAL_PROCESSING_TIME
#             / SUCCESSFUL_REQUESTS,

#             4,

#         )

#     return {

#         "total_requests": TOTAL_REQUESTS,

#         "successful_requests": SUCCESSFUL_REQUESTS,

#         "failed_requests": FAILED_REQUESTS,

#         "average_processing_time": average_processing_time,

#         "last_request": LAST_REQUEST_TIME,

#     }

# # =====================================================
# # Prediction Cache
# # =====================================================

# PREDICTION_CACHE: dict[
#     tuple[str, float],
#     dict[str, Any],
# ] = {}

# CACHE_HITS = 0

# CACHE_MISSES = 0

# MAX_CACHE_SIZE = 500


# # =====================================================
# # Build Cache Key
# # =====================================================

# def build_cache_key(
#     text: str,
#     threshold: float,
# ) -> tuple[str, float]:
#     """
#     Build cache key.
#     """

#     return (

#         preprocess_text(text),

#         round(
#             threshold,
#             2,
#         ),

#     )

# # =====================================================
# # Get Cached Prediction
# # =====================================================

# def get_cached_prediction(
#     text: str,
#     threshold: float,
# ) -> dict[str, Any] | None:
#     """
#     Return cached prediction.
#     """

#     global CACHE_HITS
#     global CACHE_MISSES

#     key = build_cache_key(
#         text,
#         threshold,
#     )

#     prediction = PREDICTION_CACHE.get(
#         key,
#     )

#     if prediction is None:

#         CACHE_MISSES += 1

#         if ENABLE_CACHE_LOGS:

#             log_debug(
#                 "Cache MISS"
#             )

#         return None

#     CACHE_HITS += 1

#     if ENABLE_CACHE_LOGS:

#         log_debug(
#             "Cache HIT"
#         )

#     return prediction
# # =====================================================
# # Store Prediction
# # =====================================================

# def cache_prediction(
#     text: str,
#     threshold: float,
#     prediction: dict[str, Any],
# ) -> None:
#     """
#     Store prediction in cache.
#     """

#     if len(
#         PREDICTION_CACHE
#     ) >= MAX_CACHE_SIZE:

#         oldest_key = next(
#             iter(
#                 PREDICTION_CACHE
#             )
#         )

#         del PREDICTION_CACHE[
#             oldest_key
#         ]

#         log_debug(
#             "Old cache removed."
#         )

#     key = build_cache_key(
#         text,
#         threshold,
#     )

#     PREDICTION_CACHE[
#         key
#     ] = prediction

#     if ENABLE_CACHE_LOGS:

#         log_debug(
#             "Prediction cached."
#         )
# # =====================================================
# # Cache Statistics
# # =====================================================

# def cache_statistics() -> dict[str, Any]:
#     """
#     Return cache statistics.
#     """

#     total = CACHE_HITS + CACHE_MISSES

#     hit_rate = 0.0

#     if total > 0:

#         hit_rate = round(

#             CACHE_HITS
#             / total,

#             4,

#         )

#     return {

#         "entries": len(
#             PREDICTION_CACHE
#         ),

#         "hits": CACHE_HITS,

#         "misses": CACHE_MISSES,

#         "hit_rate": hit_rate,

#         "max_size": MAX_CACHE_SIZE,

#     }
# # =====================================================
# # Module Start Time
# # =====================================================

# MODULE_START_TIME = time.time()


# # =====================================================
# # Performance Metrics
# # =====================================================

# FASTEST_REQUEST = None

# SLOWEST_REQUEST = None


# # =====================================================
# # Update Performance Metrics
# # =====================================================

# def update_performance_metrics(
#     processing_time: float,
# ) -> None:
#     """
#     Update fastest and slowest request.
#     """

#     global FASTEST_REQUEST
#     global SLOWEST_REQUEST

#     if processing_time <= 0:
#         return

#     if FASTEST_REQUEST is None:

#         FASTEST_REQUEST = processing_time

#     elif processing_time < FASTEST_REQUEST:

#         FASTEST_REQUEST = processing_time

#     if SLOWEST_REQUEST is None:

#         SLOWEST_REQUEST = processing_time

#     elif processing_time > SLOWEST_REQUEST:

#         SLOWEST_REQUEST = processing_time


# # =====================================================
# # Performance Statistics
# # =====================================================

# def performance_statistics() -> dict[str, Any]:
#     """
#     Return performance statistics.
#     """

#     success_rate = 0.0

#     if TOTAL_REQUESTS > 0:

#         success_rate = round(

#             SUCCESSFUL_REQUESTS /
#             TOTAL_REQUESTS,

#             4,

#         )

#     failure_rate = round(

#         1.0 - success_rate,

#         4,

#     )

#     uptime_seconds = round(

#         time.time()
#         - MODULE_START_TIME,

#         2,

#     )

#     return {

#         "uptime_seconds": uptime_seconds,

#         "fastest_request": FASTEST_REQUEST,

#         "slowest_request": SLOWEST_REQUEST,

#         "success_rate": success_rate,

#         "failure_rate": failure_rate,

#     }
# # =====================================================
# # Model Warm-up
# # =====================================================

# MODEL_LOAD_TIME = None

# MODEL_WARMED_UP = False


# def warmup_model() -> None:
#     """
#     Warm up the model before the first request.
#     """

#     global MODEL_LOAD_TIME
#     global MODEL_WARMED_UP

#     print("1. warmup_model() called")

#     if MODEL_WARMED_UP:
#         print("2. Already warmed")
#         return

#     start = time.perf_counter()

#     print("3. Before get_classifier()")

#     classifier = get_classifier()

#     print("4. After get_classifier()", classifier)

#     MODEL_LOAD_TIME = round(
#         time.perf_counter() - start,
#         4,
#     )

#     MODEL_WARMED_UP = True

#     print("5. Warmup complete")
# # =====================================================
# # Runtime Reset
# # =====================================================

# def reset_runtime_metrics() -> None:
#     """
#     Reset runtime metrics.
#     """

#     global TOTAL_REQUESTS
#     global SUCCESSFUL_REQUESTS
#     global FAILED_REQUESTS
#     global TOTAL_PROCESSING_TIME
#     global LAST_REQUEST_TIME

#     TOTAL_REQUESTS = 0

#     SUCCESSFUL_REQUESTS = 0

#     FAILED_REQUESTS = 0

#     TOTAL_PROCESSING_TIME = 0.0

#     LAST_REQUEST_TIME = None

#     log_info(
#         "Runtime metrics reset."
#     )


# # =====================================================
# # Reset Cache
# # =====================================================

# def reset_cache() -> None:
#     """
#     Reset prediction cache.
#     """

#     clear_cache()

#     log_info(
#         "Cache reset."
#     )


# # =====================================================
# # Reset Module
# # =====================================================

# def reset_module() -> None:
#     """
#     Reset cache and runtime metrics.
#     """

#     reset_runtime_metrics()

#     reset_cache()

#     log_info(
#         "Module reset completed."
#     )


# # =====================================================
# # Module Statistics
# # =====================================================

# def module_statistics() -> dict[str, Any]:
#     """
#     Return module statistics.
#     """

#     return {

#         "module": MODULE_NAME,

#         "version": MODULE_VERSION,

#         "model_loaded": _classifier is not None,

#         "model_warmed_up": MODEL_WARMED_UP,

#         "model_load_time": MODEL_LOAD_TIME,

#         "cache_entries": len(
#             PREDICTION_CACHE
#         ),

#         "cache_limit": MAX_CACHE_SIZE,

#         "runtime_requests": TOTAL_REQUESTS,

#         "successful_requests": SUCCESSFUL_REQUESTS,

#         "failed_requests": FAILED_REQUESTS,

#     }


# # =====================================================
# # Cached Response Builder
# # =====================================================

# def build_cached_response(
#     response: dict[str, Any],
#     lookup_time: float,
# ) -> dict[str, Any]:
#     """
#     Return cached response with cache metadata.
#     """

#     cached = response.copy()

#     cached["cached"] = True

#     cached["cache_lookup_time"] = round(
#         lookup_time,
#         6,
#     )

#     return cached
# # =====================================================
# # Clear Cache
# # =====================================================

# def clear_cache() -> None:
#     """
#     Clear cache.
#     """

#     global CACHE_HITS
#     global CACHE_MISSES

#     PREDICTION_CACHE.clear()

#     CACHE_HITS = 0

#     CACHE_MISSES = 0

#     log_info(
#         "Prediction cache cleared."
#     )
# # =====================================================
# # Health Check
# # =====================================================

# def health_check() -> dict[str, Any]:
#     """
#     Return complete health information.
#     """

#     return {

#         "status": "healthy",

#         "module": module_information(),

#         "statistics": module_statistics(),

#         "model": {

#             "name": MODEL_NAME,

#             "loaded": _classifier is not None,

#             "device": DEVICE_NAME,

#             "candidate_labels": len(
#                 CANDIDATE_LABELS
#             ),

#         },

#         "runtime": runtime_statistics(),

#         "cache": cache_statistics(),

#         "performance": performance_statistics(),

#         "system": system_information(),

#     }
# # =====================================================
# # System Information
# # =====================================================

# def system_information() -> dict[str, Any]:
#     """
#     Return system information.
#     """

#     import platform
#     import transformers

#     return {

#         "python": platform.python_version(),

#         "platform": platform.system(),

#         "platform_release": platform.release(),

#         "torch": torch.__version__,

#         "transformers": transformers.__version__,

#     }
# # =====================================================
# # Category Classification
# # =====================================================

# def classify_article(
#     text: str,
#     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
# ) -> dict[str, Any]:
#     """
#     Classify a single news article.
#     """

#     log_debug(
#         "Classification request received."
#     )

#     # -------------------------------------------------
#     # Warm-up
#     # -------------------------------------------------

#     if not MODEL_WARMED_UP:

#         warmup_model()

#     # -------------------------------------------------
#     # Validate Input
#     # -------------------------------------------------

#     if not is_valid_input(text):

#         log_warning(
#             "Invalid input."
#         )

#         update_metrics(
#             success=False,
#             processing_time=0.0,
#         )

#         return build_error_response(
#             "Invalid input."
#         )

#     confidence_threshold = normalize_threshold(
#         confidence_threshold,
#     )

#     # -------------------------------------------------
#     # Cache Lookup
#     # -------------------------------------------------

#     cache_start = time.perf_counter()

#     cached_prediction = get_cached_prediction(
#         text,
#         confidence_threshold,
#     )

#     cache_lookup_time = round(
#         time.perf_counter() - cache_start,
#         6,
#     )

#     if cached_prediction is not None:

#         update_metrics(
#             success=True,
#             processing_time=0.0,
#         )

#         log_debug(
#             "Returned from cache."
#         )

#         return build_cached_response(
#             cached_prediction,
#             cache_lookup_time,
#         )

#     # -------------------------------------------------
#     # Model Prediction
#     # -------------------------------------------------

#     start_time = time.perf_counter()

#     try:

#         processed_text = preprocess_text(
#             text,
#         )

#         classifier = get_classifier()

#         result = classifier(

#             processed_text,

#             candidate_labels=CANDIDATE_LABELS,

#             hypothesis_template=HYPOTHESIS_TEMPLATE,

#             multi_label=False,

#         )

#         raw_category = result["labels"][0]

#         confidence = round(

#             float(
#                 result["scores"][0]
#             ),

#             4,

#         )

#         category = CATEGORY_MAPPING.get(

#             raw_category,

#             raw_category,

#         )

#         if confidence < confidence_threshold:

#             category = "Unknown"

#         top_categories = build_top_categories(

#             result["labels"],

#             result["scores"],

#         )

#         processing_time = round(

#             time.perf_counter()
#             - start_time,

#             4,

#         )

#         response = build_success_response(

#             category,

#             confidence,

#             top_categories,

#             processing_time,

#         )

#         cache_prediction(

#             processed_text,

#             confidence_threshold,

#             response,

#         )

#         update_metrics(

#             success=True,

#             processing_time=processing_time,

#         )

#         if ENABLE_PERFORMANCE_LOGS:

#             log_info(

#                 f"{category} | "

#                 f"{processing_time:.4f}s"

#             )

#         return response

#     except Exception as exc:

#         log_error(
#             str(exc)
#         )

#         update_metrics(

#             success=False,

#             processing_time=0.0,

#         )

#         return build_error_response(
#             str(exc)
#         )
# # =====================================================
# # Batch Classification
# # =====================================================

# def classify_articles_batch(
#     articles: list[str],
#     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
# ) -> dict[str, Any]:
#     """
#     Classify multiple articles.
#     """

#     if ENABLE_BATCH_LOGS:

#         log_info(

#             f"Batch started "

#             f"({len(articles)} articles)"

#         )

#     start_time = time.perf_counter()

#     results = []

#     processed = 0

#     failed = 0

#     for article in articles:

#         result = classify_article(

#             article,

#             confidence_threshold,

#         )

#         results.append(
#             result
#         )

#         if result["success"]:

#             processed += 1

#         else:

#             failed += 1

#     total_time = round(

#         time.perf_counter()
#         - start_time,

#         4,

#     )

#     if ENABLE_BATCH_LOGS:

#         log_info(

#             f"Batch completed "

#             f"in {total_time} sec."

#         )

#     return {

#         "success": True,

#         "processed": processed,

#         "failed": failed,

#         "total_articles": len(
#             articles
#         ),

#         "processing_time": total_time,

#         "results": results,

#     }

# # =====================================================
# # Public API
# # =====================================================

# __all__ = [

#     "classify_article",

#     "classify_articles_batch",

#     "health_check",

#     "system_information",

#     "module_information",

#     "module_statistics",

#     "runtime_statistics",

#     "performance_statistics",

#     "cache_statistics",

#     "clear_cache",

#     "reset_cache",

#     "reset_runtime_metrics",

#     "reset_module",

#     "warmup_model",

# ]
# # # =====================================================
# # # PHase 2 part1 
# # # =====================================================

# # # =====================================================
# # # Threshold Normalization
# # # =====================================================

# # def normalize_threshold(
# #     threshold: float,
# # ) -> float:
# #     """
# #     Normalize confidence threshold.
# #     """

# #     if not isinstance(
# #         threshold,
# #         (int, float),
# #     ):

# #         logger.warning(
# #             "Invalid threshold. Using default."
# #         )

# #         return DEFAULT_CONFIDENCE_THRESHOLD

# #     threshold = float(threshold)

# #     if threshold < 0.0:

# #         return 0.0

# #     if threshold > 1.0:

# #         return 1.0

# #     return threshold


# # # =====================================================
# # # Build Top Categories
# # # =====================================================

# # def build_top_categories(
# #     labels: list[str],
# #     scores: list[float],
# # ) -> list[dict[str, Any]]:
# #     """
# #     Convert raw HuggingFace output into
# #     standardized top category list.
# #     """

# #     top_categories = []

# #     for label, score in zip(

# #         labels[:TOP_K],

# #         scores[:TOP_K],

# #     ):

# #         top_categories.append(

# #             {

# #                 "label": CATEGORY_MAPPING.get(

# #                     label,

# #                     label,

# #                 ),

# #                 "score": round(

# #                     float(score),

# #                     4,

# #                 ),

# #             }

# #         )

# #     return top_categories


# # # =====================================================
# # # Success Response
# # # =====================================================

# # def build_success_response(

# #     category: str,

# #     confidence: float,

# #     top_categories: list[dict[str, Any]],

# #     processing_time: float,

# # ) -> dict[str, Any]:
# #     """
# #     Standard success response.
# #     """

# #     return {

# #         "success": True,

# #         "category": category,

# #         "score": confidence,

# #         "top_categories": top_categories,

# #         "processing_time": processing_time,

# #         "model": MODEL_NAME,

# #         "message": "Classification successful.",

# #     }


# # # =====================================================
# # # Error Response
# # # =====================================================

# # def build_error_response(
# #     message: str,
# # ) -> dict[str, Any]:
# #     """
# #     Standard error response.
# #     """

# #     return {

# #         "success": False,

# #         "category": "",

# #         "score": 0.0,

# #         "top_categories": [],

# #         "processing_time": 0.0,

# #         "model": MODEL_NAME,

# #         "message": message,

# #     }

# # # =====================================================
# # # PHase 2 part2 
# # # =====================================================
# # # =====================================================
# # # Category Classification
# # # =====================================================

# # def classify_article(
# #     text: str,
# #     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
# # ) -> dict[str, Any]:
# #     """
# #     Classify a single news article.
# #     """

# #     if not is_valid_input(text):

# #         logger.warning(
# #             "Invalid input received."
# #         )

# #         update_metrics(
# #             success=False,
# #             processing_time=0.0,
# #         )

# #         return build_error_response(
# #             "Invalid input."
# #         )

# #     confidence_threshold = normalize_threshold(
# #         confidence_threshold
# #     )

# #     start_time = time.perf_counter()

# #     try:

# #         text = preprocess_text(text)

# #         classifier = get_classifier()

# #         result = classifier(

# #             text,

# #             candidate_labels=CANDIDATE_LABELS,

# #             hypothesis_template=HYPOTHESIS_TEMPLATE,

# #             multi_label=False,

# #         )

# #         raw_category = result["labels"][0]

# #         confidence = round(

# #             float(result["scores"][0]),

# #             4,

# #         )

# #         category = CATEGORY_MAPPING.get(

# #             raw_category,

# #             raw_category,

# #         )

# #         if confidence < confidence_threshold:

# #             category = "Unknown"

# #         top_categories = build_top_categories(

# #             result["labels"],

# #             result["scores"],

# #         )

# #         processing_time = round(

# #             time.perf_counter()
# #             - start_time,

# #             4,

# #         )

# #         update_metrics(

# #             success=True,

# #             processing_time=processing_time,

# #         )

# #         logger.info(

# #             "Category=%s Score=%.4f Time=%.4fs",

# #             category,

# #             confidence,

# #             processing_time,

# #         )

# #         return build_success_response(

# #             category,

# #             confidence,

# #             top_categories,

# #             processing_time,

# #         )

# #     except Exception as exc:

# #         logger.exception(

# #             "Category classification failed."

# #         )

# #         update_metrics(

# #             success=False,

# #             processing_time=0.0,

# #         )

# #         return build_error_response(

# #             str(exc),

# #         )
# # # =====================================================
# # # PHase 3 part1
# # # =====================================================
# # # =====================================================
# # # Prediction Cache
# # # =====================================================

# # PREDICTION_CACHE: dict[
# #     tuple[str, float],
# #     dict[str, Any],
# # ] = {}

# # CACHE_HITS = 0

# # CACHE_MISSES = 0

# # MAX_CACHE_SIZE = 500


# # # =====================================================
# # # Cache Key
# # # =====================================================

# # def build_cache_key(
# #     text: str,
# #     threshold: float,
# # ) -> tuple[str, float]:
# #     """
# #     Build a unique cache key.
# #     """

# #     text = preprocess_text(text)

# #     threshold = round(
# #         threshold,
# #         2,
# #     )

# #     return (
# #         text,
# #         threshold,
# #     )


# # # =====================================================
# # # Get Cached Prediction
# # # =====================================================

# # def get_cached_prediction(
# #     text: str,
# #     threshold: float,
# # ) -> dict[str, Any] | None:
# #     """
# #     Return cached prediction.
# #     """

# #     global CACHE_HITS
# #     global CACHE_MISSES

# #     key = build_cache_key(
# #         text,
# #         threshold,
# #     )

# #     prediction = PREDICTION_CACHE.get(
# #         key,
# #     )

# #     if prediction is None:

# #         CACHE_MISSES += 1

# #         return None

# #     CACHE_HITS += 1

# #     logger.info(
# #         "Prediction served from cache."
# #     )

# #     return prediction


# # # =====================================================
# # # Store Prediction
# # # =====================================================

# # def cache_prediction(
# #     text: str,
# #     threshold: float,
# #     prediction: dict[str, Any],
# # ) -> None:
# #     """
# #     Store prediction in cache.
# #     """

# #     if len(
# #         PREDICTION_CACHE
# #     ) >= MAX_CACHE_SIZE:

# #         oldest_key = next(
# #             iter(PREDICTION_CACHE)
# #         )

# #         del PREDICTION_CACHE[
# #             oldest_key
# #         ]

# #     key = build_cache_key(
# #         text,
# #         threshold,
# #     )

# #     PREDICTION_CACHE[
# #         key
# #     ] = prediction


# # # =====================================================
# # # Cache Statistics
# # # =====================================================

# # def cache_statistics() -> dict[str, Any]:
# #     """
# #     Cache information.
# #     """

# #     total = CACHE_HITS + CACHE_MISSES

# #     hit_rate = 0.0

# #     if total > 0:

# #         hit_rate = round(

# #             CACHE_HITS
# #             / total,

# #             4,

# #         )

# #     return {

# #         "entries": len(
# #             PREDICTION_CACHE
# #         ),

# #         "hits": CACHE_HITS,

# #         "misses": CACHE_MISSES,

# #         "hit_rate": hit_rate,

# #         "max_size": MAX_CACHE_SIZE,

# #     }


# # # =====================================================
# # # Clear Cache
# # # =====================================================

# # def clear_cache() -> None:
# #     """
# #     Remove all cached predictions.
# #     """

# #     global CACHE_HITS
# #     global CACHE_MISSES

# #     PREDICTION_CACHE.clear()

# #     CACHE_HITS = 0

# #     CACHE_MISSES = 0

# #     logger.info(
# #         "Prediction cache cleared."
# #     )
# # # =====================================================
# # # PHase 3 part2
# # # =====================================================
# # # =====================================================
# # # Category Classification
# # # =====================================================

# # def classify_article(
# #     text: str,
# #     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
# # ) -> dict[str, Any]:
# #     """
# #     Classify a single news article.
# #     """

# #     # ------------------------------------------
# #     # Validate Input
# #     # ------------------------------------------

# #     if not is_valid_input(text):

# #         logger.warning(
# #             "Invalid input received."
# #         )

# #         update_metrics(
# #             success=False,
# #             processing_time=0.0,
# #         )

# #         return build_error_response(
# #             "Invalid input."
# #         )

# #     # ------------------------------------------
# #     # Normalize Threshold
# #     # ------------------------------------------

# #     confidence_threshold = normalize_threshold(
# #         confidence_threshold
# #     )

# #     # ------------------------------------------
# #     # Check Cache
# #     # ------------------------------------------

# #     cached_prediction = get_cached_prediction(
# #         text,
# #         confidence_threshold,
# #     )

# #     if cached_prediction is not None:

# #         logger.info(
# #             "Returning cached prediction."
# #         )

# #         update_metrics(
# #             success=True,
# #             processing_time=0.0,
# #         )

# #         return cached_prediction

# #     # ------------------------------------------
# #     # Start Timer
# #     # ------------------------------------------

# #     start_time = time.perf_counter()

# #     try:

# #         text = preprocess_text(text)

# #         classifier = get_classifier()

# #         result = classifier(

# #             text,

# #             candidate_labels=CANDIDATE_LABELS,

# #             hypothesis_template=HYPOTHESIS_TEMPLATE,

# #             multi_label=False,

# #         )

# #         raw_category = result["labels"][0]

# #         confidence = round(
# #             float(result["scores"][0]),
# #             4,
# #         )

# #         category = CATEGORY_MAPPING.get(
# #             raw_category,
# #             raw_category,
# #         )

# #         if confidence < confidence_threshold:

# #             category = "Unknown"

# #         top_categories = build_top_categories(

# #             result["labels"],

# #             result["scores"],

# #         )

# #         processing_time = round(

# #             time.perf_counter()
# #             - start_time,

# #             4,

# #         )

# #         response = build_success_response(

# #             category,

# #             confidence,

# #             top_categories,

# #             processing_time,

# #         )

# #         cache_prediction(

# #             text,

# #             confidence_threshold,

# #             response,

# #         )

# #         update_metrics(

# #             success=True,

# #             processing_time=processing_time,

# #         )

# #         logger.info(

# #             "Category=%s Score=%.4f Time=%.4fs",

# #             category,

# #             confidence,

# #             processing_time,

# #         )

# #         return response

# #     except Exception as exc:

# #         logger.exception(

# #             "Category classification failed."

# #         )

# #         update_metrics(

# #             success=False,

# #             processing_time=0.0,

# #         )

# #         return build_error_response(

# #             str(exc),

# #         )
# # # =====================================================
# # # Health Check
# # # =====================================================

# # def health_check() -> dict[str, Any]:
# #     """
# #     Return classifier health.
# #     """

# #     return {

# #         "status": "healthy",

# #         "model": MODEL_NAME,

# #         "device": DEVICE_NAME,

# #         "loaded": _classifier is not None,

# #         "labels": len(
# #             CANDIDATE_LABELS
# #         ),

# #         "runtime": runtime_statistics(),

# #         "cache": cache_statistics(),

# #     }
# # # =====================================================
# # # Module Start Time
# # # =====================================================

# # MODULE_START_TIME = time.time()


# # # =====================================================
# # # Performance Metrics
# # # =====================================================

# # FASTEST_REQUEST = None

# # SLOWEST_REQUEST = None


# # # =====================================================
# # # Update Performance Metrics
# # # =====================================================

# # def update_performance_metrics(
# #     processing_time: float,
# # ) -> None:
# #     """
# #     Update fastest and slowest request.
# #     """

# #     global FASTEST_REQUEST
# #     global SLOWEST_REQUEST

# #     if processing_time <= 0:

# #         return

# #     if FASTEST_REQUEST is None:

# #         FASTEST_REQUEST = processing_time

# #     elif processing_time < FASTEST_REQUEST:

# #         FASTEST_REQUEST = processing_time

# #     if SLOWEST_REQUEST is None:

# #         SLOWEST_REQUEST = processing_time

# #     elif processing_time > SLOWEST_REQUEST:

# #         SLOWEST_REQUEST = processing_time


# # # =====================================================
# # # Performance Statistics
# # # =====================================================

# # def performance_statistics() -> dict[str, Any]:
# #     """
# #     Return performance statistics.
# #     """

# #     success_rate = 0.0

# #     if TOTAL_REQUESTS > 0:

# #         success_rate = round(

# #             SUCCESSFUL_REQUESTS
# #             / TOTAL_REQUESTS,

# #             4,

# #         )

# #     failure_rate = round(

# #         1.0 - success_rate,

# #         4,

# #     )

# #     uptime_seconds = round(

# #         time.time() - MODULE_START_TIME,

# #         2,

# #     )

# #     return {

# #         "uptime_seconds": uptime_seconds,

# #         "fastest_request": FASTEST_REQUEST,

# #         "slowest_request": SLOWEST_REQUEST,

# #         "success_rate": success_rate,

# #         "failure_rate": failure_rate,

# #     }
# # # =====================================================
# # # Update Runtime Metrics
# # # =====================================================


# # def update_metrics(
# #     success: bool,
# #     processing_time: float,
# # ) -> None:
# #     """
# #     Update runtime statistics.
# #     """

# #     global TOTAL_REQUESTS
# #     global SUCCESSFUL_REQUESTS
# #     global FAILED_REQUESTS
# #     global TOTAL_PROCESSING_TIME
# #     global LAST_REQUEST_TIME

# #     TOTAL_REQUESTS += 1

# #     if success:

# #         SUCCESSFUL_REQUESTS += 1

# #         TOTAL_PROCESSING_TIME += processing_time

# #     else:

# #         FAILED_REQUESTS += 1

# #     LAST_REQUEST_TIME = time.strftime(
# #         "%Y-%m-%d %H:%M:%S"
# #     )

# #     update_performance_metrics(
# #         processing_time
# #     )
# # # =====================================================
# # # Health Check
# # # =====================================================

# # def health_check() -> dict[str, Any]:
# #     """
# #     Return complete health report.
# #     """

# #     return {

# #         "status": "healthy",

# #         "model": {

# #             "name": MODEL_NAME,

# #             "loaded": _classifier is not None,

# #             "device": DEVICE_NAME,

# #             "candidate_labels": len(
# #                 CANDIDATE_LABELS
# #             ),

# #         },

# #         "runtime": runtime_statistics(),

# #         "cache": cache_statistics(),

# #         "performance": performance_statistics(),

# #     }
# # # =====================================================
# # # System Information
# # # =====================================================

# # def system_information() -> dict[str, Any]:
# #     """
# #     Return environment information.
# #     """

# #     import platform

# #     import transformers

# #     return {

# #         "python": platform.python_version(),

# #         "platform": platform.system(),

# #         "platform_release": platform.release(),

# #         "torch": torch.__version__,

# #         "transformers": transformers.__version__,

# #     }
# # # =====================================================
# # # Health Check
# # # =====================================================

# # def health_check() -> dict[str, Any]:
# #     """
# #     Return complete module health.
# #     """

# #     return {

# #         "status": "healthy",

# #         "model": {

# #             "name": MODEL_NAME,

# #             "loaded": _classifier is not None,

# #             "device": DEVICE_NAME,

# #             "candidate_labels": len(
# #                 CANDIDATE_LABELS
# #             ),

# #         },

# #         "runtime": runtime_statistics(),

# #         "cache": cache_statistics(),

# #         "performance": performance_statistics(),

# #         "system": system_information(),

# #     }



# # # =====================================================
# # # Production Configuration
# # # =====================================================

# # DEBUG_MODE = False

# # ENABLE_CONSOLE_LOGS = True

# # ENABLE_PERFORMANCE_LOGS = True

# # ENABLE_CACHE_LOGS = True

# # ENABLE_ERROR_LOGS = True

# # ENABLE_BATCH_LOGS = True

# # MODULE_NAME = "Category Classifier"

# # MODULE_VERSION = "4.2"

# # LOG_PREFIX = "[CATEGORY]"

# # # =====================================================
# # # Logging Helpers
# # # =====================================================

# # def log_debug(
# #     message: str,
# # ) -> None:

# #     if DEBUG_MODE:

# #         logger.info(

# #             "%s %s",

# #             LOG_PREFIX,

# #             message,

# #         )


# # def log_info(
# #     message: str,
# # ) -> None:

# #     if ENABLE_CONSOLE_LOGS:

# #         logger.info(

# #             "%s %s",

# #             LOG_PREFIX,

# #             message,

# #         )


# # def log_warning(
# #     message: str,
# # ) -> None:

# #     logger.warning(

# #         "%s %s",

# #         LOG_PREFIX,

# #         message,

# #     )


# # def log_error(
# #     message: str,
# # ) -> None:

# #     if ENABLE_ERROR_LOGS:

# #         logger.exception(

# #             "%s %s",

# #             LOG_PREFIX,

# #             message,

# #         )
# # # =====================================================
# # # Module Information
# # # =====================================================

# # def module_information() -> dict[str, Any]:

# #     return {

# #         "module": MODULE_NAME,

# #         "version": MODULE_VERSION,

# #         "model": MODEL_NAME,

# #         "device": DEVICE_NAME,

# #         "debug": DEBUG_MODE,

# #     }
# # # =====================================================
# # # Lazy Model Loader
# # # =====================================================

# # def get_classifier():
# #     """
# #     Load model only once.
# #     """

# #     global _classifier

# #     if _classifier is None:

# #         log_info(
# #             "Loading BART classification model..."
# #         )

# #         start_time = time.perf_counter()

# #         _classifier = pipeline(

# #             task="zero-shot-classification",

# #             model=MODEL_NAME,

# #             device=DEVICE,

# #         )

# #         load_time = round(

# #             time.perf_counter()
# #             - start_time,

# #             4,

# #         )

# #         log_info(

# #             f"Model loaded successfully in {load_time} sec."

# #         )

# #     else:

# #         log_debug(
# #             "Using already loaded model."
# #         )

# #     return _classifier
# # # =====================================================
# # # Get Cached Prediction
# # # =====================================================

# # def get_cached_prediction(
# #     text: str,
# #     threshold: float,
# # ) -> dict[str, Any] | None:
# #     """
# #     Return cached prediction.
# #     """

# #     global CACHE_HITS
# #     global CACHE_MISSES

# #     key = build_cache_key(
# #         text,
# #         threshold,
# #     )

# #     prediction = PREDICTION_CACHE.get(
# #         key,
# #     )

# #     if prediction is None:

# #         CACHE_MISSES += 1

# #         if ENABLE_CACHE_LOGS:

# #             log_debug(
# #                 "Cache MISS"
# #             )

# #         return None

# #     CACHE_HITS += 1

# #     if ENABLE_CACHE_LOGS:

# #         log_debug(
# #             "Cache HIT"
# #         )

# #     return prediction
# # # =====================================================
# # # Store Prediction
# # # =====================================================

# # def cache_prediction(
# #     text: str,
# #     threshold: float,
# #     prediction: dict[str, Any],
# # ) -> None:
# #     """
# #     Store prediction in cache.
# #     """

# #     if len(
# #         PREDICTION_CACHE
# #     ) >= MAX_CACHE_SIZE:

# #         oldest_key = next(
# #             iter(PREDICTION_CACHE)
# #         )

# #         del PREDICTION_CACHE[
# #             oldest_key
# #         ]

# #         log_debug(
# #             "Old cache entry removed."
# #         )

# #     key = build_cache_key(
# #         text,
# #         threshold,
# #     )

# #     PREDICTION_CACHE[
# #         key
# #     ] = prediction

# #     if ENABLE_CACHE_LOGS:

# #         log_debug(
# #             "Prediction cached."
# #         )
# # # =====================================================
# # # Clear Cache
# # # =====================================================
# # # =====================================================
# # # Clear Cache
# # # =====================================================

# # def clear_cache() -> None:
# #     """
# #     Clear prediction cache.
# #     """

# #     global CACHE_HITS
# #     global CACHE_MISSES

# #     PREDICTION_CACHE.clear()

# #     CACHE_HITS = 0

# #     CACHE_MISSES = 0

# #     log_info(
# #         "Prediction cache cleared."
# #     )


# # # =====================================================
# # # Health Check
# # # =====================================================

# # def health_check() -> dict[str, Any]:
# #     """
# #     Return complete module health.
# #     """

# #     return {

# #         "status": "healthy",

# #         "module": module_information(),

# #         "model": {

# #             "name": MODEL_NAME,

# #             "loaded": _classifier is not None,

# #             "device": DEVICE_NAME,

# #             "candidate_labels": len(
# #                 CANDIDATE_LABELS
# #             ),

# #         },

# #         "runtime": runtime_statistics(),

# #         "cache": cache_statistics(),

# #         "performance": performance_statistics(),

# #         "system": system_information(),

# #     }
# # # =====================================================
# # # Category Classification
# # # =====================================================

# # def classify_article(
# #     text: str,
# #     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
# # ) -> dict[str, Any]:
# #     """
# #     Classify a single news article.
# #     """

# #     log_debug(
# #         "Classification request received."
# #     )

# #     if not is_valid_input(text):

# #         log_warning(
# #             "Invalid input."
# #         )

# #         update_metrics(
# #             success=False,
# #             processing_time=0.0,
# #         )

# #         return build_error_response(
# #             "Invalid input."
# #         )

# #     confidence_threshold = normalize_threshold(
# #         confidence_threshold
# #     )

# #     cached_prediction = get_cached_prediction(
# #         text,
# #         confidence_threshold,
# #     )

# #     if cached_prediction is not None:

# #         log_debug(
# #             "Returning cached prediction."
# #         )

# #         update_metrics(
# #             success=True,
# #             processing_time=0.0,
# #         )

# #         return cached_prediction

# #     start_time = time.perf_counter()

# #     try:

# #         classifier = get_classifier()

# #         processed_text = preprocess_text(
# #             text,
# #         )

# #         log_debug(
# #             "Running BART model."
# #         )

# #         result = classifier(

# #             processed_text,

# #             candidate_labels=CANDIDATE_LABELS,

# #             hypothesis_template=HYPOTHESIS_TEMPLATE,

# #             multi_label=False,

# #         )

# #         raw_category = result["labels"][0]

# #         confidence = round(

# #             float(
# #                 result["scores"][0]
# #             ),

# #             4,

# #         )

# #         category = CATEGORY_MAPPING.get(

# #             raw_category,

# #             raw_category,

# #         )

# #         if confidence < confidence_threshold:

# #             category = "Unknown"

# #         top_categories = build_top_categories(

# #             result["labels"],

# #             result["scores"],

# #         )

# #         processing_time = round(

# #             time.perf_counter()
# #             - start_time,

# #             4,

# #         )

# #         response = build_success_response(

# #             category,

# #             confidence,

# #             top_categories,

# #             processing_time,

# #         )

# #         cache_prediction(

# #             processed_text,

# #             confidence_threshold,

# #             response,

# #         )

# #         update_metrics(

# #             success=True,

# #             processing_time=processing_time,

# #         )

# #         if ENABLE_PERFORMANCE_LOGS:

# #             log_info(

# #                 f"{category} | "
# #                 f"{processing_time} sec"

# #             )

# #         return response

# #     except Exception as exc:

# #         log_error(
# #             str(exc)
# #         )

# #         update_metrics(

# #             success=False,

# #             processing_time=0.0,

# #         )

# #         return build_error_response(
# #             str(exc)
# #         )
# # # =====================================================
# # # Batch Classification
# # # =====================================================

# # def classify_articles_batch(
# #     articles: list[str],
# #     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
# # ) -> dict[str, Any]:
# #     """
# #     Batch classification.
# #     """

# #     if ENABLE_BATCH_LOGS:

# #         log_info(
# #             f"Batch started ({len(articles)} articles)"
# #         )

# #     start_time = time.perf_counter()

# #     results = []

# #     processed = 0

# #     failed = 0

# #     for article in articles:

# #         result = classify_article(

# #             article,

# #             confidence_threshold,

# #         )

# #         results.append(
# #             result
# #         )

# #         if result["success"]:

# #             processed += 1

# #         else:

# #             failed += 1

# #     total_time = round(

# #         time.perf_counter()
# #         - start_time,

# #         4,

# #     )

# #     if ENABLE_BATCH_LOGS:

# #         log_info(

# #             f"Batch completed in "
# #             f"{total_time} sec"

# #         )

# #     return {

# #         "success": True,

# #         "processed": processed,

# #         "failed": failed,

# #         "total_articles": len(
# #             articles
# #         ),

# #         "processing_time": total_time,

# #         "results": results,

# #     }




"""
=====================================================
News Category Classifier
Project : News Intelligence Platform
Module  : nlp.category_classifier
Version : 3.0
Author  : CDAC Project
=====================================================
"""


from __future__ import annotations

import os

os.environ["HF_HOME"] = r"D:\huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = r"D:\huggingface_cache"
os.environ["HF_HUB_CACHE"] = r"D:\huggingface_cache"

import logging
import platform
import time
from typing import Any

import torch
import transformers
from transformers import pipeline


# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(__name__)

# =====================================================
# Module Configuration
# =====================================================

MODULE_NAME = "Category Classifier"

MODULE_VERSION = "3.0"

MODEL_NAME = "typeform/distilbert-base-uncased-mnli"

DEBUG_MODE = False

# =====================================================
# Logging Configuration
# =====================================================

ENABLE_CONSOLE_LOGS = True

ENABLE_ERROR_LOGS = True

ENABLE_CACHE_LOGS = True

ENABLE_BATCH_LOGS = True

ENABLE_PERFORMANCE_LOGS = True

LOG_PREFIX = "[CATEGORY]"

# =====================================================
# Device Configuration
# =====================================================

DEVICE = 0 if torch.cuda.is_available() else -1

DEVICE_NAME = "GPU" if DEVICE == 0 else "CPU"

# =====================================================
# Lazy Loaded Model
# =====================================================

_classifier = None

# =====================================================
# Runtime Metrics
# =====================================================

TOTAL_REQUESTS = 0

SUCCESSFUL_REQUESTS = 0

FAILED_REQUESTS = 0

TOTAL_PROCESSING_TIME = 0.0

LAST_REQUEST_TIME = None

# =====================================================
# Cache Configuration
# =====================================================

PREDICTION_CACHE: dict[
    tuple[str, float],
    dict[str, Any],
] = {}

CACHE_HITS = 0

CACHE_MISSES = 0

MAX_CACHE_SIZE = 500

# =====================================================
# Performance Metrics
# =====================================================

MODULE_START_TIME = time.time()

FASTEST_REQUEST = None

SLOWEST_REQUEST = None

# =====================================================
# Classification Configuration
# =====================================================

DEFAULT_CONFIDENCE_THRESHOLD = 0.40

TOP_K = 3

HYPOTHESIS_TEMPLATE = (
    "This news article is about {}."
)

# =====================================================
# Candidate Labels
# =====================================================

CANDIDATE_LABELS = [

    "Politics and Government",

    "Business and Finance",

    "Technology and Artificial Intelligence",

    "Sports",

    "Entertainment and Media",

    "Health and Medicine",

    "Science and Research",

    "World News",

    "Education",

    "Environment and Climate",

    "Crime and Law",

]

# =====================================================
# Category Mapping
# =====================================================

CATEGORY_MAPPING = {

    "Politics and Government": "Politics",

    "Business and Finance": "Business",

    "Technology and Artificial Intelligence": "Technology",

    "Sports": "Sports",

    "Entertainment and Media": "Entertainment",

    "Health and Medicine": "Health",

    "Science and Research": "Science",

    "World News": "World",

    "Education": "Education",

    "Environment and Climate": "Environment",

    "Crime and Law": "Crime",

}

# =====================================================
# Input Validation Configuration
# =====================================================

MIN_INPUT_CHARACTERS = 20

MIN_INPUT_WORDS = 3

MAX_INPUT_CHARACTERS = 1500

# =====================================================
# Logging Helpers
# =====================================================

def log_debug(
    message: str,
) -> None:

    if DEBUG_MODE:

        logger.info(
            "%s %s",
            LOG_PREFIX,
            message,
        )


def log_info(
    message: str,
) -> None:

    if ENABLE_CONSOLE_LOGS:

        logger.info(
            "%s %s",
            LOG_PREFIX,
            message,
        )


def log_warning(
    message: str,
) -> None:

    logger.warning(
        "%s %s",
        LOG_PREFIX,
        message,
    )


def log_error(
    message: str,
) -> None:

    if ENABLE_ERROR_LOGS:

        logger.exception(
            "%s %s",
            LOG_PREFIX,
            message,
        )

# =====================================================
# Lazy Model Loader
# =====================================================

def get_classifier():
    """
    Load the Hugging Face model only once.
    """

    global _classifier

    if _classifier is None:

        log_info(
            "Loading category classification model..."
        )

        start = time.perf_counter()

        _classifier = pipeline(

            task="zero-shot-classification",

            model=MODEL_NAME,

            device=DEVICE,

        )

        elapsed = round(

            time.perf_counter() - start,

            4,

        )

        log_info(
            f"Model loaded in {elapsed} sec."
        )

    return _classifier

# =====================================================
# Input Validation
# =====================================================

def is_valid_input(
    text: str,
) -> bool:
    """
    Validate article text.
    """

    if not isinstance(
        text,
        str,
    ):
        return False

    text = text.strip()

    if not text:
        return False

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

    text = " ".join(
        text.split()
    )

    if len(text) > MAX_INPUT_CHARACTERS:

        text = text[
            :MAX_INPUT_CHARACTERS
        ]

    return text.strip()
# =====================================================
# Threshold Normalization
# =====================================================

def normalize_threshold(
    threshold: float,
) -> float:
    """
    Normalize confidence threshold.
    """

    if not isinstance(
        threshold,
        (int, float),
    ):
        return DEFAULT_CONFIDENCE_THRESHOLD

    threshold = float(
        threshold,
    )

    if threshold < 0.0:
        return 0.0

    if threshold > 1.0:
        return 1.0

    return threshold


# =====================================================
# Build Top Categories
# =====================================================

def build_top_categories(
    labels: list[str],
    scores: list[float],
) -> list[dict[str, Any]]:
    """
    Build top predicted categories.
    """

    categories = []

    for label, score in zip(

        labels[:TOP_K],

        scores[:TOP_K],

    ):

        categories.append(

            {

                "label": CATEGORY_MAPPING.get(
                    label,
                    label,
                ),

                "score": round(
                    float(score),
                    4,
                ),

            }

        )

    return categories


# =====================================================
# Success Response
# =====================================================

def build_success_response(

    category: str,

    confidence: float,

    top_categories: list[dict[str, Any]],

    processing_time: float,

) -> dict[str, Any]:

    return {

        "success": True,

        "category": category,

        "score": confidence,

        "top_categories": top_categories,

        "processing_time": processing_time,

        "model": MODEL_NAME,

        "message": "Classification successful.",

    }


# =====================================================
# Error Response
# =====================================================

def build_error_response(
    message: str,
) -> dict[str, Any]:

    return {

        "success": False,

        "category": "",

        "score": 0.0,

        "top_categories": [],

        "processing_time": 0.0,

        "model": MODEL_NAME,

        "message": message,

    }


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

        TOTAL_PROCESSING_TIME += processing_time

    else:

        FAILED_REQUESTS += 1

    LAST_REQUEST_TIME = time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    update_performance_metrics(
        processing_time,
    )


# =====================================================
# Runtime Statistics
# =====================================================

def runtime_statistics() -> dict[str, Any]:
    """
    Return runtime statistics.
    """

    average = 0.0

    if SUCCESSFUL_REQUESTS > 0:

        average = round(

            TOTAL_PROCESSING_TIME
            / SUCCESSFUL_REQUESTS,

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
# Cache Key
# =====================================================

def build_cache_key(
    text: str,
    threshold: float,
) -> tuple[str, float]:

    return (

        preprocess_text(text),

        round(
            threshold,
            2,
        ),

    )


# =====================================================
# Cache Lookup
# =====================================================

def get_cached_prediction(
    text: str,
    threshold: float,
) -> dict[str, Any] | None:

    global CACHE_HITS
    global CACHE_MISSES

    key = build_cache_key(
        text,
        threshold,
    )

    prediction = PREDICTION_CACHE.get(
        key,
    )

    if prediction is None:

        CACHE_MISSES += 1

        return None

    CACHE_HITS += 1

    return prediction


# =====================================================
# Cache Storage
# =====================================================

def cache_prediction(
    text: str,
    threshold: float,
    prediction: dict[str, Any],
) -> None:

    if len(
        PREDICTION_CACHE
    ) >= MAX_CACHE_SIZE:

        oldest = next(
            iter(
                PREDICTION_CACHE
            )
        )

        del PREDICTION_CACHE[
            oldest
        ]

    key = build_cache_key(
        text,
        threshold,
    )

    PREDICTION_CACHE[
        key
    ] = prediction


# =====================================================
# Cache Statistics
# =====================================================

def cache_statistics() -> dict[str, Any]:

    total = CACHE_HITS + CACHE_MISSES

    hit_rate = 0.0

    if total > 0:

        hit_rate = round(

            CACHE_HITS / total,

            4,

        )

    return {

        "entries": len(
            PREDICTION_CACHE
        ),

        "hits": CACHE_HITS,

        "misses": CACHE_MISSES,

        "hit_rate": hit_rate,

        "max_size": MAX_CACHE_SIZE,

    }


# =====================================================
# Clear Cache
# =====================================================

def clear_cache() -> None:

    global CACHE_HITS
    global CACHE_MISSES

    PREDICTION_CACHE.clear()

    CACHE_HITS = 0

    CACHE_MISSES = 0


# =====================================================
# Performance Metrics
# =====================================================

def update_performance_metrics(
    processing_time: float,
) -> None:

    global FASTEST_REQUEST
    global SLOWEST_REQUEST

    if processing_time <= 0:
        return

    if FASTEST_REQUEST is None:

        FASTEST_REQUEST = processing_time

    elif processing_time < FASTEST_REQUEST:

        FASTEST_REQUEST = processing_time

    if SLOWEST_REQUEST is None:

        SLOWEST_REQUEST = processing_time

    elif processing_time > SLOWEST_REQUEST:

        SLOWEST_REQUEST = processing_time


# =====================================================
# Performance Statistics
# =====================================================

def performance_statistics() -> dict[str, Any]:

    success_rate = 0.0

    if TOTAL_REQUESTS > 0:

        success_rate = round(

            SUCCESSFUL_REQUESTS
            / TOTAL_REQUESTS,

            4,

        )

    return {

        "uptime_seconds": round(

            time.time()
            - MODULE_START_TIME,

            2,

        ),

        "fastest_request": FASTEST_REQUEST,

        "slowest_request": SLOWEST_REQUEST,

        "success_rate": success_rate,

        "failure_rate": round(
            1.0 - success_rate,
            4,
        ),

    }
# =====================================================
# Category Classification
# =====================================================

def classify_article(
    text: str,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    """
    Classify a single news article.
    """

    # ------------------------------------------
    # Validate Input
    # ------------------------------------------

    if not is_valid_input(text):

        log_warning(
            "Invalid input."
        )

        update_metrics(
            success=False,
            processing_time=0.0,
        )

        return build_error_response(
            "Invalid input."
        )

    # ------------------------------------------
    # Normalize Threshold
    # ------------------------------------------

    confidence_threshold = normalize_threshold(
        confidence_threshold,
    )

    # ------------------------------------------
    # Cache Lookup
    # ------------------------------------------

    cached_prediction = get_cached_prediction(
        text,
        confidence_threshold,
    )

    if cached_prediction is not None:

        log_debug(
            "Prediction returned from cache."
        )

        update_metrics(
            success=True,
            processing_time=0.0,
        )

        return cached_prediction

    # ------------------------------------------
    # Run Model
    # ------------------------------------------

    start_time = time.perf_counter()

    try:

        processed_text = preprocess_text(
            text,
        )

        classifier = get_classifier()

        result = classifier(

            processed_text,

            candidate_labels=CANDIDATE_LABELS,

            hypothesis_template=HYPOTHESIS_TEMPLATE,

            multi_label=False,

        )

        raw_category = result["labels"][0]

        confidence = round(

            float(
                result["scores"][0]
            ),

            4,

        )

        category = CATEGORY_MAPPING.get(

            raw_category,

            raw_category,

        )

        if confidence < confidence_threshold:

            category = "Unknown"

        top_categories = build_top_categories(

            result["labels"],

            result["scores"],

        )

        processing_time = round(

            time.perf_counter()
            - start_time,

            4,

        )

        response = build_success_response(

            category,

            confidence,

            top_categories,

            processing_time,

        )

        cache_prediction(

            processed_text,

            confidence_threshold,

            response,

        )

        update_metrics(

            success=True,

            processing_time=processing_time,

        )

        if ENABLE_PERFORMANCE_LOGS:

            log_info(

                f"Category={category} | "
                f"Score={confidence:.4f} | "
                f"Time={processing_time:.4f}s"

            )

        return response

    except Exception as exc:

        log_error(
            str(exc)
        )

        update_metrics(

            success=False,

            processing_time=0.0,

        )

        return build_error_response(

            str(exc),

        )
# =====================================================
# Batch Classification
# =====================================================

def classify_articles_batch(
    articles: list[str],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> dict[str, Any]:
    """
    Classify multiple news articles.
    """

    if not isinstance(articles, list):

        return {

            "success": False,

            "message": "Input must be a list of articles.",

            "results": [],

        }

    start_time = time.perf_counter()

    results = []

    processed = 0

    failed = 0

    for article in articles:

        result = classify_article(

            article,

            confidence_threshold,

        )

        results.append(
            result
        )

        if result["success"]:

            processed += 1

        else:

            failed += 1

    total_time = round(

        time.perf_counter() - start_time,

        4,

    )

    return {

        "success": True,

        "processed": processed,

        "failed": failed,

        "total_articles": len(articles),

        "processing_time": total_time,

        "results": results,

    }


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

        "debug": DEBUG_MODE,

    }


# =====================================================
# System Information
# =====================================================

def system_information() -> dict[str, Any]:
    """
    Return system information.
    """

    return {

        "python": platform.python_version(),

        "platform": platform.system(),

        "platform_release": platform.release(),

        "torch": torch.__version__,

        "transformers": transformers.__version__,

    }


# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Return complete health information.
    """

    return {

        "status": "healthy",

        "module": module_information(),

        "model": {

            "name": MODEL_NAME,

            "loaded": _classifier is not None,

            "device": DEVICE_NAME,

            "candidate_labels": len(
                CANDIDATE_LABELS
            ),

        },

        "runtime": runtime_statistics(),

        "cache": cache_statistics(),

        "performance": performance_statistics(),

        "system": system_information(),

    }


# =====================================================
# Public API
# =====================================================

__all__ = [

    "classify_article",

    "classify_articles_batch",

    "health_check",

    "module_information",

    "system_information",

    "runtime_statistics",

    "performance_statistics",

    "cache_statistics",

    "clear_cache",

]