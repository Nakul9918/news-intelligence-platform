"""
=====================================================
Named Entity Recognition (NER)
Project : News Intelligence Platform
Module  : nlp.ner
Version : 1.0 (Production)
=====================================================

This module provides Named Entity Recognition (NER)
using GLiNER for news articles.

Supported Entity Types
----------------------
- Person
- Organization
- Company
- Product
- Technology
- Location
- Country
- City
- Event
"""

from __future__ import annotations

import logging
import re
from typing import Any

from gliner import GLiNER

# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(__name__)

# =====================================================
# Model Configuration
# =====================================================

MODEL_NAME = "urchade/gliner_small-v2.1"

DEFAULT_LABELS = [
    "Person",
    "Organization",
    "Company",
    "Location",
    "Country",
    "City",
    "Product",
    "Technology",
    "Event",
]

DEFAULT_THRESHOLD = 0.50

# =====================================================
# Validation Configuration
# =====================================================

MIN_INPUT_CHARACTERS = 20
MIN_INPUT_WORDS = 3
MAX_INPUT_CHARACTERS = 5000

# =====================================================
# Load GLiNER Model
# =====================================================

try:

    logger.info(
        "Loading GLiNER model: %s",
        MODEL_NAME,
    )

    ner_model = GLiNER.from_pretrained(
        MODEL_NAME
    )

    logger.info(
        "GLiNER model loaded successfully."
    )

except Exception:

    logger.exception(
        "Failed to load GLiNER model."
    )

    raise

# =====================================================
# Input Validation
# =====================================================

def is_valid_input(text: str) -> bool:
    """
    Validate input text before processing.

    Parameters
    ----------
    text : str

    Returns
    -------
    bool
    """

    if not isinstance(text, str):
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

def preprocess_text(text: str) -> str:
    """
    Normalize article text before entity extraction.
    """

    text = text.replace("\n", " ")

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = text.strip()

    if len(text) > MAX_INPUT_CHARACTERS:
        text = text[:MAX_INPUT_CHARACTERS]

    return text


# =====================================================
# Entity Cleaning
# =====================================================

def clean_entity(entity: str) -> str:
    """
    Clean extracted entity.
    """

    entity = entity.strip()

    entity = re.sub(
        r"\s+",
        " ",
        entity,
    )

    return entity


# =====================================================
# Entity Validation
# =====================================================

def is_valid_entity(entity: str) -> bool:
    """
    Validate extracted entity.
    """

    entity = clean_entity(entity)

    if not entity:
        return False

    if len(entity) < 2:
        return False

    return True


