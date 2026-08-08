"""
=====================================================
News Content Cleaner
Version : 6.0
Production Ready
=====================================================

Author : CDAC Project

Purpose:
Clean raw news article text before NLP processing.

Pipeline:

Raw Text
    ↓
Unicode Normalization
    ↓
HTML Entity Decode
    ↓
Whitespace Cleanup
    ↓
Regex Cleaning
    ↓
Boilerplate Removal
    ↓
Duplicate Removal
    ↓
Validation
    ↓
Clean Text
"""

from __future__ import annotations

import html
import logging
import re
import unicodedata

from typing import Set

from nlp.cleaner_config import (
    GLOBAL_REMOVE_PHRASES,
    SOURCE_REMOVE_PHRASES,
    REGEX_PATTERNS,
)

# =====================================================
# Logger
# =====================================================

logger = logging.getLogger(__name__)

# =====================================================
# Debug
# =====================================================

DEBUG = False

# =====================================================
# Validation
# =====================================================

MIN_CHARACTERS = 30
MIN_WORDS = 5

# =====================================================
# Precompiled Regex
# =====================================================

URL_RE = re.compile(
    r"https?://\S+|www\.\S+",
    flags=re.IGNORECASE,
)

MULTI_SPACE_RE = re.compile(r"[ \t]+")

MULTI_NEWLINE_RE = re.compile(r"\n{3,}")

EMPTY_PAREN_RE = re.compile(r"\(\s*\)")

EMPTY_BRACKET_RE = re.compile(r"\[\s*\]")

EMPTY_BRACE_RE = re.compile(r"\{\s*\}")

MULTI_DOT_RE = re.compile(r"\.{2,}")

MULTI_EXCLAMATION_RE = re.compile(r"!{2,}")

MULTI_QUESTION_RE = re.compile(r"\?{2,}")

# =====================================================
# Unicode Translation
# =====================================================

UNICODE_TRANSLATION = str.maketrans(
    {
        "\xa0": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
    }
)

UNICODE_REPLACEMENTS = {

    "“": '"',
    "”": '"',

    "‘": "'",
    "’": "'",

    "—": "-",
    "–": "-",
    "−": "-",

}

# =====================================================
# Debug Helper
# =====================================================

def debug(message: str) -> None:
    """
    Print debug message only when DEBUG=True.
    """

    if DEBUG:
        print(message)

# =====================================================
# Unicode Normalization
# =====================================================

