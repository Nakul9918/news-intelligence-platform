import logging

from transformers import pipeline

from config import LOG_SEPARATOR


logger = logging.getLogger("CommonSummary")


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "facebook/bart-large-cnn"

DEFAULT_LANGUAGE = "en"

MIN_CONTENT_LENGTH = 100

MAX_INPUT_LENGTH = 1024

MAX_SUMMARY_LENGTH = 150

MIN_SUMMARY_LENGTH = 30


# ============================================================
# LOAD MODEL
# ============================================================

logger.info(LOG_SEPARATOR)

logger.info("Loading Summary Model...")

logger.info(LOG_SEPARATOR)


SUMMARY_MODEL = pipeline(
    task="summarization",
    model=MODEL_NAME,
    device=0
)


logger.info("Summary Model Loaded Successfully.")

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
# SUMMARY GENERATION
# ============================================================

def generate_summary(text):
    """
    Generate summary for an article.
    """

    text = normalize_text(text)

    if not has_content(text):
        return ""

    # Limit input because BART has a maximum input size.
    text = text[:MAX_INPUT_LENGTH * 4]

    result = SUMMARY_MODEL(
        text,
        max_length=MAX_SUMMARY_LENGTH,
        min_length=MIN_SUMMARY_LENGTH,
        do_sample=False
    )

    if not result:
        return ""

    summary = result[0].get(
        "summary_text",
        ""
    )

    return normalize_text(summary)


# ============================================================
# BUILD RESULT
# ============================================================

def build_result(summary):
    """
    Build standard summary result.
    """

    return {
        "summary": summary,
        "model": MODEL_NAME,
        "language": DEFAULT_LANGUAGE
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def summary_health():
    """
    Display summary model health information.
    """

    logger.info(LOG_SEPARATOR)

    logger.info("Summary Model Health")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Library            : Transformers"
    )

    logger.info(
        f"Model              : {MODEL_NAME}"
    )

    logger.info(
        f"Language           : {DEFAULT_LANGUAGE}"
    )

    logger.info(
        f"Minimum Length     : {MIN_CONTENT_LENGTH}"
    )

    logger.info(
        f"Maximum Summary    : {MAX_SUMMARY_LENGTH}"
    )

    logger.info(LOG_SEPARATOR)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    summary_health()

    sample_text = """
    Microsoft announced that it has acquired an artificial
    intelligence startup for 2 billion dollars. The company
    said the acquisition will strengthen its cloud business
    and expand its artificial intelligence capabilities.
    The deal is expected to help Microsoft compete in the
    rapidly growing AI market.
    """

    summary = generate_summary(
        sample_text
    )

    result = build_result(
        summary
    )

    logger.info(LOG_SEPARATOR)

    logger.info("Summary Test")

    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Summary : {result['summary']}"
    )

    logger.info(
        f"Model   : {result['model']}"
    )

    logger.info(LOG_SEPARATOR)