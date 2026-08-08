"""
=====================================================
Summarizer Phase 2 Test
Project : News Intelligence Platform
=====================================================
"""

from pprint import pprint

from nlp.summarizer import (
    clear_summary_cache,
    generate_summaries,
    generate_summary,
    health_check,
    module_statistics,
    performance_statistics,
    reset_module,
    runtime_statistics,
    warmup_model,
)

ARTICLE = """
Apple introduced a new AI-powered MacBook during its latest launch event.
The company announced several AI features, improved battery life,
a faster processor, and tighter integration with cloud services.
Executives stated that these features are designed to improve
productivity for professionals and students.
"""

ARTICLE_2 = """
Microsoft announced new enterprise AI capabilities for Azure.
The update includes faster model deployment, better security,
and improved integration with Microsoft 365 services.
"""

ARTICLE_3 = """
Google released a major update to Android.
The new version focuses on privacy, performance,
battery optimization, and AI-powered user experiences.
"""


def separator(title: str):

    print()

    print("=" * 60)

    print(title)

    print("=" * 60)


def main():

    reset_module()

    separator("WARMUP")

    warmup_model()

    separator("SINGLE SUMMARY")

    summary = generate_summary(ARTICLE)

    print(summary)

    separator("CACHE TEST")

    print("First Call")

    generate_summary(ARTICLE)

    print()

    print("Second Call (Should Use Cache)")

    generate_summary(ARTICLE)

    pprint(module_statistics())

    separator("BATCH SUMMARIZATION")

    summaries = generate_summaries(

        [

            ARTICLE,

            ARTICLE_2,

            ARTICLE_3,

        ]

    )

    for index, summary in enumerate(

        summaries,

        start=1,

    ):

        print(f"\nSummary {index}")

        print(summary)

    separator("RUNTIME")

    pprint(

        runtime_statistics()

    )

    separator("PERFORMANCE")

    pprint(

        performance_statistics()

    )

    separator("MODULE")

    pprint(

        module_statistics()

    )

    separator("HEALTH")

    pprint(

        health_check()

    )

    separator("RESET MODULE")

    reset_module()

    pprint(

        module_statistics()

    )

    print()

    print("All tests completed successfully.")


if __name__ == "__main__":

    main()