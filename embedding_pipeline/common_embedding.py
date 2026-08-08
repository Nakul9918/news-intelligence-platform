import logging

from sentence_transformers import SentenceTransformer

from config import LOG_SEPARATOR


logger = logging.getLogger("CommonEmbedding")


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_LANGUAGE = "en"

MIN_CONTENT_LENGTH = 30

EMBEDDING_DIMENSION = 384


# ============================================================
# LOAD MODEL
# ============================================================

logger.info(LOG_SEPARATOR)

logger.info("Loading Embedding Model...")

logger.info(LOG_SEPARATOR)


EMBEDDING_MODEL = SentenceTransformer(
    MODEL_NAME,
    device="cuda"
)


logger.info("Embedding Model Loaded Successfully.")

logger.info(LOG_SEPARATOR)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize article text.
    """

    if not text:
        return ""

    text = str(text)

    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# CONTENT VALIDATION
# ============================================================

def has_content(text):
    """
    Validate article content.
    """

    if text is None:
        return False

    text = normalize_text(text)

    if len(text) < MIN_CONTENT_LENGTH:
        return False

    return True


# ============================================================
# GENERATE EMBEDDING
# ============================================================

def generate_embedding(text):
    """
    Generate vector embedding for article text.
    """

    text = normalize_text(text)

    if not has_content(text):
        return []

    embedding = EMBEDDING_MODEL.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


# ============================================================
# BUILD RESULT
# ============================================================

def build_result(embedding):
    """
    Build standard embedding result.
    """

    return {
        "embedding": embedding,
        "dimension": len(embedding),
        "model": MODEL_NAME
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def embedding_health():
    """
    Display embedding model health.
    """

    logger.info(LOG_SEPARATOR)

    logger.info("Embedding Model Health")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Library            : SentenceTransformers"
    )

    logger.info(
        f"Model              : {MODEL_NAME}"
    )

    logger.info(
        f"Language           : {DEFAULT_LANGUAGE}"
    )

    logger.info(
        f"Dimension          : {EMBEDDING_DIMENSION}"
    )

    logger.info(LOG_SEPARATOR)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    embedding_health()

    sample_text = """
    Microsoft announced that it has acquired an artificial
    intelligence startup for 2 billion dollars. The company
    said the acquisition will strengthen its cloud business
    and expand its artificial intelligence capabilities.
    """

    embedding = generate_embedding(
        sample_text
    )

    result = build_result(
        embedding
    )

    logger.info(LOG_SEPARATOR)

    logger.info("Embedding Test")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Dimension : {result['dimension']}"
    )

    logger.info(
        f"Model     : {result['model']}"
    )

    logger.info(
        f"Vector Preview : {result['embedding'][:5]}"
    )

    logger.info(LOG_SEPARATOR)