"""
=====================================================
News Processing Pipeline
Project : News Intelligence Platform
Module  : pipeline
Version : 1.0 (Production)
=====================================================

End-to-end NLP processing pipeline.

Workflow

Raw Article
    │
    ▼
Content Cleaner
    ▼
Summarizer
    ▼
Sentiment Analysis
    ▼
Category Classification
    ▼
Keyword Extraction
    ▼
Named Entity Recognition
    ▼
Sentence Embeddings
    ▼
MongoDB / Elasticsearch
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any


# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(__name__)

# =====================================================
# NLP Modules
# =====================================================

try:

    from nlp.content_cleaner import clean_content

    from nlp.summarizer import generate_summary

    from nlp.sentiment import predict_sentiment

    from nlp.category_classifier import classify_article

    from nlp.keyword_extractor import extract_keywords

    from nlp.ner import extract_entities

    from nlp.embeddings import extract_embedding

except Exception:

    logger.exception(
        "Unable to import NLP modules."
    )

    raise


# =====================================================
# Pipeline Configuration
# =====================================================

PIPELINE_NAME = "News Intelligence Pipeline"

PIPELINE_VERSION = "1.0"

PIPELINE_STATUS = "Production"

# =====================================================
# Metadata Configuration
# =====================================================

DEFAULT_LANGUAGE = "en"

DEFAULT_SOURCE = "Unknown"

# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Pipeline health status.
    """

    return {

        "status": "healthy",

        "pipeline": PIPELINE_NAME,

        "version": PIPELINE_VERSION,

        "environment": PIPELINE_STATUS,

        "modules": {

            "cleaner": True,

            "summarizer": True,

            "sentiment": True,

            "category": True,

            "keywords": True,

            "ner": True,

            "embeddings": True,

        },

    }


# =====================================================
# Pipeline Metadata
# =====================================================

def build_metadata() -> dict[str, Any]:
    """
    Build processing metadata.
    """

    return {

        "pipeline": PIPELINE_NAME,

        "version": PIPELINE_VERSION,

        "processed_at": datetime.utcnow().isoformat(),

    }


# =====================================================
# Processing Statistics
# =====================================================

def build_statistics(
    start_time: float,
) -> dict[str, Any]:
    """
    Build processing statistics.
    """

    processing_time = round(

        time.perf_counter() - start_time,

        4,

    )

    return {

        "processing_time": processing_time,

    }


# =====================================================
# Public Exports
# =====================================================
__all__ = [

    "health_check",

    "process_article",

    "process_articles_batch",

    "build_mongodb_document",

    "validate_document",

]
# =====================================================
# Process Single Article
# =====================================================

def process_article(
    article: dict[str, Any],
) -> dict[str, Any]:
    """
    Process a single news article using the complete NLP pipeline.

    Parameters
    ----------
    article : dict

    Returns
    -------
    dict
        Fully processed article.
    """

    logger.info(
        "Starting article processing."
    )

    start_time = time.perf_counter()

    # -------------------------------------------------
    # Validate Input
    # -------------------------------------------------

    if not isinstance(article, dict):

        logger.warning(
            "Article must be a dictionary."
        )

        return {}

    title = article.get("title", "")

    content = article.get("content", "")

    source = article.get(
        "source",
        DEFAULT_SOURCE,
    )

    url = article.get("url", "")

    published_at = article.get(
        "published_at",
        "",
    )

    if not content:

        logger.warning(
            "Article content is empty."
        )

        return {}

    # -------------------------------------------------
    # Cleaner
    # -------------------------------------------------

    cleaned_content = clean_content(
        content
    )

    # -------------------------------------------------
    # Summarizer
    # -------------------------------------------------

    summary = generate_summary(
        cleaned_content
    )

    # -------------------------------------------------
    # Sentiment
    # -------------------------------------------------

    sentiment = predict_sentiment(
        cleaned_content
    )

    # -------------------------------------------------
    # Category
    # -------------------------------------------------

    category = classify_article(
        cleaned_content
    )

    # -------------------------------------------------
    # Keywords
    # -------------------------------------------------

    keywords = extract_keywords(
        cleaned_content
    )

    # -------------------------------------------------
    # Named Entities
    # -------------------------------------------------

    entities = extract_entities(
        cleaned_content
    )

    # -------------------------------------------------
    # Embeddings
    # -------------------------------------------------

    embedding = extract_embedding(
        cleaned_content
    )

    # -------------------------------------------------
    # Build Output
    # -------------------------------------------------

    processed_article = {

        "title": title,

        "content": content,

        "clean_content": cleaned_content,

        "summary": summary,

        "sentiment": sentiment,

        "category": category,

        "keywords": keywords,

        "entities": entities,

        "embedding": embedding,

        "source": source,

        "url": url,

        "published_at": published_at,

        "metadata": build_metadata(),

        "statistics": build_statistics(
            start_time
        ),

    }

    logger.info(
        "Article processed successfully."
    )

    return processed_article
# =====================================================
# Batch Article Processing
# =====================================================

