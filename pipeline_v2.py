"""
=====================================================
News Processing Pipeline
Project : News Intelligence Platform
Module  : pipeline_v2
Version : 2.0 (Production)
=====================================================

This module orchestrates all NLP components.

Workflow
--------
Raw Article
      │
      ▼
Content Cleaner
      ▼
Summarizer
      ▼
Sentiment
      ▼
Category
      ▼
Keywords
      ▼
NER
      ▼
Embeddings
      ▼
MongoDB
      ▼
Elasticsearch
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

print("Importing content_cleaner...")
from nlp.content_cleaner import clean_content
print("✓ content_cleaner")

print("Importing summarizer...")
from nlp.summarizer import generate_summary
print("✓ summarizer")

print("Importing sentiment...")
from nlp.sentiment import predict_sentiment
print("✓ sentiment")

print("Importing category...")
from nlp.category_classifier import classify_article
print("✓ category")

print("Importing keywords...")
from nlp.keyword_extractor import extract_keywords
print("✓ keywords")

print("Importing ner...")
from nlp.ner import extract_entities
print("✓ ner")

print("Importing embeddings...")
from nlp.embeddings import extract_embedding
print("✓ embeddings")

# =====================================================
# Configuration
# =====================================================

PIPELINE_NAME = "News Intelligence Pipeline"

PIPELINE_VERSION = "2.0"

DEFAULT_SOURCE = "Unknown"

DEFAULT_LANGUAGE = "en"

# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Check pipeline health.
    """

    return {

        "status": "healthy",

        "pipeline": PIPELINE_NAME,

        "version": PIPELINE_VERSION,

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
# Metadata
# =====================================================

def build_metadata() -> dict[str, Any]:
    """
    Build pipeline metadata.
    """

    return {

        "pipeline": PIPELINE_NAME,

        "version": PIPELINE_VERSION,

        "processed_at": datetime.utcnow().isoformat(),

    }


# =====================================================
# Statistics
# =====================================================

def build_statistics(
    start_time: float,
) -> dict[str, Any]:
    """
    Build processing statistics.
    """

    return {

        "processing_time": round(

            time.perf_counter() - start_time,

            4,

        )

    }


# =====================================================
# Public API
# =====================================================

__all__ = [

    "health_check",

    "process_article",

    "process_articles_batch",

    "build_mongodb_document",

    "validate_document",

]