def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters.
    """

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    text = text.translate(UNICODE_TRANSLATION)

    for old, new in UNICODE_REPLACEMENTS.items():
        text = text.replace(old, new)

    return text

# =====================================================
# Decode HTML
# =====================================================

def decode_html_entities(text: str) -> str:
    """
    Decode HTML entities.

    Example:

    &amp;
    &#39;
    &nbsp;
    """

    if not text:
        return ""

    return html.unescape(text)

# =====================================================
# Normalize One Line
# =====================================================

def normalize_line(line: str) -> str:
    """
    Normalize line for duplicate comparison.
    """

    line = normalize_unicode(line)

    line = line.lower()

    line = re.sub(r"\s+", " ", line)

    return line.strip()

# =====================================================
# Validation
# =====================================================

def is_valid_content(text: str) -> bool:
    """
    Validate cleaned article.
    """

    if not text:
        return False

    if len(text) < MIN_CHARACTERS:
        return False

    if len(text.split()) < MIN_WORDS:
        return False

    return True
# =====================================================
# Compile Cleaner Regex Once
# =====================================================

COMPILED_REGEX_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE | re.MULTILINE)
    for pattern in REGEX_PATTERNS
]

# =====================================================
# Build Phrase Cache
# =====================================================

def build_phrase_cache(source: str = "") -> Set[str]:
    """
    Merge global and source-specific phrases.

    Duplicate phrases are automatically removed.
    """

    phrases: Set[str] = set()

    for phrase in GLOBAL_REMOVE_PHRASES:
        phrase = phrase.strip().lower()

        if phrase:
            phrases.add(phrase)

    for phrase in SOURCE_REMOVE_PHRASES.get(source, []):

        phrase = phrase.strip().lower()

        if phrase:
            phrases.add(phrase)

    return phrases

# =====================================================
# Exact Match
# =====================================================

def is_exact_match(
    line: str,
    phrases: Set[str],
) -> bool:
    """
    True only if the whole line exactly matches.
    """

    return line in phrases

# =====================================================
# Prefix Match
# =====================================================
def is_prefix_match(
    line: str,
    phrases: Set[str],
) -> bool:
    """
    Match boilerplate that starts with a configured phrase.
    """

    for phrase in phrases:

        if line.startswith(phrase + " "):
            return True

    return False
# =====================================================
# Suffix Match
# =====================================================

def is_suffix_match(
    line: str,
    phrases: Set[str],
) -> bool:
    """
    Match

    ...Read More

    ...Continue Reading
    """

    for phrase in phrases:

        if line.endswith(" " + phrase):
            return True

    return False

# =====================================================
# Boilerplate Detection
# =====================================================

def is_boilerplate_line(
    line: str,
    phrases: Set[str],
) -> bool:
    """
    Safe boilerplate detection.

    We intentionally DO NOT use

        phrase in line

    because it breaks valid news such as

        Prime Minister
        Opinion Poll
        Trending Stocks
    """

    if not line:
        return False

    line = normalize_line(line)

    if is_exact_match(line, phrases):
        return True

    if is_prefix_match(line, phrases):
        return True

    if is_suffix_match(line, phrases):
        return True

    return False

# =====================================================
# Regex Cleaning
# =====================================================

def remove_regex(text: str) -> str:
    """
    Remove text using configured regex patterns.
    """

    if not text:
        return ""

    before = len(text)

    for pattern in COMPILED_REGEX_PATTERNS:
        text = pattern.sub("", text)

    if DEBUG:

        debug(
            f"[Regex] {before} -> {len(text)}"
        )

    return text
# =====================================================
# Remove Boilerplate Lines
# =====================================================

def remove_boilerplate_lines(
    text: str,
    source: str = "",
) -> str:
    """
    Remove boilerplate lines such as:

    - Advertisement
    - Subscribe
    - Read More
    - Login
    - ET Prime

    using the configured phrase cache.
    """

    if not text:
        return ""

    phrases = build_phrase_cache(source)

    cleaned_lines = []

    removed_count = 0

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if is_boilerplate_line(line, phrases):

            removed_count += 1

            if DEBUG:
                debug(f"[Boilerplate Removed] {line}")

            continue

        cleaned_lines.append(line)

    if DEBUG:
        debug(f"[Boilerplate] Removed {removed_count} lines")

    return "\n".join(cleaned_lines)


# =====================================================
# Remove Duplicate Lines
# =====================================================

def remove_duplicate_lines(text: str) -> str:
    """
    Remove duplicate lines while preserving order.
    """

    if not text:
        return ""

    seen = set()

    cleaned = []

    duplicate_count = 0

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        normalized = normalize_line(line)

        if normalized in seen:

            duplicate_count += 1
            continue

        seen.add(normalized)

        cleaned.append(line)

    if DEBUG:
        debug(f"[Duplicate] Removed {duplicate_count} duplicate lines")

    return "\n".join(cleaned)


# =====================================================
# Remove Very Short Junk Lines
# =====================================================

SHORT_WORD_WHITELIST = {
    "AI",
    "UK",
    "US",
    "EU",
    "UN",
    "PM",
    "Xi",
}


def remove_short_lines(text: str) -> str:
    """
    Remove meaningless short lines while preserving
    useful abbreviations.
    """

    if not text:
        return ""

    cleaned = []

    removed = 0

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line in SHORT_WORD_WHITELIST:
            cleaned.append(line)
            continue

        if len(line) < 3:

            removed += 1
            continue

        cleaned.append(line)

    if DEBUG:
        debug(f"[Short Lines] Removed {removed}")

    return "\n".join(cleaned)


# =====================================================
# Standalone Headings
# =====================================================

HEADINGS_TO_REMOVE = {
    "Synopsis",
    "Summary",
    "Highlights",
    "Key Highlights",
    "Advertisement",
    "Related Stories",
    "Related News",
    "Read More",
    "Breaking News",
    "Latest News",
    "Must Read",
}

# =====================================================
# Precompute Normalized Headings (Built Once)
# =====================================================

NORMALIZED_HEADINGS = {
    normalize_line(heading)
    for heading in HEADINGS_TO_REMOVE
}
# =====================================================
# Remove Standalone Headings
# =====================================================
def remove_headings(text: str) -> str:
    """
    Remove standalone headings that are not part
    of the article body.
    """

    if not text:
        return ""

    cleaned = []

    removed = 0

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        normalized = normalize_line(line)

        if normalized in NORMALIZED_HEADINGS:

            removed += 1

            if DEBUG:
                debug(f"[Heading Removed] {line}")

            continue

        cleaned.append(line)

    if DEBUG:
        debug(f"[Heading] Removed {removed}")

    return "\n".join(cleaned)


# =====================================================
# Remove Control Characters
# =====================================================

CONTROL_CHAR_RE = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"
)

def remove_control_characters(text: str) -> str:
    """
    Remove invisible ASCII control characters.
    """

    if not text:
        return ""

    return CONTROL_CHAR_RE.sub("", text)


# =====================================================
# Remove URLs
# =====================================================

def remove_urls(text: str) -> str:
    """
    Remove URLs from article text.
    """

    if not text:
        return ""

    return URL_RE.sub("", text)


# =====================================================
# Remove Empty Brackets
# =====================================================

def remove_empty_brackets(text: str) -> str:
    """
    Remove empty (), [] and {}.
    """

    if not text:
        return ""

    text = EMPTY_PAREN_RE.sub("", text)
    text = EMPTY_BRACKET_RE.sub("", text)
    text = EMPTY_BRACE_RE.sub("", text)

    return text


# =====================================================
# Normalize Punctuation
# =====================================================

def normalize_punctuation(text: str) -> str:
    """
    Replace repeated punctuation with a single character.
    """

    if not text:
        return ""

    text = MULTI_DOT_RE.sub(".", text)
    text = MULTI_EXCLAMATION_RE.sub("!", text)
    text = MULTI_QUESTION_RE.sub("?", text)

    return text


# =====================================================
# Normalize Spaces
# =====================================================

def normalize_spaces(text: str) -> str:
    """
    Normalize spaces and blank lines.
    """

    if not text:
        return ""

    cleaned_lines = []

    for line in text.splitlines():

        line = MULTI_SPACE_RE.sub(" ", line).strip()

        if line:
            cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    text = MULTI_NEWLINE_RE.sub("\n\n", text)

    return text


# =====================================================
# Final Cleanup
# =====================================================

def final_cleanup(text: str) -> str:
    """
    Final cleanup before validation.
    """

    if not text:
        return ""

    text = normalize_spaces(text)

    return text.strip()


# =====================================================
# Main Cleaning Pipeline
# =====================================================

# def clean_content(
#     text: str,
#     source: str = "",
# ) -> str:
#     """
#     Main content cleaning pipeline.
#     """

