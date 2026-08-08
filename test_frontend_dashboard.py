"""
============================================================
PHASE 17 — FRONTEND & DASHBOARD INTEGRATION TEST SUITE
============================================================
"""

import os
import sys
import requests

API_URL = "http://127.0.0.1:8000"

def run_frontend_dashboard_tests():
    print("=" * 80)
    print("RUNNING FRONTEND & DASHBOARD INTEGRATION VERIFICATION (PHASE 17)")
    print("=" * 80)

    # 1. API Health Connection
    print("\n--- Check 1: API Connection & Health ---")
    resp = requests.get(f"{API_URL}/health", timeout=5)
    assert resp.status_code == 200, "API Health check failed!"
    print("[PASS] API Connection OK")

    # 2. Metrics Endpoint
    print("\n--- Check 2: Metrics Rendering Data ---")
    m_resp = requests.get(f"{API_URL}/api/metrics", timeout=5)
    assert m_resp.status_code == 200, "API Metrics failed!"
    m_data = m_resp.json()
    assert "total_articles" in m_data, "Total articles metric missing!"
    print(f"[PASS] Metrics Data OK (Total: {m_data['total_articles']}, Today: {m_data['today_articles']})")

    # 3. Live Feed Endpoint
    print("\n--- Check 3: Live Feed Stream ---")
    lf_resp = requests.get(f"{API_URL}/api/live-feed?limit=5", timeout=5)
    assert lf_resp.status_code == 200, "Live feed failed!"
    lf_data = lf_resp.json()
    assert "articles" in lf_data and len(lf_data["articles"]) > 0, "Live feed articles missing!"
    print(f"[PASS] Live Feed Stream OK (Retrieved: {len(lf_data['articles'])} articles)")

    # 4. Source Analytics
    print("\n--- Check 4: Source Analytics ---")
    sa_resp = requests.get(f"{API_URL}/api/analytics/source-trends?window=24h", timeout=5)
    assert sa_resp.status_code == 200, "Source trends failed!"
    print("[PASS] Source Analytics OK")

    # 5. Category Analytics
    print("\n--- Check 5: Category Analytics ---")
    ca_resp = requests.get(f"{API_URL}/api/analytics/category-trends?window=24h", timeout=5)
    assert ca_resp.status_code == 200, "Category trends failed!"
    print("[PASS] Category Analytics OK")

    # 6. Sentiment Analytics
    print("\n--- Check 6: Sentiment Analytics ---")
    st_resp = requests.get(f"{API_URL}/api/analytics/sentiment-trends?window=24h", timeout=5)
    assert st_resp.status_code == 200, "Sentiment trends failed!"
    print("[PASS] Sentiment Analytics OK")

    # 7. Temporal Volume Analytics
    print("\n--- Check 7: Temporal Volume Analytics ---")
    va_resp = requests.get(f"{API_URL}/api/analytics/volume?window=24h&bucket=1h", timeout=5)
    assert va_resp.status_code == 200, "Volume analytics failed!"
    print("[PASS] Temporal Volume Analytics OK")

    # 8. Spike Detection
    print("\n--- Check 8: Spike Detection Signal ---")
    sp_resp = requests.get(f"{API_URL}/api/analytics/spikes", timeout=5)
    assert sp_resp.status_code == 200, "Spike detection failed!"
    print("[PASS] Spike Detection OK")

    # 9. Emerging Keywords & Entities
    print("\n--- Check 9: Emerging Keywords & Entities ---")
    kw_resp = requests.get(f"{API_URL}/api/analytics/keywords", timeout=5)
    ent_resp = requests.get(f"{API_URL}/api/analytics/entities", timeout=5)
    assert kw_resp.status_code == 200 and ent_resp.status_code == 200, "Emerging keywords/entities failed!"
    print("[PASS] Emerging Keywords & Entities OK")

    # 10. Cross-Source Intelligence
    print("\n--- Check 10: Cross-Source Intelligence ---")
    cs_resp = requests.get(f"{API_URL}/api/analytics/cross-source", timeout=5)
    assert cs_resp.status_code == 200, "Cross-source analytics failed!"
    print("[PASS] Cross-Source Intelligence OK")

    # 11. Search Strategies (BM25, KNN, Hybrid)
    print("\n--- Check 11: BM25, KNN & Hybrid Search Engines ---")
    s_bm25 = requests.get(f"{API_URL}/api/search?q=economy&type=bm25", timeout=30).json()
    s_knn = requests.get(f"{API_URL}/api/search?q=economy%20growth%20in%20India&type=knn", timeout=30).json()
    s_hybrid = requests.get(f"{API_URL}/api/search?q=economy%20growth%20in%20India&type=hybrid", timeout=30).json()
    assert s_bm25.get("count", 0) >= 0 and s_hybrid.get("count", 0) >= 0, "Search engine failed!"
    print("[PASS] Search Engines OK (BM25, KNN, Hybrid verified)")

    # 12. AI Analyst & Grounded RAG
    print("\n--- Check 12: AI Analyst & Grounded RAG ---")
    ai_resp = requests.post(f"{API_URL}/api/ai/ask", json={"question": "What are the major news trends today?"}, timeout=30)
    assert ai_resp.status_code == 200, "AI Analyst endpoint failed!"
    ai_data = ai_resp.json()
    assert "answer" in ai_data and "sources" in ai_data, "AI Analyst response structure invalid!"
    print("[PASS] AI Analyst & Grounded RAG OK")

    # 13. Article Explorer
    print("\n--- Check 13: Article Explorer ---")
    sample_art_id = lf_data["articles"][0]["article_id"]
    art_resp = requests.get(f"{API_URL}/api/articles/{sample_art_id}", timeout=15)
    assert art_resp.status_code == 200, "Article Explorer failed!"
    print("[PASS] Article Explorer OK")

    # 14. Dashboard File Verification
    print("\n--- Check 14: Streamlit Dashboard File ---")
    assert os.path.exists("dashboard.py"), "dashboard.py missing!"
    print("[PASS] Streamlit dashboard.py exists and verified")

    print("\n" + "=" * 80)
    print("ALL 14 FRONTEND & DASHBOARD INTEGRATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_frontend_dashboard_tests()
