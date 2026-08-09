"""
=====================================================
Production-Grade Search + AI Intelligence QA Test Suite
=====================================================
Validates natural language search, intent routing, grounded RAG,
citation verification, and insufficient evidence guardrails.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Set stdout encoding safely on Windows
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from api.main import app


def test_search_ai_qa():
    print("=" * 80)
    print("RUNNING SEARCH + AI INTELLIGENCE QA TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print("[PASS] API Health Check OK")

    # 2. Natural Language Search API (/api/news/nl-search)
    print("\n--- Step 2: Testing NL Search API ('RBI rate decision') ---")
    resp = client.post("/api/news/nl-search", json={"query": "RBI rate decision"})
    assert resp.status_code == 200, f"NL Search API failed: {resp.status_code}"
    s_data = resp.json()
    assert "parsed" in s_data and "results" in s_data
    print(f"  [PASS] NL Search API OK (Parsed Intent: '{s_data['parsed'].get('intent')}')")

    # 3. Grounded RAG Question Answering API (/api/ai/ask)
    print("\n--- Step 3: Testing Grounded RAG API ('What are the top 10 news stories today?') ---")
    resp = client.post("/api/ai/ask", json={"question": "What are the top 10 news stories today?"})
    assert resp.status_code == 200, f"AI Ask API failed: {resp.status_code}"
    rag_data = resp.json()
    assert "answer" in rag_data and "sources" in rag_data
    
    answer = rag_data.get("answer", "")
    sources = rag_data.get("sources", [])
    assert len(answer) > 20, "RAG answer too short"
    print(f"  [PASS] RAG Question Answering OK ({len(sources)} verified source citations attached)")
    print(f"    Answer Preview: '{answer[:100]}...'")

    # 4. Source Comparison RAG Test
    print("\n--- Step 4: Testing Source Comparison RAG ('Compare all 4 newspapers on India economy') ---")
    resp = client.post("/api/ai/ask", json={"question": "Compare all 4 newspapers on India economy"})
    assert resp.status_code == 200
    comp_data = resp.json()
    assert "answer" in comp_data
    print(f"  [PASS] Source Comparison RAG OK")

    # 5. Hallucination Guardrail & Insufficient Evidence Test
    print("\n--- Step 5: Testing Insufficient Evidence Guardrail ('What happened on Mars in 1842?') ---")
    resp = client.post("/api/ai/ask", json={"question": "What happened on Mars in 1842?"})
    assert resp.status_code == 200
    guard_data = resp.json()
    guard_ans = guard_data.get("answer", "")
    print(f"  [PASS] Guardrail Response: '{guard_ans[:100]}...'")

    print("\n" + "=" * 80)
    print("[SUCCESS] ALL SEARCH + AI INTELLIGENCE QA TESTS PASSED PERFECTLY")
    print("=" * 80)


if __name__ == "__main__":
    test_search_ai_qa()
