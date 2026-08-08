import logging

from transformers import pipeline

from config import (
    LOG_SEPARATOR,
)

logger = logging.getLogger(
    "CommonNER"
)
MODEL_NAME = (
    "dbmdz/bert-large-cased-finetuned-conll03-english"
)

DEFAULT_LANGUAGE = "en"

MIN_CONTENT_LENGTH = 30

DEFAULT_ENTITIES = []

logger.info(LOG_SEPARATOR)

logger.info(
    "Loading NER Model..."
)

logger.info(LOG_SEPARATOR)

NER_MODEL = pipeline(

    task="ner",

    model=MODEL_NAME,

    aggregation_strategy="simple",

)

logger.info(
    "NER Model Loaded Successfully."
)

logger.info(LOG_SEPARATOR)
def normalize_text(
    text
):
    """
    Normalize article text.
    """

    if not text:

        return ""

    text = str(
        text
    )

    text = " ".join(
        text.split()
    )

    return text.strip()
def has_content(
    text
):
    """
    Validate article.
    """

    if text is None:

        return False

    text = normalize_text(
        text
    )

    if len(text) < MIN_CONTENT_LENGTH:

        return False

    return True

# =====================================================
# Predict Entities
# =====================================================

def predict_entities(
    text
):
    """
    Extract named entities.
    """

    if not has_content(
        text
    ):

        return DEFAULT_ENTITIES

    text = normalize_text(
        text
    )

    try:

        predictions = NER_MODEL(
            text
        )

    except Exception as error:

        logger.exception(
            f"NER Prediction Failed : {error}"
        )

        return DEFAULT_ENTITIES

    entities = []

    seen = set()

    for entity in predictions:

        entity_text = entity.get(
            "word",
            ""
        ).strip()

        entity_label = entity.get(
            "entity_group",
            ""
        )

        entity_score = round(

            float(

                entity.get(
                    "score",
                    0.0
                )

            ),

            4,

        )

        if not entity_text:

            continue

        key = (
            entity_text.lower(),
            entity_label
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        entities.append(

            {

                "text": entity_text,

                "label": entity_label,

                "score": entity_score,

            }

        )

    return entities

# =====================================================
# Build Result
# =====================================================

def build_result(
    entities
):
    """
    Build standard NER result.
    """

    return {

        "entities": entities,

        "entity_count": len(
            entities
        ),

        "model": MODEL_NAME,

    }

# =====================================================
# Health Check
# =====================================================

def ner_health():
    """
    Display model information.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(
        "NER Model Health"
    )

    logger.info(LOG_SEPARATOR)

    logger.info(
        "Library            : Transformers"
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

    logger.info(LOG_SEPARATOR)

# =====================================================
# Self Test
# =====================================================
if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

    ner_health()

    sample_text = """
    Prime Minister Narendra Modi met
    Elon Musk in New Delhi.

    Tesla announced a new investment
    in India worth 2 billion dollars.
    """

    entities = predict_entities(
        sample_text
    )

    result = build_result(
        entities
    )

    logger.info(LOG_SEPARATOR)
    logger.info("NER Test")
    logger.info(LOG_SEPARATOR)

    logger.info(
        f"Entities : {result['entities']}"
    )

    logger.info(
        f"Count    : {result['entity_count']}"
    )

    logger.info(
        f"Model    : {result['model']}"
    )

    logger.info(LOG_SEPARATOR)