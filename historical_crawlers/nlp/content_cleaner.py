import re

from nlp.cleaner_config import (
    GLOBAL_REMOVE_PHRASES,
    SOURCE_REMOVE_PHRASES,
    REGEX_PATTERNS
)

# =====================================================
# Remove Regex Patterns
# =====================================================

def remove_regex(text):

    for pattern in REGEX_PATTERNS:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    return text


# =====================================================
# Remove Global Boilerplate
# =====================================================

def remove_global_phrases(text):

    for phrase in GLOBAL_REMOVE_PHRASES:

        pattern = r"\b" + re.escape(phrase) + r"\b"

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    return text


# =====================================================
# Remove Source Specific Boilerplate
# =====================================================

def remove_source_phrases(text, source):

    phrases = SOURCE_REMOVE_PHRASES.get(source, [])

    for phrase in phrases:

        pattern = r"\b" + re.escape(phrase) + r"\b"

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    return text


# =====================================================
# Remove Duplicate Lines
# =====================================================

def remove_duplicate_lines(text):

    lines = text.splitlines()

    cleaned = []

    seen = set()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.lower() in seen:
            continue

        seen.add(line.lower())

        cleaned.append(line)

    return "\n".join(cleaned)


# =====================================================
# Remove Empty Lines
# =====================================================

def remove_empty_lines(text):

    lines = text.splitlines()

    lines = [line.strip() for line in lines if line.strip()]

    return "\n".join(lines)


# =====================================================
# Normalize Spaces
# =====================================================

def normalize_spaces(text):

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


# =====================================================
# Main Cleaner
# =====================================================

def clean_content(text, source=""):

    if not text:
        return ""

    text = remove_regex(text)

    text = remove_global_phrases(text)

    text = remove_source_phrases(text, source)

    text = remove_duplicate_lines(text)

    text = remove_empty_lines(text)

    text = normalize_spaces(text)

    return text