#     if not text:
#         return ""

#     try:

#         # Initial normalization
#         text = normalize_unicode(text)
#         text = decode_html_entities(text)
#         text = remove_control_characters(text)

#         # Pattern cleaning
#         text = remove_regex(text)
#         text = remove_boilerplate_lines(text, source)

#         # Structural cleaning
#         text = remove_duplicate_lines(text)
#         text = remove_headings(text)
#         text = remove_short_lines(text)

#         # Text cleanup
#         text = remove_urls(text)
#         text = remove_empty_brackets(text)
#         text = normalize_punctuation(text)
#         text = normalize_spaces(text)
#         text = final_cleanup(text)

#         # Validation
#         if not is_valid_content(text):

#             if DEBUG:
#                 debug("[Cleaner] Content rejected")

#             return ""

#         return text

#     except Exception as exc:

#         logger.exception(
#             "Content cleaning failed: %s",
#             exc,
#         )

#         return ""

def clean_content(
    text: str,
    source: str = "",
) -> str:
    """
    Main content cleaning pipeline.
    """

    if not text:
        return ""

    try:

        # Initial normalization
        text = normalize_unicode(text)
        text = decode_html_entities(text)
        text = remove_control_characters(text)

        # Pattern cleaning
        text = remove_regex(text)
        text = remove_boilerplate_lines(text, source)

        # Structural cleaning
        text = remove_duplicate_lines(text)
        text = remove_headings(text)
        text = remove_short_lines(text)

        # Text cleanup
        text = remove_urls(text)
        text = remove_empty_brackets(text)
        text = normalize_punctuation(text)
        text = normalize_spaces(text)
        text = final_cleanup(text)

        # Validation
        if not is_valid_content(text):

            if DEBUG:
                debug("[Cleaner] Content rejected")

            return ""

        return text

    except Exception as exc:

        logger.exception(
            "Content cleaning failed: %s",
            exc,
        )

        return ""