# =====================================================
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Check whether the NER module is ready.
    """

    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "loaded": ner_model is not None,
        "labels": DEFAULT_LABELS,
        "threshold": DEFAULT_THRESHOLD,
    }


# =====================================================
# Public Exports
# =====================================================

__all__ = [
    "extract_entities",
    "extract_entities_batch",
    "health_check",
]
# =====================================================
# Raw Entity Extraction
# =====================================================

def extract_raw_entities(
    text: str,
    labels: list[str] | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict[str, Any]]:
    """
    Extract raw entities from text using GLiNER.

    Parameters
    ----------
    text : str
        Input article text.

    labels : list[str] | None
        Entity labels to extract.
        If None, DEFAULT_LABELS will be used.

    threshold : float
        Minimum confidence score (0.0 - 1.0).

    Returns
    -------
    list[dict[str, Any]]
        Raw entities predicted by GLiNER.
    """

    # -------------------------------
    # Validate Input
    # -------------------------------

    if not is_valid_input(text):
        logger.warning("Invalid input text received.")
        return []

    # -------------------------------
    # Validate Threshold
    # -------------------------------

    if not isinstance(threshold, (int, float)):
        logger.warning("Threshold must be numeric.")
        return []

    threshold = float(threshold)

    if not 0.0 <= threshold <= 1.0:
        logger.warning(
            "Threshold %.2f is outside valid range (0.0 - 1.0).",
            threshold,
        )
        return []

    # -------------------------------
    # Prepare Labels
    # -------------------------------

    if labels is None:
        labels = DEFAULT_LABELS

    elif not isinstance(labels, list):
        logger.warning("Labels must be a list.")
        return []

    elif len(labels) == 0:
        logger.warning("Label list is empty.")
        return []

    # -------------------------------
    # Preprocess Text
    # -------------------------------

    text = preprocess_text(text)

    # -------------------------------
    # Entity Extraction
    # -------------------------------

    try:

        entities = ner_model.predict_entities(
            text=text,
            labels=labels,
            threshold=threshold,
        )

        logger.info(
            "Extracted %d raw entities.",
            len(entities),
        )

        return entities

    except Exception:

        logger.exception(
            "GLiNER entity extraction failed."
        )

        return []
# =====================================================
# Generic Entity Filter
# =====================================================

GENERIC_ENTITIES = {
    "article",
    "company",
    "country",
    "city",
    "event",
    "location",
    "news",
    "organization",
    "person",
    "product",
    "technology",
}

# =====================================================
# Entity Normalization
# =====================================================

def normalize_entity(entity: str) -> str:
    """
    Normalize extracted entity text.
    """

    if not isinstance(entity, str):
        return ""

    entity = entity.strip()

    entity = re.sub(r"\s+", " ", entity)

    entity = re.sub(
        r"[^\w\s&./-]",
        "",
        entity,
    )

    return entity.strip()


# =====================================================
# Label Normalization
# =====================================================

def normalize_label(label: str) -> str:
    """
    Normalize entity label.
    """

    if not isinstance(label, str):
        return "Unknown"

    label = label.strip()

    if not label:
        return "Unknown"

    return label.title()


# =====================================================
# Entity Validation
# =====================================================

def is_valid_normalized_entity(entity: str) -> bool:
    """
    Validate normalized entity.
    """

    if not entity:
        return False

    if len(entity) < 2:
        return False

    if entity.isdigit():
        return False

    if entity.lower() in GENERIC_ENTITIES:
        return False

    return True


# =====================================================
# Standardize Entity
# =====================================================

def standardize_entity(
    raw_entity: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Convert a raw GLiNER entity into a standard format.
    """

    entity = normalize_entity(
        raw_entity.get("text", "")
    )

    if not is_valid_normalized_entity(entity):
        return None

    confidence = float(
        raw_entity.get("score", 0.0)
    )

    confidence = max(
        0.0,
        min(confidence, 1.0),
    )

    return {
        "entity": entity,
        "label": normalize_label(
            raw_entity.get("label", "")
        ),
        "confidence": round(confidence, 4),
    }


# =====================================================
# Normalize Entity List
# =====================================================

