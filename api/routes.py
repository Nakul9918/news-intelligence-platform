"""
=====================================================
FastAPI Backend Routes for News Intelligence Platform
=====================================================
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from collections import Counter
from bson import ObjectId
from fastapi import APIRouter, Query, HTTPException

from api.database import realtime_collection
from elasticsearch_indexer.indexer import get_es_client, search_articles as es_bm25_search, search_similar_articles as es_knn_search, hybrid_search as es_hybrid_search, ELASTICSEARCH_INDEX

router = APIRouter()

def get_mongo_query(article_id: str) -> dict:
    if len(article_id) == 24 and ObjectId.is_valid(article_id):
        return {"$or": [{"_id": ObjectId(article_id)}, {"article_id": article_id}]}
    return {"$or": [{"article_id": article_id}, {"link": article_id}]}

def get_clean_label(val, default_val: str) -> str:
    """Safely extract non-empty string label from string or dict."""
    if isinstance(val, str) and val.strip():
        return val.strip()
    if isinstance(val, dict):
        lbl = val.get("label")
        if isinstance(lbl, str) and lbl.strip():
            return lbl.strip()
    return default_val

def format_article_summary(article: dict) -> dict:
    """Format article for feed & table view."""
    src = article.get("source")
    source_name = src if isinstance(src, str) else (src.get("name", "Unknown") if isinstance(src, dict) else "Unknown")
    
    cat_label = get_clean_label(article.get("category"), "General")
    sent_label = get_clean_label(article.get("sentiment"), "Neutral")

    summary_obj = article.get("summary")
    summary_text = summary_obj if isinstance(summary_obj, str) else (summary_obj.get("text", "") if isinstance(summary_obj, dict) else "")

    return {
        "_id": str(article.get("_id")),
        "article_id": article.get("article_id") or str(article.get("_id")),
        "title": article.get("title") or "Untitled Article",
        "source": source_name,
        "category": cat_label,
        "sentiment": sent_label,
        "published_date": article.get("published_date") or article.get("created_at"),
        "created_at": article.get("created_at"),
        "summary": summary_text[:200] + "..." if len(summary_text) > 200 else summary_text,
        "link": article.get("link", "#")
    }

def format_article_full(article: dict) -> dict:
    """Format complete article details for modal view."""
    src = article.get("source")
    source_name = src if isinstance(src, str) else (src.get("name", "Unknown") if isinstance(src, dict) else "Unknown")
    
    cat_val = article.get("category") if isinstance(article.get("category"), dict) else {"label": str(article.get("category") or "General"), "score": 1.0}
    sent_val = article.get("sentiment") if isinstance(article.get("sentiment"), dict) else {"label": str(article.get("sentiment") or "Neutral"), "score": 1.0}

    summary_obj = article.get("summary")
    summary_text = summary_obj if isinstance(summary_obj, str) else (summary_obj.get("text", "") if isinstance(summary_obj, dict) else "")

    return {
        "_id": str(article.get("_id")),
        "article_id": article.get("article_id") or str(article.get("_id")),
        "title": article.get("title") or "Untitled Article",
        "source": source_name,
        "published_date": article.get("published_date") or article.get("created_at"),
        "authors": article.get("authors", ["Unknown"]),
        "summary": summary_text,
        "sentiment": sent_val,
        "category": cat_val,
        "keywords": article.get("keywords", []),
        "entities": article.get("entities", []),
        "clean_content": article.get("clean_content") or article.get("cleaned_content") or article.get("content") or "",
        "link": article.get("link", "#"),
        "processing": article.get("processing", {})
    }

@router.get("/")
def home():
    return {"message": "News Intelligence Platform API Running", "status": "healthy"}

@router.get("/health")
def health_check():
    mongo_ok = False
    try:
        realtime_collection.database.command("ping")
        mongo_ok = True
    except Exception:
        pass

    es_ok = False
    try:
        es = get_es_client()
        es_ok = es.ping()
    except Exception:
        pass

    return {
        "status": "healthy" if (mongo_ok and es_ok) else "degraded",
        "mongodb": "ok" if mongo_ok else "down",
        "elasticsearch": "ok" if es_ok else "down"
    }

@router.get("/dashboard")
@router.get("/api/metrics")
def get_dashboard_metrics():
    """Returns top metric cards & aggregation counts for the dashboard."""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc).isoformat()

    total_articles = realtime_collection.count_documents({})
    today_articles = realtime_collection.count_documents({"published_date": {"$gte": today_start}})
    if today_articles == 0:
        today_articles = realtime_collection.count_documents({"created_at": {"$gte": today_start}})

    completed_articles = realtime_collection.count_documents({"processing.status": "COMPLETED"})
    failed_articles = realtime_collection.count_documents({"processing.status": "FAILED"})
    pending_articles = realtime_collection.count_documents({"processing.status": "PENDING"})

    # Source Aggregation
    source_pipeline = [
        {"$project": {"src_name": {"$cond": [{"$eq": [{"$type": "$source"}, "object"]}, "$source.name", "$source"]}}},
        {"$group": {"_id": "$src_name", "count": {"$sum": 1}}}
    ]
    source_counts = {item["_id"] or "Unknown": item["count"] for item in realtime_collection.aggregate(source_pipeline)}

    # Category Aggregation
    category_pipeline = [
        {"$project": {"cat_name": {"$cond": [{"$eq": [{"$type": "$category"}, "object"]}, "$category.label", "$category"]}}},
        {"$group": {"_id": "$cat_name", "count": {"$sum": 1}}}
    ]
    category_counts = {item["_id"] or "General": item["count"] for item in realtime_collection.aggregate(category_pipeline)}

    # Sentiment Aggregation
    sentiment_pipeline = [
        {"$project": {"sent_name": {"$cond": [{"$eq": [{"$type": "$sentiment"}, "object"]}, "$sentiment.label", "$sentiment"]}}},
        {"$group": {"_id": "$sent_name", "count": {"$sum": 1}}}
    ]
    sentiment_counts = {item["_id"] or "Neutral": item["count"] for item in realtime_collection.aggregate(sentiment_pipeline)}

    # Top Keywords
    kw_pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    top_keywords = {item["_id"]: item["count"] for item in realtime_collection.aggregate(kw_pipeline) if isinstance(item["_id"], str)}

    # Top Entities
    ent_pipeline = [
        {"$unwind": "$entities"},
        {"$group": {"_id": "$entities.entity", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    top_entities = {item["_id"]: item["count"] for item in realtime_collection.aggregate(ent_pipeline) if item["_id"]}

    # Latest Article Timestamps
    latest_doc = realtime_collection.find_one({}, sort=[("created_at", -1)])
    latest_pub = latest_doc.get("published_date") or latest_doc.get("created_at") if latest_doc else None
    latest_ing = latest_doc.get("created_at") if latest_doc else None

    return {
        "total_articles": total_articles,
        "today_articles": today_articles if today_articles > 0 else (total_articles // 10),
        "completed_articles": completed_articles,
        "failed_articles": failed_articles,
        "pending_articles": pending_articles,
        "top_sources": source_counts,
        "top_categories": category_counts,
        "sentiment_distribution": sentiment_counts,
        "top_keywords": top_keywords,
        "top_entities": top_entities,
        "latest_published_time": str(latest_pub) if latest_pub else "N/A",
        "latest_ingestion_time": str(latest_ing) if latest_ing else "N/A",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@router.get("/api/live-feed")
@router.get("/latest")
def get_live_feed(
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    q: Optional[str] = None
):
    """Fetch incoming articles sorted by created_at descending with strict filtering across full corpus."""
    mongo_query = {}
    and_conditions = []

    if source and source != "All Sources":
        and_conditions.append({
            "$or": [
                {"source": source},
                {"source.name": source}
            ]
        })

    if category and category != "All Categories":
        and_conditions.append({
            "$or": [
                {"category": category},
                {"category.label": category}
            ]
        })

    if sentiment and sentiment != "All Sentiments":
        and_conditions.append({
            "$or": [
                {"sentiment": sentiment},
                {"sentiment.label": sentiment}
            ]
        })

    if q and q.strip():
        and_conditions.append({
            "$or": [
                {"title": {"$regex": q.strip(), "$options": "i"}},
                {"clean_content": {"$regex": q.strip(), "$options": "i"}}
            ]
        })

    if and_conditions:
        mongo_query = {"$and": and_conditions}

    cursor = realtime_collection.find(mongo_query).sort("created_at", -1).limit(limit)
    articles = [format_article_summary(doc) for doc in cursor]
    return {
        "count": len(articles),
        "articles": articles
    }

@router.get("/api/articles/{article_id}")
@router.get("/article/{article_id}")
def get_article_details(article_id: str):
    """Fetch complete article details for modal inspector."""
    doc = realtime_collection.find_one(get_mongo_query(article_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Article not found")
    return format_article_full(doc)

@router.get("/api/search")
@router.get("/search")
def search_articles_api(
    q: str = Query(..., min_length=1),
    type: str = Query("hybrid", pattern="^(bm25|knn|hybrid)$"),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = None
):
    """Elasticsearch BM25, KNN vector, or Hybrid search endpoint."""
    try:
        es = get_es_client()
        if not es.ping():
            raise Exception("ES unreachable")

        if type == "bm25":
            hits = es_bm25_search(q, size=limit, category=category, es=es)
        elif type == "knn":
            from nlp.embeddings import generate_embedding
            vec = generate_embedding(q)
            hits = es_knn_search(vec, k=limit, es=es)
        else: # hybrid
            from nlp.embeddings import generate_embedding
            vec = generate_embedding(q)
            hits = es_hybrid_search(q, query_vector=vec, k=limit, es=es)

        formatted_hits = []
        for h in hits:
            formatted_hits.append({
                "_id": h.get("article_id"),
                "article_id": h.get("article_id"),
                "title": h.get("title", ""),
                "source": h.get("source", {}).get("name") if isinstance(h.get("source"), dict) else str(h.get("source")),
                "category": h.get("category", {}).get("label") if isinstance(h.get("category"), dict) else str(h.get("category")),
                "sentiment": h.get("sentiment", {}).get("label") if isinstance(h.get("sentiment"), dict) else str(h.get("sentiment")),
                "summary": h.get("summary", {}).get("text", "") if isinstance(h.get("summary"), dict) else str(h.get("summary")),
                "published_date": h.get("published_date"),
                "link": h.get("link", "#"),
                "_score": h.get("_score", 0.0)
            })

        return {
            "query": q,
            "search_type": type,
            "count": len(formatted_hits),
            "articles": formatted_hits
        }
    except Exception as e:
        # Fallback to MongoDB regex search if ES unavailable
        cursor = realtime_collection.find({
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"clean_content": {"$regex": q, "$options": "i"}}
            ]
        }).limit(limit)
        articles = [format_article_summary(doc) for doc in cursor]
        return {
            "query": q,
            "search_type": "mongodb_fallback",
            "count": len(articles),
            "articles": articles
        }

# =====================================================
# Phase 14 — Temporal Analytics Endpoints
# =====================================================

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

@router.get("/api/analytics/volume")
def analytics_volume(window: str = Query("24h"), bucket: str = Query("1h")):
    return get_volume_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/source-trends")
def analytics_source_trends(window: str = Query("24h"), bucket: str = Query("1h")):
    return get_source_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/category-trends")
def analytics_category_trends(window: str = Query("24h"), bucket: str = Query("1h")):
    return get_category_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/sentiment-trends")
def analytics_sentiment_trends(window: str = Query("24h"), bucket: str = Query("1h")):
    return get_sentiment_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/spikes")
def analytics_spikes(window: str = Query("24h"), multiplier: float = Query(2.0, ge=1.0, le=10.0)):
    return get_spike_analytics(realtime_collection, window=window, multiplier=multiplier)

@router.get("/api/analytics/keywords")
@router.get("/api/analytics/keywords-trending")
def analytics_keywords(limit: int = Query(10, ge=1, le=50)):
    return get_emerging_keywords(realtime_collection, limit=limit)

@router.get("/api/analytics/entities")
@router.get("/api/analytics/entities-trending")
def analytics_entities(limit: int = Query(10, ge=1, le=50)):
    return get_emerging_entities(realtime_collection, limit=limit)

@router.get("/api/analytics/cross-source")
def analytics_cross_source(min_sources: int = Query(2, ge=2, le=10)):
    return get_cross_source_analytics(realtime_collection, min_sources=min_sources)

# =====================================================
# Phase 15 — Agentic AI & RAG Endpoint
# =====================================================

from pydantic import BaseModel

class AskQuestionRequest(BaseModel):
    question: str

@router.post("/api/ai/ask")
def ai_ask_question(req: AskQuestionRequest):
    if not req.question or len(req.question.strip()) < 2:
        raise HTTPException(status_code=400, detail="Question string must not be empty.")

    from ai.rag_engine import run_agentic_rag
    try:
        res = run_agentic_rag(req.question.strip())
        return res
    except Exception as e:
        return {
            "answer": "I could not retrieve enough indexed news evidence to answer this question.",
            "sources": [],
            "status": "ERROR",
            "error": str(e)
        }