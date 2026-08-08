"""
=====================================================
Historical ETL Pipeline
Version : 2.0
=====================================================
"""

import subprocess
import sys
import time

# =====================================================
# Pipeline Workers
# =====================================================

WORKERS = [

    (
        "Content Extraction",
        "historical_crawlers.historical_content_extractor"
    ),

    (
        "Content Cleaning",
        "historical_crawlers.cleaner_worker"
    ),

    (
        "Keyword Extraction",
        "historical_crawlers.keyword_worker"
    ),

    (
        "Sentiment Analysis",
        "historical_crawlers.sentiment_worker"
    ),

    (
        "Category Classification",
        "historical_crawlers.category_worker"
    )

]

# =====================================================
# Start Pipeline
# =====================================================

print("\n" + "=" * 70)
print("Historical ETL Pipeline Started")
print("=" * 70)

pipeline_start = time.time()

# =====================================================
# Execute Workers
# =====================================================

for step_name, worker in WORKERS:

    print("\n" + "=" * 70)
    print(f"Step   : {step_name}")
    print(f"Worker : {worker}")
    print("=" * 70)

    start_time = time.time()

    result = subprocess.run(
        [sys.executable, "-m", worker]
    )

    end_time = time.time()

    if result.returncode != 0:

        print("\n" + "=" * 70)
        print(f"FAILED : {step_name}")
        print("=" * 70)

        sys.exit(1)

    print(f"\nCompleted : {step_name}")
    print(f"Time Taken : {round(end_time - start_time, 2)} seconds")

# =====================================================
# Finish
# =====================================================

pipeline_end = time.time()

print("\n" + "=" * 70)
print("Historical ETL Pipeline Finished Successfully")
print(f"Total Time : {round(pipeline_end - pipeline_start, 2)} seconds")
print("=" * 70)