def process_articles_batch(
    articles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Process multiple news articles.

    Parameters
    ----------
    articles : list[dict]
        List of raw news articles.

    Returns
    -------
    list[dict]
        Successfully processed articles.
    """

    logger.info("=" * 60)
    logger.info("Starting batch article processing")
    logger.info("=" * 60)

    print("=" * 60)
    print("Starting batch article processing")
    print("=" * 60)

    # -------------------------------------------------
    # Validate Input
    # -------------------------------------------------

    if not isinstance(articles, list):

        logger.warning("Input must be a list.")

        print("ERROR : Input must be a list.")

        return []

    if len(articles) == 0:

        logger.warning("Empty article list.")

        print("ERROR : Empty article list.")

        return []

    processed_articles: list[dict[str, Any]] = []

    processed_count = 0
    skipped_count = 0
    failed_count = 0

    total_articles = len(articles)

    # -------------------------------------------------
    # Process Each Article
    # -------------------------------------------------

    for index, article in enumerate(
        articles,
        start=1,
    ):

        print()
        print("-" * 60)
        print(
            f"Processing Article {index}/{total_articles}"
        )
        print("-" * 60)

        logger.info(
            "Processing article %d/%d",
            index,
            total_articles,
        )

        try:

            result = process_article(
                article
            )

            if result:

                processed_articles.append(
                    result
                )

                processed_count += 1

                print("SUCCESS")

            else:

                skipped_count += 1

                print("SKIPPED")

        except Exception as e:

            failed_count += 1

            logger.exception(
                "Article %d failed.",
                index,
            )

            print("FAILED")
            print(e)

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("Batch Summary")
    print("=" * 60)

    print(
        f"Total Articles : {total_articles}"
    )

    print(
        f"Processed      : {processed_count}"
    )

    print(
        f"Skipped        : {skipped_count}"
    )

    print(
        f"Failed         : {failed_count}"
    )

    print(
        f"Returned       : {len(processed_articles)}"
    )

    logger.info(
        "Batch processing completed."
    )

    logger.info(
        "Processed : %d",
        processed_count,
    )

    logger.info(
        "Skipped : %d",
        skipped_count,
    )

    logger.info(
        "Failed : %d",
        failed_count,
    )

    return processed_articles

# =====================================================
# Build MongoDB Document
# =====================================================

def build_mongodb_document(
    processed_article: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a MongoDB-ready document.

    Parameters
    ----------
    processed_article : dict

    Returns
    -------
    dict
        MongoDB document.
    """

    logger.info(
        "Building MongoDB document."
    )

    if not isinstance(
        processed_article,
        dict,
    ):

        logger.warning(
            "Processed article must be a dictionary."
        )

        return {}

    document = {

        # -----------------------------
        # Original Data
        # -----------------------------

        "title": processed_article.get(
            "title",
            "",
        ),

        "content": processed_article.get(
            "content",
            "",
        ),

        "clean_content": processed_article.get(
            "clean_content",
            "",
        ),

        # -----------------------------
        # NLP Results
        # -----------------------------

        "summary": processed_article.get(
            "summary",
            "",
        ),

        "sentiment": processed_article.get(
            "sentiment",
            {},
        ),

        "category": processed_article.get(
            "category",
            {},
        ),

        "keywords": processed_article.get(
            "keywords",
            [],
        ),

        "entities": processed_article.get(
            "entities",
            [],
        ),

        "embedding": processed_article.get(
            "embedding",
            [],
        ),

        # -----------------------------
        # Article Metadata
        # -----------------------------

        "source": processed_article.get(
            "source",
            DEFAULT_SOURCE,
        ),

        "url": processed_article.get(
            "url",
            "",
        ),

        "published_at": processed_article.get(
            "published_at",
            "",
        ),

        # -----------------------------
        # Pipeline Metadata
        # -----------------------------

        "metadata": processed_article.get(
            "metadata",
            {},
        ),

        "statistics": processed_article.get(
            "statistics",
            {},
        ),

        # -----------------------------
        # Database Timestamp
        # -----------------------------

        "created_at": datetime.utcnow(),

    }

    logger.info(
        "MongoDB document created."
    )

    return document
# =====================================================
# Validate MongoDB Document
# =====================================================

def validate_document(
    document: dict[str, Any],
) -> tuple[bool, str]:
    """
    Validate a MongoDB document.

    Returns
    -------
    tuple
        (True, "Valid")
        (False, "Reason")
    """

    if not isinstance(document, dict):

        return False, "Document must be a dictionary."

    required_fields = [

        "title",
        "content",
        "clean_content",
        "summary",
        "sentiment",
        "category",
        "keywords",
        "entities",
        "embedding",
        "metadata",
        "statistics",
        "created_at",

    ]

    for field in required_fields:

        if field not in document:

            return False, f"Missing field: {field}"

    if not isinstance(document["keywords"], list):

        return False, "keywords must be list."

    if not isinstance(document["entities"], list):

        return False, "entities must be list."

    if not isinstance(document["embedding"], list):

        return False, "embedding must be list."

    if len(document["embedding"]) == 0:

        return False, "embedding is empty."

    return True, "Valid"