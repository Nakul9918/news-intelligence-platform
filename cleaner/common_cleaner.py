"""
=========================================================
Common Cleaner

Reusable text cleaning utilities.

Responsibilities
----------------
Remove HTML
Remove Boilerplate
Remove URLs
Remove Duplicate Lines
Normalize Text
Return Clean Content
=========================================================
"""

# =====================================================
# Standard Library
# =====================================================

import re

# =====================================================
# Reuse Generic Utilities
# =====================================================

from extractor.common_extractor import (
    remove_html_tags,
    remove_extra_spaces,
    normalize_text,
)

# =====================================================
# Boilerplate Patterns
# =====================================================

# =====================================================
# Boilerplate Text
# =====================================================

BOILERPLATE_TEXT = [

    "Listen to this article",

    "Listen to this article in summarized format",

    "Unlock AI Briefing",

    "Catch all the",

    "Read More",

    "Subscribe",

    "Follow us on",

    "Advertisement",

    "Ads by",

    "...more",

]

# =====================================================
# Remove Boilerplate
# =====================================================

def remove_boilerplate(
    text
):
    """
    Remove common boilerplate text.
    """

    if not text:
        return ""

    for phrase in BOILERPLATE_TEXT:

        text = text.replace(
            phrase,
            ""
        )

    return text

# =====================================================
# Remove URLs
# =====================================================

def remove_urls(
    text
):
    """
    Remove URLs.
    """

    if not text:
        return ""

    return re.sub(

        r"http[s]?://\S+",

        "",

        text

    )


# =====================================================
# Remove Duplicate Lines
# =====================================================

def remove_duplicate_lines(
    text
):
    """
    Remove duplicate lines.
    """

    if not text:
        return ""

    cleaned = []

    seen = set()

    for line in text.splitlines():

        line = line.strip()

        if not line:

            continue

        if line in seen:

            continue

        seen.add(line)

        cleaned.append(line)

    return "\n".join(
        cleaned
    )


# =====================================================
# Remove Empty Lines
# =====================================================

def remove_empty_lines(
    text
):
    """
    Remove repeated blank lines.
    """

    if not text:
        return ""

    return re.sub(

        r"\n\s*\n+",

        "\n",

        text

    )


# =====================================================
# Final Cleaning Pipeline
# =====================================================

def clean_text(
    text
):
    """
    Complete article cleaning pipeline.
    """

    if not text:

        return ""

    # =====================================
    # HTML
    # =====================================

    text = remove_html_tags(
        text
    )

    # =====================================
    # Normalize
    # =====================================

    text = normalize_text(
        text
    )

    # =====================================
    # Remove Boilerplate
    # =====================================

    text = remove_boilerplate(
        text
    )

    # =====================================
    # Remove URLs
    # =====================================

    text = remove_urls(
        text
    )

    # =====================================
    # Remove Duplicate Lines
    # =====================================

    text = remove_duplicate_lines(
        text
    )

    # =====================================
    # Remove Empty Lines
    # =====================================

    text = remove_empty_lines(
        text
    )

    # =====================================
    # Normalize Spaces
    # =====================================

    text = remove_extra_spaces(
        text
    )

    return text.strip()