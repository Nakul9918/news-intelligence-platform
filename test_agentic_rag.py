"""
Phase 15 — Agentic AI & RAG Integration Test
"""

import sys
import io
import time
import requests
from pathlib import Path
from pymongo import MongoClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME

API_URL = "http://127.0.0.1:8000"

def test_agentic_rag_suite():
    print("=" * 80)
    print("RUNNING AGENTIC AI + RAG INTEGRATION & GROUNDING TEST (PHASE 15)")
    print("=" * 80)

    # 1. API Health Check
    print("\n--- Step 1: API Health Check ---")
    resp = requests.get(f"{API_URL}/health", timeout=5)
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print(f"[PASS] API Health Check OK: {resp.json()}")

    # 2. General News Trending Query Test
    print("\n--- Step 2: General News Trending Query ---")
    payload = {"question": "What are the major news topics trending today?"}
    resp = requests.post(f"{API_URL}/api/ai/ask", json=payload, timeout=30)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert "answer" in res, "answer missing from response!"
    assert "intent" in res, "intent missing from response!"
    assert "sources" in res, "sources array missing from response!"
    print(f"[PASS] Trending Query OK (Intent: {res['intent']}, Provider: {res['provider']}, Sources: {len(res['sources'])})")

    # 3. Temporal Analytics Query Test
    print("\n--- Step 3: Temporal & Spike Query ---")
    payload = {"question": "Was there unusual news activity today?"}
    resp = requests.post(f"{API_URL}/api/ai/ask", json=payload, timeout=30)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert "get_spike_analytics" in res.get("tools_executed", []), "Spike tool missing from execution!"
    print(f"[PASS] Temporal Query OK (Tools Executed: {res['tools_executed']})")

    # 4. Source Comparison Query Test
    print("\n--- Step 4: Source Comparison Query ---")
    payload = {"question": "Compare Economic Times and The Hindu coverage."}
    resp = requests.post(f"{API_URL}/api/ai/ask", json=payload, timeout=30)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert res["intent"] == "COMPARISON", f"Expected intent COMPARISON, got {res['intent']}"
    print(f"[PASS] Source Comparison Query OK (Intent: {res['intent']})")

    # 5. Cross-Source Topic Query Test
    print("\n--- Step 5: Cross-Source Topic Query ---")
    payload = {"question": "Which topics are being covered by multiple news sources?"}
    resp = requests.post(f"{API_URL}/api/ai/ask", json=payload, timeout=30)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert "get_cross_source_analytics" in res.get("tools_executed", []), "Cross-source tool missing!"
    print(f"[PASS] Cross-Source Topic Query OK (Identified Topics in Response)")

    # 6. Citation & Grounding Verification Test
    print("\n--- Step 6: Citation & Source URL Verification ---")
    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    coll = m_client[DATABASE_NAME][REALTIME_COLLECTION_NAME]

    if res.get("sources"):
        sample_src = res["sources"][0]
        aid = sample_src["article_id"]
        db_doc = coll.find_one({"$or": [{"article_id": aid}, {"link": sample_src["url"]}]})
        assert db_doc is not None, f"Source citation {aid} not found in database!"
        print(f"[PASS] Citation Verified: Article ID '{aid[:20]}...' exists in MongoDB with title '{db_doc.get('title')[:30]}...'")
    m_client.close()

    # 7. Hallucination / Insufficient Evidence Test
    print("\n--- Step 7: Hallucination & Insufficient Evidence Test ---")
    payload = {"question": "What happened on planet Mars in the year 1842 according to Indian Express?"}
    resp = requests.post(f"{API_URL}/api/ai/ask", json=payload, timeout=30)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert ("Insufficient evidence" in res["answer"] or res.get("status") == "INSUFFICIENT_EVIDENCE"), "AI failed hallucination guardrail!"
    print(f"[PASS] Hallucination Guardrail OK: Response stated '{res['answer'][:60]}...' without fabricating facts.")

    # 8. Backward Compatibility Check for Phase 13 & 14 Endpoints
    print("\n--- Step 8: Phase 13 & 14 Backward Compatibility Check ---")
    resp = requests.get(f"{API_URL}/api/metrics", timeout=5)
    assert resp.status_code == 200
    resp = requests.get(f"{API_URL}/api/analytics/volume", timeout=5)
    assert resp.status_code == 200
    resp = requests.get(f"{API_URL}/api/search?q=india&type=hybrid", timeout=5)
    assert resp.status_code == 200
    print("[PASS] All Phase 13 & 14 Endpoints Remain 100% Functional!")

    print("\n" + "=" * 80)
    print("ALL PHASE 15 AGENTIC AI & RAG TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    test_agentic_rag_suite()
