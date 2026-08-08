"""
=====================================================
Sentence Embeddings
Project : News Intelligence Platform
Module  : nlp.embeddings
Version : 1.0 (Production)
=====================================================

Generate semantic embeddings for news articles.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from sentence_transformers import SentenceTransformer

# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(__name__)

# =====================================================
# Model Configuration
# =====================================================

MODEL_NAME = "all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384

NORMALIZE_EMBEDDINGS = True

# =====================================================
# Validation Configuration
# =====================================================

MIN_INPUT_CHARACTERS = 20
MIN_INPUT_WORDS = 3
MAX_INPUT_CHARACTERS = 5000

# =====================================================
# Load Embedding Model
# =====================================================

try:

    logger.info(
        "Loading embedding model: %s",
        MODEL_NAME,
    )

    embedding_model = SentenceTransformer(
        MODEL_NAME
    )

    logger.info(
        "Embedding model loaded successfully."
    )

except Exception:

    logger.exception(
        "Failed to load embedding model."
    )

    raise

# =====================================================
# Input Validation
# =====================================================

def is_valid_input(text: str) -> bool:
    """
    Validate input text.
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
    Normalize input text.
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
# Health Check
# =====================================================

def health_check() -> dict[str, Any]:
    """
    Check whether the embedding module is ready.
    """

    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "dimension": EMBEDDING_DIMENSION,
        "loaded": embedding_model is not None,
        "normalized": NORMALIZE_EMBEDDINGS,
    }
# =====================================================
# Generate Embedding
# =====================================================

def generate_embedding(
    text: str,
) -> list[float]:
    """
    Generate a normalized embedding for a single text.

    Parameters
    ----------
    text : str
        Input article text.

    Returns
    -------
    list[float]
        Embedding vector.
        Returns an empty list if generation fails.
    """

    logger.info("Starting embedding generation.")

    if not is_valid_input(text):
        logger.warning("Invalid input text.")
        return []

    text = preprocess_text(text)

    try:

        embedding = embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
        )

        embedding = embedding.tolist()

        logger.info(
            "Embedding generated successfully. Dimension=%d",
            len(embedding),
        )

        return embedding

    except Exception:

        logger.exception(
            "Embedding generation failed."
        )

        return []
# =====================================================
# Batch Embedding Generation
# =====================================================

def generate_embeddings_batch(
    texts: list[str],
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.

    Parameters
    ----------
    texts : list[str]
        List of article texts.

    Returns
    -------
    list[list[float]]
        List of embedding vectors.
    """

    if not isinstance(texts, list):
        logger.warning("Input must be a list of texts.")
        return []

    if not texts:
        logger.warning("Empty text list received.")
        return []

    valid_texts = []

    for text in texts:

        if not is_valid_input(text):
            continue

        valid_texts.append(
            preprocess_text(text)
        )

    if not valid_texts:
        logger.warning("No valid texts found.")
        return []

    try:

        embeddings = embedding_model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
        )

        embeddings = embeddings.tolist()

        logger.info(
            "Generated %d embeddings.",
            len(embeddings),
        )

        return embeddings

    except Exception:

        logger.exception(
            "Batch embedding generation failed."
        )

        return []
# =====================================================
# Public Embedding API
# =====================================================

def extract_embedding(
    text: str,
) -> list[float]:
    """
    Generate a production-ready embedding for a single article.

    Parameters
    ----------
    text : str
        News article text.

    Returns
    -------
    list[float]
        Embedding vector.
    """

    logger.info("Starting embedding extraction.")

    embedding = generate_embedding(text)

    if not embedding:

        logger.warning(
            "Embedding extraction failed."
        )

        return []

    logger.info(
        "Embedding extraction completed successfully."
    )

    return embedding


# =====================================================
# Public Batch Embedding API
# =====================================================

def extract_embeddings_batch(
    texts: list[str],
) -> list[list[float]]:
    """
    Generate embeddings for multiple articles.

    Parameters
    ----------
    texts : list[str]
        List of article texts.

    Returns
    -------
    list[list[float]]
        List of embedding vectors.
    """

    logger.info(
        "Starting batch embedding extraction."
    )

    embeddings = generate_embeddings_batch(
        texts
    )

    logger.info(
        "Batch embedding extraction completed. "
        "Generated %d embeddings.",
        len(embeddings),
    )

    return embeddings
