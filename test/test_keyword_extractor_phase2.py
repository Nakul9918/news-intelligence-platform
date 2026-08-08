"""
=====================================================
Keyword Extractor Phase 2 Test

Project : News Intelligence Platform
=====================================================
"""

from pprint import pprint

from nlp.keyword_extractor import (
    warmup_model,
    extract_keywords,
    extract_keywords_batch,
    runtime_statistics,
    performance_statistics,
    module_statistics,
    health_check,
    reset_module,
)

ARTICLE_1 = """
Apple introduced a new AI-powered MacBook Pro during WWDC 2026.
The company announced faster processors, improved battery life,
AI-powered developer tools, and tighter iCloud integration.
"""

ARTICLE_2 = """
Microsoft announced new enterprise AI capabilities for Azure.
The update includes better security, cloud scalability,
and improved Microsoft 365 integration.
"""

ARTICLE_3 = """
Google released Android 17 with AI-powered features,
privacy improvements, and enhanced battery optimization.
"""


def separator(title: str):

    print()

    print("=" * 60)

    print(title)

    print("=" * 60)


def main():

    # -------------------------------------------------
    # Reset
    # -------------------------------------------------

    reset_module()

    # -------------------------------------------------
    # Warmup
    # -------------------------------------------------

    separator("WARMUP")

    warmup_model()

    # -------------------------------------------------
    # Single Extraction
    # -------------------------------------------------

    separator("SINGLE EXTRACTION")

    keywords = extract_keywords(
        ARTICLE_1
    )

    pprint(keywords)

    # -------------------------------------------------
    # Cache Test
    # -------------------------------------------------

    separator("CACHE TEST")

    print("First Call")

    extract_keywords(
        ARTICLE_1
    )

    print()

    print("Second Call (Should Use Cache)")

    extract_keywords(
        ARTICLE_1
    )

    pprint(
        module_statistics()
    )

    # -------------------------------------------------
    # Batch Extraction
    # -------------------------------------------------

    separator("BATCH EXTRACTION")

    results = extract_keywords_batch(

        [

            ARTICLE_1,

            ARTICLE_2,

            ARTICLE_3,

        ]

    )

    for index, keywords in enumerate(

        results,

        start=1,

    ):

        print()

        print(f"Article {index}")

        pprint(keywords)

    # -------------------------------------------------
    # Runtime
    # -------------------------------------------------

    separator("RUNTIME")

    pprint(
        runtime_statistics()
    )

    # -------------------------------------------------
    # Performance
    # -------------------------------------------------

    separator("PERFORMANCE")

    pprint(
        performance_statistics()
    )

    # -------------------------------------------------
    # Module
    # -------------------------------------------------

    separator("MODULE")

    pprint(
        module_statistics()
    )

    # -------------------------------------------------
    # Health
    # -------------------------------------------------

    separator("HEALTH")

    pprint(
        health_check()
    )

    # -------------------------------------------------
    # Reset
    # -------------------------------------------------

    separator("RESET")

    reset_module()

    pprint(
        module_statistics()
    )

    print()

    print("All tests completed successfully.")


if __name__ == "__main__":

    main()