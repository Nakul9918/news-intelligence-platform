"""
============================================================
Master Automated Test Suite & Regression Runner
News Intelligence Platform
============================================================
"""

import sys
import subprocess
import time

TEST_SUITES = [
    ("1. Config & Package Imports", "python -c \"import config; from qc.quality_gate import evaluate_article_quality; print('Config & Imports OK')\""),
    ("2. Data Quality Gate & Quarantine", "python -c \"from qc.quality_gate import evaluate_article_quality; res = evaluate_article_quality({'article_id':'t1','link':'https://x.com','source':'ET','title':'Sample Valid Title Header'}); assert res['quality_status'] == 'PASSED'; print('DQ Gate OK')\""),
    ("3. News Collectors Test", "python test_collectors.py"),
    ("4. MongoDB Idempotent Upsert & Schema", "python test_consumer_mongo.py"),
    ("5. Extraction & Content Cleaning", "python test_extraction_cleaning.py"),
    ("6. NLP Suite & 384-Dim Embeddings", "python test_nlp_pipeline.py"),
    ("7. Historical Intelligence Engine", "python -c \"from api.intelligence_engine import get_top_news, query_time_machine, compare_source_coverage; print('Top News items:', len(get_top_news('month', limit=5)))\""),
    ("8. FastAPI REST Endpoints", "python test_dashboard_api.py"),
    ("9. Temporal Analytics Engine", "python test_temporal_analytics.py"),
    ("10. Agentic AI & RAG Grounding", "python test_agentic_rag.py"),
    ("11. End-to-End System Pipeline", "python test_end_to_end_flow.py"),
    ("12. Historical Backfill System", "python test_historical_backfill.py"),
    ("13. Dashboard Offline Mode & Imports", "python -c \"import sys; sys.path.insert(0,'d:/project/news-intelligence-platform/project'); import dashboard; print('Dashboard imports OK')\""),
]

def run_suite():
    print("=" * 70)
    print("  NEWS INTELLIGENCE PLATFORM — MASTER TEST SUITE")
    print("=" * 70)

    results = {}
    passed = 0
    failed = 0

    for name, cmd in TEST_SUITES:
        print(f"\n[RUNNING] {name}...")
        t0 = time.time()
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, encoding="utf-8", errors="ignore", timeout=180)
            elapsed = time.time() - t0
            if res.returncode == 0:
                print(f"  [PASS] {name} ({elapsed:.2f}s)")
                results[name] = "PASS"
                passed += 1
            else:
                print(f"  [FAIL] {name} (Exit code: {res.returncode})")
                print("  --- STDOUT ---")
                print(res.stdout[:500] if res.stdout else "None")
                print("  --- STDERR ---")
                print(res.stderr[:500] if res.stderr else "None")
                results[name] = "FAIL"
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {name} Exception: {e}")
            results[name] = "FAIL"
            failed += 1

    print("\n" + "=" * 70)
    print("                  MASTER TEST SUITE RESULTS")
    print("=" * 70)
    print(f"TOTAL SUITES EXECUTED : {len(TEST_SUITES)}")
    print(f"PASSED                : {passed}")
    print(f"FAILED                : {failed}")
    print("-" * 70)

    for name, status in results.items():
        print(f"  - {name}: {status}")

    print("=" * 70)
    return failed == 0

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
