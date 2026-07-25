"""
=====================================================
Named Entity Recognition (NER)
=====================================================

Extracts named entities from cleaned article text.

Supported Entities
------------------
PERSON   : People
ORG      : Organizations
GPE      : Countries, Cities, States
LOC      : Locations
DATE     : Dates
EVENT    : Events
PRODUCT  : Products
MONEY    : Monetary values
"""

from nlp.models import ner_model

# =====================================================
# Allowed Entity Labels
# =====================================================

ALLOWED_LABELS = {
    "PERSON",
    "ORG",
    "GPE",
    "LOC",
    "DATE",
    "EVENT",
    "PRODUCT",
    "MONEY"
}


# =====================================================
# Noise Words
# =====================================================

NOISE_WORDS = {
    "Synopsis",
    "Summary",
    "Highlights",
    "Advertisement",
    "Related Stories",
    "Read More",
    "Breaking News",
    "Key Highlights"
}


# =====================================================
# Extract Named Entities
# =====================================================

def extract_entities(text):
    """
    Extract named entities from text.

    Parameters
    ----------
    text : str

    Returns
    -------
    dict
        Dictionary containing extracted entities grouped
        by their entity labels.
    """

    if not text or not text.strip():
        return {}

    try:

        doc = ner_model(text)

        entities = {}

        for ent in doc.ents:

            # Ignore unwanted entity labels
            if ent.label_ not in ALLOWED_LABELS:
                continue

            label = ent.label_

            # Normalize whitespace
            value = " ".join(ent.text.split()).strip()

            # Ignore empty or tiny entities
            if len(value) < 2:
                continue

            # Ignore standalone noise words
            if value.lower() in {word.lower() for word in NOISE_WORDS}:
                continue

            # Ignore entities beginning with noise words
            if any(
                value.lower().startswith(word.lower() + " ")
                for word in NOISE_WORDS
            ):
                continue

            # Create label bucket
            if label not in entities:
                entities[label] = []

            # Remove duplicates (case-insensitive)
            existing = {
                entity.lower()
                for entity in entities[label]
            }

            if value.lower() not in existing:
                entities[label].append(value)

        return entities

    except Exception as e:

        print(f"NER Error: {e}")

        return {}