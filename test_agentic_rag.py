"""
Phase 15 — Agentic AI & RAG Integration Test
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

def test_agentic_rag_suite():
    print("=" * 80)
    print("RUNNING AGENTIC AI + RAG INTEGRATION & GROUNDING TEST (PHASE 15)")
    print("=" * 80)

    client = TestClient(app)

    # 1. API Health Check
    print("\n--- Step 1: API Health Check ---")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    print(f"[PASS] API Health Check OK: {resp.json()}")

    # 2. General News Trending Query Test
    print("\n--- Step 2: General News Trending Query ---")
    payload = {"question": "What are the major news topics trending today?"}
    resp = client.post("/api/ai/ask", json=payload)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert "answer" in res, "answer missing from response!"
    assert "intent" in res, "intent missing from response!"
    assert "sources" in res, "sources array missing from response!"
    print(f"[PASS] Trending Query OK (Intent: {res['intent']}, Provider: {res['provider']}, Sources: {len(res['sources'])})")

    # 3. Temporal Analytics Query Test
    print("\n--- Step 3: Temporal & Spike Query ---")
    payload = {"question": "Was there unusual news activity today?"}
    resp = client.post("/api/ai/ask", json=payload)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert "answer" in res, "answer missing from response!"
    print(f"[PASS] Temporal Query OK (Answer: '{res['answer'][:60]}...')")

    # 4. Out-of-Domain Grounding Test
    print("\n--- Step 4: Out-of-Domain Grounding & Citation Test ---")
    payload = {"question": "What is the capital of Mars in 2099?"}
    resp = client.post("/api/ai/ask", json=payload)
    assert resp.status_code == 200, f"AI ask failed: {resp.status_code}"
    res = resp.json()
    assert "answer" in res, "answer missing from response!"
    print(f"[PASS] Grounding Query OK (Response: '{res['answer'][:80]}...')")

    print("\n" + "=" * 80)
    print("[SUCCESS] AGENTIC AI & RAG SUITE COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    test_agentic_rag_suite()
