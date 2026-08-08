from nlp.keyword_extractor import (
    is_valid_input,
    preprocess_text,
    clean_phrase,
    is_valid_phrase,
)

print("=" * 60)
print("VALIDATION")
print("=" * 60)

print(
    is_valid_input(
        "Apple introduced a new AI powered MacBook with improved battery life."
    )
)

print()

print("=" * 60)
print("PREPROCESS")
print("=" * 60)

print(
    preprocess_text(
        "   Apple      launched    AI    MacBook   "
    )
)

print()

print("=" * 60)
print("PHRASE CLEAN")
print("=" * 60)

print(
    clean_phrase(
        "   MacBook     Pro   "
    )
)

print()

print("=" * 60)
print("PHRASE VALIDATION")
print("=" * 60)

print(
    is_valid_phrase(
        "MacBook Pro"
    )
)

print(
    is_valid_phrase(
        "said"
    )
)
# =====================================================
# Named Entity Configuration
# =====================================================

VALID_ENTITY_TYPES = {

    "PERSON",

    "ORG",

    "PRODUCT",

    "GPE",

    "LOC",

    "EVENT",

    "WORK_OF_ART",

}

# =====================================================
# Named Entity Extraction
# =====================================================

def extract_named_entities(
    doc,
) -> list[str]:
    """
    Extract named entities from article.
    """

    entities = []

    seen = set()

    for entity in doc.ents:

        if entity.label_ not in VALID_ENTITY_TYPES:

            continue

        phrase = clean_phrase(
            entity.text
        )

        if not is_valid_phrase(
            phrase
        ):

            continue

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        entities.append(
            phrase
        )

    return entities


# =====================================================
# Noun Chunk Extraction
# =====================================================

def extract_noun_chunks(
    doc,
) -> list[str]:
    """
    Extract noun phrases.
    """

    chunks = []

    seen = set()

    for chunk in doc.noun_chunks:

        phrase = clean_phrase(
            chunk.text
        )

        if not is_valid_phrase(
            phrase
        ):

            continue

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        chunks.append(
            phrase
        )

    return chunks


# =====================================================
# Candidate Pool Builder
# =====================================================

def build_candidate_pool(
    doc,
) -> list[str]:
    """
    Build candidate keyword pool.
    """

    candidates = []

    seen = set()

    for phrase in extract_named_entities(
        doc
    ):

        key = phrase.lower()

        seen.add(key)

        candidates.append(
            phrase
        )

    for phrase in extract_noun_chunks(
        doc
    ):

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        candidates.append(
            phrase
        )

    return candidates


# =====================================================
# Candidate Filter
# =====================================================

def filter_candidates(
    candidates: list[str],
) -> list[str]:
    """
    Remove duplicate and invalid candidates.
    """

    cleaned = []

    seen = set()

    for phrase in candidates:

        phrase = clean_phrase(
            phrase
        )

        if not is_valid_phrase(
            phrase
        ):

            continue

        key = phrase.lower()

        if key in seen:

            continue

        seen.add(key)

        cleaned.append(
            phrase
        )

    return cleaned