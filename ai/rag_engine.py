"""
Unified Agentic RAG Engine
"""

from typing import Dict, List, Any
from pymongo import MongoClient

from ai.query_router import analyze_query
from ai.context_builder import build_rag_context
from ai.llm_client import generate_grounded_answer
from config import MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME
from elasticsearch_indexer.indexer import get_es_client, search_articles as es_bm25_search, search_similar_articles as es_knn_search, hybrid_search as es_hybrid_search
from nlp.embeddings import generate_embedding

from api.temporal_analytics import (
    get_volume_analytics,
    get_source_analytics,
    get_category_analytics,
    get_sentiment_analytics,
    get_spike_analytics,
    get_emerging_keywords,
    get_emerging_entities,
    get_cross_source_analytics
)

def run_agentic_rag(question: str) -> Dict[str, Any]:
    """
    Executes complete RAG pipeline:
    Query Understanding -> Deterministic Tool Selection -> Retrieval & Analytics ->
    Context Building -> Grounded Answer Generation -> Verified Citations.
    """
    # 1. Query Understanding & Routing
    parsed = analyze_query(question)
    intent = parsed["intent"]
    tools = parsed["tools"]
    filters = parsed["filters"]

    m_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    coll = m_client[DATABASE_NAME][REALTIME_COLLECTION_NAME]

    retrieved_articles = []
    analytics_summaries = []
    retrieval_method = "hybrid"

    # 2. Tool Execution — Temporal & Analytics Tools
    if "get_spike_analytics" in tools:
        spikes = get_spike_analytics(coll, window=filters["time_window"])
        ov = spikes["overall"]
        analytics_summaries.append(f"Spike Analysis: {ov['message']} (Current: {ov['current_volume']} articles, Baseline: {ov['baseline_volume']} articles).")
    
    if "get_emerging_keywords" in tools:
        kw = get_emerging_keywords(coll, limit=5)
        top_kws = [f"{item['keyword']} (+{item['growth_pct']}%)" for item in kw.get("keywords", [])[:5]]
        if top_kws:
            analytics_summaries.append(f"Emerging Keywords: {', '.join(top_kws)}.")

    if "get_emerging_entities" in tools:
        ent = get_emerging_entities(coll, limit=5)
        top_ents = [f"{item['entity']} [{item['type']}] (+{item['growth_pct']}%)" for item in ent.get("entities", [])[:5]]
        if top_ents:
            analytics_summaries.append(f"Emerging Entities: {', '.join(top_ents)}.")

    if "get_cross_source_analytics" in tools:
        cs = get_cross_source_analytics(coll, min_sources=2)
        top_cs = [f"'{item['topic']}' (Covered by {item['sources_count']} sources: {', '.join(item['sources'][:3])})" for item in cs.get("topics", [])[:3]]
        if top_cs:
            analytics_summaries.append(f"Cross-Source Activity: {'; '.join(top_cs)}.")

    if "get_volume_analytics" in tools:
        vol = get_volume_analytics(coll, window=filters["time_window"])
        analytics_summaries.append(f"Total News Volume ({filters['time_window']}): {vol['total_count']} articles.")

    if "get_source_analytics" in tools:
        src_tr = get_source_analytics(coll, window=filters["time_window"])
        if src_tr.get("sources"):
            analytics_summaries.append(f"Active Sources: {', '.join(src_tr['sources'])}.")

    # 3. Tool Execution — Article Retrieval (ES Hybrid / BM25 / KNN with Mongo Fallback)
    try:
        es = get_es_client()
        if es.ping():
            # Generate query vector for hybrid search
            try:
                vec = generate_embedding(question)
                raw_hits = es_hybrid_search(question, query_vector=vec, k=8, category=filters["category"], es=es)
                retrieval_method = "hybrid"
            except Exception:
                raw_hits = es_bm25_search(question, size=8, category=filters["category"], es=es)
                retrieval_method = "bm25"

            for h in raw_hits:
                retrieved_articles.append({
                    "_id": h.get("article_id"),
                    "article_id": h.get("article_id"),
                    "title": h.get("title", ""),
                    "source": h.get("source"),
                    "published_date": h.get("published_date"),
                    "category": h.get("category"),
                    "sentiment": h.get("sentiment"),
                    "summary": h.get("summary", {}).get("text", "") if isinstance(h.get("summary"), dict) else str(h.get("summary")),
                    "clean_content": h.get("clean_content", ""),
                    "link": h.get("link", "#")
                })
        else:
            raise Exception("ES ping failed")
    except Exception:
        # Fallback to MongoDB query if ES is unreachable
        mongo_query = {}
        if filters["category"]:
            mongo_query["category.label"] = filters["category"]
        if filters["sentiment"]:
            mongo_query["sentiment.label"] = filters["sentiment"]
        
        cursor = coll.find(mongo_query).sort("created_at", -1).limit(8)
        retrieved_articles = list(cursor)
        retrieval_method = "mongodb_fallback"

    m_client.close()

    # 4. Context Builder & Grounding
    analytics_str = "\n".join(analytics_summaries) if analytics_summaries else None
    context_str, citations = build_rag_context(retrieved_articles, max_articles=8)

    # 5. Answer Generation
    llm_res = generate_grounded_answer(
        question=question,
        intent=intent,
        context_str=context_str,
        citations=citations,
        analytics_summary=analytics_str
    )

    return {
        "question": question,
        "intent": intent,
        "answer": llm_res["answer"],
        "sources": citations,
        "retrieval": {
            "method": retrieval_method,
            "results_count": len(citations)
        },
        "tools_executed": tools,
        "analytics_summary": analytics_str,
        "status": llm_res["status"],
        "provider": llm_res["provider"]
    }