def normalize_entities(
    raw_entities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Normalize all raw entities returned by GLiNER.
    """

    if not raw_entities:
        return []

    normalized_entities: list[dict[str, Any]] = []

    for raw_entity in raw_entities:

        entity = standardize_entity(raw_entity)

        if entity is not None:
            normalized_entities.append(entity)

    logger.info(
        "Normalized %d entities.",
        len(normalized_entities),
    )

    return normalized_entities
# =====================================================
# Entity Key
# =====================================================

def entity_key(entity: dict[str, Any]) -> tuple[str, str]:
    """
    Generate a unique key for an entity.

    Duplicate detection is based on:
    - Entity text (case-insensitive)
    - Entity label
    """

    return (
        entity["entity"].casefold(),
        entity["label"].casefold(),
    )


# =====================================================
# Remove Duplicate Entities
# =====================================================

def deduplicate_entities(
    entities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Remove duplicate entities while keeping the
    highest-confidence occurrence.
    """

    if not entities:
        return []

    unique_entities: dict[
        tuple[str, str],
        dict[str, Any],
    ] = {}

    for entity in entities:

        key = entity_key(entity)

        existing = unique_entities.get(key)

        if existing is None:

            unique_entities[key] = entity

        elif entity["confidence"] > existing["confidence"]:

            unique_entities[key] = entity

    logger.info(
        "Removed %d duplicate entities.",
        len(entities) - len(unique_entities),
    )

    return list(unique_entities.values())


# =====================================================
# Sort Entities
# =====================================================

def sort_entities(
    entities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Sort entities by confidence (highest first),
    then alphabetically for deterministic output.
    """

    return sorted(
        entities,
        key=lambda entity: (
            -entity["confidence"],
            entity["entity"].casefold(),
            entity["label"].casefold(),
        ),
    )


# =====================================================
# Finalize Entities
# =====================================================

def finalize_entities(
    entities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Final processing before returning entities.

    Steps
    -----
    1. Remove duplicates
    2. Sort by confidence
    """

    if not entities:
        return []

    entities = deduplicate_entities(entities)

    entities = sort_entities(entities)

    logger.info(
        "Returning %d finalized entities.",
        len(entities),
    )

    return entities
# =====================================================
# Batch Entity Extraction
# =====================================================

def extract_entities_batch(
    articles: list[str],
    labels: list[str] | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[list[dict[str, Any]]]:
    """
    Extract entities from multiple news articles.

    Parameters
    ----------
    articles : list[str]
        List of article texts.

    labels : list[str] | None
        Entity labels to detect.

    threshold : float
        Confidence threshold.

    Returns
    -------
    list[list[dict[str, Any]]]
        One finalized entity list per article.
    """

    if not isinstance(articles, list):
        logger.warning("Input must be a list of article texts.")
        return []

    if not articles:
        logger.warning("Empty article list received.")
        return []

    results: list[list[dict[str, Any]]] = []

    processed = 0
    skipped = 0

    for index, article in enumerate(articles, start=1):

        try:

            if not is_valid_input(article):
                logger.warning(
                    "Skipping invalid article at index %d.",
                    index,
                )
                skipped += 1
                continue

            entities = extract_entities(
                text=article,
                labels=labels,
                threshold=threshold,
            )

            results.append(entities)
            processed += 1

        except Exception:

            logger.exception(
                "Failed to process article %d.",
                index,
            )

            skipped += 1

    logger.info(
        "Batch processing completed. "
        "Processed=%d | Skipped=%d",
        processed,
        skipped,
    )

    return results
# =====================================================
# Public Entity Extraction API
# =====================================================

def extract_entities(
    text: str,
    labels: list[str] | None = None,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict[str, Any]]:
    """
    Extract production-ready named entities from a news article.

    Processing Pipeline
    -------------------
    1. Validate input
    2. Preprocess text
    3. Extract raw entities
    4. Normalize entities
    5. Remove duplicates
    6. Sort by confidence

    Parameters
    ----------
    text : str
        News article text.

    labels : list[str] | None
        Entity labels to detect.
        If None, DEFAULT_LABELS will be used.

    threshold : float
        Confidence threshold.

    Returns
    -------
    list[dict[str, Any]]
        Final processed entities.

    Example
    -------
    [
        {
            "entity": "Apple",
            "label": "Company",
            "confidence": 0.9876
        },
        {
            "entity": "MacBook",
            "label": "Product",
            "confidence": 0.8742
        }
    ]
    """

    logger.info("Starting entity extraction.")

    if not is_valid_input(text):
        logger.warning("Invalid input text.")
        return []

    try:

        raw_entities = extract_raw_entities(
            text=text,
            labels=labels,
            threshold=threshold,
        )

        if not raw_entities:

            logger.info("No entities detected.")

            return []

        normalized_entities = normalize_entities(
            raw_entities
        )

        final_entities = finalize_entities(
            normalized_entities
        )

        logger.info(
            "Entity extraction completed successfully. "
            "Returned %d entities.",
            len(final_entities),
        )

        return final_entities

    except Exception:

        logger.exception(
            "Entity extraction pipeline failed."
        )

        return []


    