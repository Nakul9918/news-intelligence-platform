"""
=====================================================
News Content Cleaner
Version : 4.0
=====================================================
"""

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
            flags=re.IGNORECASE | re.MULTILINE
        )

    return text


# =====================================================
# Remove Boilerplate Lines
# =====================================================

def remove_boilerplate_lines(text, source=""):

    phrases = list(GLOBAL_REMOVE_PHRASES)

    phrases.extend(
        SOURCE_REMOVE_PHRASES.get(source, [])
    )

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        remove = False

        for phrase in phrases:

            if phrase.lower() in line.lower():

                remove = True
                break

        if not remove:

            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# =====================================================
# Remove Duplicate Lines
# =====================================================

def remove_duplicate_lines(text):

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

def remove_short_lines(text):

    cleaned = []

    for line in text.splitlines():

        line = line.strip()

        if len(line) < 3:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


# =====================================================
# Normalize White Spaces
# =====================================================

def normalize_spaces(text):

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# =====================================================
# Main Cleaner
# =====================================================

def clean_content(text, source=""):

    if not text:

        return ""

    # ------------------------------------------
    # Step 1 : Regex Cleaning
    # ------------------------------------------

    text = remove_regex(text)

    # ------------------------------------------
    # Step 2 : Remove Boilerplate Lines
    # ------------------------------------------

    text = remove_boilerplate_lines(
        text,
        source
    )

    # ------------------------------------------
    # Step 3 : Remove Duplicate Lines
    # ------------------------------------------

    text = remove_duplicate_lines(text)

    # ------------------------------------------
    # Step 4 : Remove Very Short Lines
    # ------------------------------------------

    text = remove_short_lines(text)

    # ------------------------------------------
    # Step 5 : Normalize Spaces
    # ------------------------------------------

    text = normalize_spaces(text)

    return text