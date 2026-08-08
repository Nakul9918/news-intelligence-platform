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

# def remove_regex(text: str) -> str:

#     for pattern in REGEX_PATTERNS:

#         text = re.sub(
#             pattern,
#             "",
#             text,
#             flags=re.IGNORECASE | re.MULTILINE,
#         )

#     return text

def remove_regex(text: str) -> str:

    print("\nREGEX DEBUG")
    print("=" * 70)

    for pattern in REGEX_PATTERNS:

        before = len(text)

        new_text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        after = len(new_text)

        if before != after:
            print(f"\nPattern : {pattern}")
            print(f"Length  : {before} -> {after}")

        text = new_text

    return text

# =====================================================
# Remove Boilerplate Lines
# =====================================================

def remove_boilerplate_lines(text: str, source: str = "") -> str:

    phrases = list(GLOBAL_REMOVE_PHRASES)
    phrases.extend(SOURCE_REMOVE_PHRASES.get(source, []))

    cleaned_lines = []

    print("\nBOILERPLATE DEBUG")
    print("=" * 70)

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        matched = False

        for phrase in phrases:

            if phrase.lower() in line.lower():

                print(f"\nREMOVED LINE:\n{line[:150]}")
                print(f"MATCHED PHRASE: {phrase}")

                matched = True
                break

        if matched:
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
    Debug Version
    Prints content length after every cleaning step.
    """

    if not text:
        print("❌ Input text is empty")
        return ""

    print("\n" + "=" * 70)
    print("CONTENT CLEANER DEBUG")
    print("=" * 70)

    print(f"Original Length : {len(text)}")

    # Step 1
    text = normalize_unicode(text)
    print(f"After normalize_unicode      : {len(text)}")

    # 👇 Print BEFORE regex cleaning
    print("\nFIRST 500 CHARACTERS BEFORE REGEX")
    print("=" * 70)
    print(text[:500])
    print("=" * 70)
    print(f"Number of newline characters : {text.count(chr(10))}")

    # Step 2
    text = remove_regex(text)
    print(f"After remove_regex           : {len(text)}")

    # Step 3
    text = remove_boilerplate_lines(text, source)
    print(f"After boilerplate removal    : {len(text)}")

    # Step 4
    text = remove_duplicate_lines(text)
    print(f"After duplicate removal      : {len(text)}")

    # Step 5
    text = remove_short_lines(text)
    print(f"After short line removal     : {len(text)}")

    # Step 6
    text = remove_headings(text)
    print(f"After heading removal        : {len(text)}")

    # Step 7
    text = remove_urls(text)
    print(f"After URL removal            : {len(text)}")

    # Step 8
    text = remove_empty_brackets(text)
    print(f"After empty bracket removal  : {len(text)}")

    # Step 9
    text = normalize_punctuation(text)
    print(f"After punctuation normalize  : {len(text)}")

    # Step 10
    text = normalize_spaces(text)
    print(f"After whitespace normalize   : {len(text)}")

    print("\nPreview:")
    print("-" * 70)
    print(repr(text[:500]))
    print("-" * 70)

    return text