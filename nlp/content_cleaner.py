"""
=====================================================
News Content Cleaner
Version : 5.0
=====================================================
"""

import re
import unicodedata

from nlp.cleaner_config import (
    GLOBAL_REMOVE_PHRASES,
    SOURCE_REMOVE_PHRASES,
    REGEX_PATTERNS
)


# =====================================================
# Unicode Normalization
# =====================================================

def normalize_unicode(text: str) -> str:
    """Normalize unicode characters."""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "\xa0": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "−": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# =====================================================
# Remove Regex Patterns
# =====================================================

def remove_regex(text: str) -> str:

    for pattern in REGEX_PATTERNS:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

    return text


# =====================================================
# Remove Boilerplate Lines
# =====================================================

def remove_boilerplate_lines(text: str, source: str = "") -> str:

    phrases = list(GLOBAL_REMOVE_PHRASES)
    phrases.extend(SOURCE_REMOVE_PHRASES.get(source, []))

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if any(phrase.lower() in line.lower() for phrase in phrases):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# =====================================================
# Remove Duplicate Lines
# =====================================================

def remove_duplicate_lines(text: str) -> str:

    seen = set()
    cleaned = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        normalized = line.lower()

        if normalized in seen:
            continue

        seen.add(normalized)

        cleaned.append(line)

    return "\n".join(cleaned)


# =====================================================
# Remove Very Short Junk Lines
# =====================================================

def remove_short_lines(text: str) -> str:

    cleaned = []

    for line in text.splitlines():

        line = line.strip()

        if len(line) < 3:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)

# =====================================================
# Remove Standalone Headings
# =====================================================

HEADINGS_TO_REMOVE = {
    "Synopsis",
    "Summary",
    "Highlights",
    "Advertisement",
    "Related Stories",
    "Read More",
    "Breaking News",
    "Key Highlights"
}


def remove_headings(text: str) -> str:

    cleaned = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.lower() in {h.lower() for h in HEADINGS_TO_REMOVE}:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)
# =====================================================
# Remove URLs
# =====================================================

def remove_urls(text: str) -> str:

    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"https\S+", "", text)
    text = re.sub(r"www\.\S+", "", text)

    return text


# =====================================================
# Remove Empty Brackets
# =====================================================

def remove_empty_brackets(text: str) -> str:

    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\[\s*\]", "", text)
    text = re.sub(r"\{\s*\}", "", text)

    return text


# =====================================================
# Normalize Punctuation
# =====================================================

def normalize_punctuation(text: str) -> str:

    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\?{2,}", "?", text)

    return text


# =====================================================
# Normalize White Spaces
# =====================================================

def normalize_spaces(text: str) -> str:

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# =====================================================
# Main Cleaner
# =====================================================

def clean_content(text: str, source: str = "") -> str:
    """
    Clean extracted news article.

    Steps:
    1. Unicode normalization
    2. Regex cleaning
    3. Boilerplate removal
    4. Duplicate line removal
    5. Short line removal
    6. Heading removal
    7. URL removal
    8. Empty bracket removal
    9. Punctuation normalization
    10. Whitespace normalization
    """

    if not text:
        return ""

    # Step 1
    text = normalize_unicode(text)

    # Step 2
    text = remove_regex(text)

    # Step 3
    text = remove_boilerplate_lines(text, source)

    # Step 4
    text = remove_duplicate_lines(text)

    # Step 5
    text = remove_short_lines(text)

    # Step 6
    text = remove_headings(text)

    # Step 7
    text = remove_urls(text)

    # Step 8
    text = remove_empty_brackets(text)

    # Step 9
    text = normalize_punctuation(text)

    # Step 10
    text = normalize_spaces(text)

    return text