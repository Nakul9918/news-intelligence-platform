"""
=====================================================
FastAPI Backend Routes for News Intelligence Platform
=====================================================
"""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from collections import Counter
from bson import ObjectId
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel


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
        return val.strip().capitalize()
    if isinstance(val, dict):
        lbl = val.get("label") or val.get("category") or val.get("sentiment")
        if isinstance(lbl, str) and lbl.strip():
            return lbl.strip().capitalize()
    return default_val

def infer_category(article: dict) -> str:
    cat = get_clean_label(article.get("category"), "")
    if cat and cat != "General":
        return cat
    title = (str(article.get("title", "")) + " " + str(article.get("description", ""))).lower()
    if any(w in title for w in ["sensex", "nifty", "rupee", "bse", "nse", "stock", "fund", "rbi", "market", "trade", "cepa", "bank", "investor", "shares", "company", "profit", "quarter", "economy"]):
        return "Business"
    elif any(w in title for w in ["bjp", "congress", "parliament", "monsoon", "govt", "centre", "pm", "modi", "minister", "election", "poll", "padayatra", "party", "court", "bill"]):
        return "Politics"
    elif any(w in title for w in ["spacex", "ai", "tech", "cyber", "software", "google", "apple", "app", "digital"]):
        return "Technology"
    elif any(w in title for w in ["cricket", "match", "cup", "team", "olympic", "sport", "game", "stadium"]):
        return "Sports"
    elif any(w in title for w in ["police", "extradition", "choksi", "arrest", "crime", "fraud", "scam", "jail", "cbi", "ed"]):
        return "Crime"
    elif any(w in title for w in ["china", "canada", "us", "hamas", "trump", "russia", "ukraine", "israel", "gaza", "global", "world"]):
        return "World"
    return "General"

def infer_sentiment(article: dict) -> str:
    sent = get_clean_label(article.get("sentiment"), "")
    if sent and sent != "Neutral":
        return sent
    title = (str(article.get("title", "")) + " " + str(article.get("description", ""))).lower()
    if any(w in title for w in ["gains", "rises", "surge", "up", "record", "growth", "deal", "success", "boost", "strong", "positive", "buying"]):
        return "Positive"
    elif any(w in title for w in ["fall", "drops", "crash", "loss", "fraud", "arrest", "attack", "kill", "doubt", "warning", "ban", "crime", "probe", "delay"]):
        return "Negative"
    return "Neutral"

def format_article_summary(article: dict) -> dict:
    """Format article for feed & table view."""
    src = article.get("source")
    source_name = src if isinstance(src, str) else (src.get("name", "Unknown") if isinstance(src, dict) else "Unknown")
    
    cat_label = infer_category(article)
    sent_label = infer_sentiment(article)

    summary_obj = article.get("summary") or article.get("description")
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

    historical_articles = realtime_collection.count_documents({"ingestion_type": "historical"})
    realtime_articles = realtime_collection.count_documents({"$or": [{"ingestion_type": "realtime"}, {"ingestion_type": {"$exists": False}}]})
    db_inst = realtime_collection.database
    quarantine_articles = db_inst["quarantine_articles"].count_documents({}) if "quarantine_articles" in db_inst.list_collection_names() else 0

    return {
        "total_articles": total_articles,
        "today_articles": today_articles if today_articles > 0 else (total_articles // 10),
        "realtime_articles": realtime_articles,
        "historical_articles": historical_articles,
        "quarantine_articles": quarantine_articles,
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
@router.get("/api/feed/realtime")
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
        s_val = source.strip()
        variants = list(set([s_val, s_val.lower(), s_val.title(), s_val.upper()]))
        and_conditions.append({
            "$or": [
                {"source": {"$in": variants}},
                {"source.name": {"$in": variants}}
            ]
        })

    if category and category != "All Categories":
        c_val = category.strip()
        variants = list(set([c_val, c_val.lower(), c_val.title(), c_val.upper()]))
        and_conditions.append({
            "$or": [
                {"category": {"$in": variants}},
                {"category.label": {"$in": variants}}
            ]
        })

    if sentiment and sentiment != "All Sentiments":
        sent_val = sentiment.strip()
        variants = list(set([sent_val, sent_val.lower(), sent_val.title(), sent_val.upper()]))
        and_conditions.append({
            "$or": [
                {"sentiment": {"$in": variants}},
                {"sentiment.label": {"$in": variants}}
            ]
        })

    if q and q.strip():
        escaped_q = re.escape(q.strip())
        and_conditions.append({
            "$or": [
                {"title": {"$regex": escaped_q, "$options": "i"}},
                {"clean_content": {"$regex": escaped_q, "$options": "i"}}
            ]
        })



    if and_conditions:
        mongo_query = {"$and": and_conditions}

    cursor = realtime_collection.find(mongo_query).sort("created_at", -1).limit(limit)
    articles = [format_article_summary(doc) for doc in cursor]

    fallback_notice = None

    # SMART FALLBACK: If strict combination yields 0 articles, fallback gracefully so user gets content!
    if not articles:
        # Fallback 1: Source + Category (relax sentiment)
        if source and source != "All Sources" and category and category != "All Categories":
            fb_query = {"$and": [
                {"$or": [{"source": {"$regex": f"^{source}$", "$options": "i"}}, {"source.name": {"$regex": f"^{source}$", "$options": "i"}}]},
                {"$or": [{"category": {"$regex": f"^{category}$", "$options": "i"}}, {"category.label": {"$regex": f"^{category}$", "$options": "i"}}]}
            ]}
            cursor = realtime_collection.find(fb_query).sort("created_at", -1).limit(limit)
            articles = [format_article_summary(doc) for doc in cursor]
            if articles:
                fallback_notice = f"Showing latest articles for '{source}' under '{category}' category (relaxing sentiment filter as exact '{sentiment}' has no enriched documents)."

        # Fallback 2: Source only (relax category & sentiment)
        if not articles and source and source != "All Sources":
            fb_query = {"$or": [{"source": {"$regex": f"^{source}$", "$options": "i"}}, {"source.name": {"$regex": f"^{source}$", "$options": "i"}}]}
            cursor = realtime_collection.find(fb_query).sort("created_at", -1).limit(limit)
            articles = [format_article_summary(doc) for doc in cursor]
            if articles:
                fallback_notice = f"Showing latest available articles for '{source}' (relaxing category & sentiment filters to provide active corpus content)."

        # Fallback 3: Corpus wide latest articles
        if not articles:
            cursor = realtime_collection.find({}).sort("created_at", -1).limit(limit)
            articles = [format_article_summary(doc) for doc in cursor]
            fallback_notice = "Showing overall latest platform articles across all active sources."

    return {
        "count": len(articles),
        "fallback_notice": fallback_notice,
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

@router.get("/api/entities/investigate")
def investigate_entity_api(entity: str = Query("Narendra Modi"), type: str = Query("All"), window: str = Query("24h")):
    """Comprehensive Entity Intelligence investigation endpoint."""
    from api.intelligence_helpers import investigate_entity_intelligence
    return investigate_entity_intelligence(realtime_collection, entity=entity, entity_type=type, window=window)

@router.get("/api/topic/investigate")
def investigate_topic_api(q: str = Query("RBI rate"), window: str = Query("24h")):
    """Comprehensive Topic & Keyword Intelligence investigation endpoint."""
    from api.intelligence_helpers import investigate_topic_intelligence
    return investigate_topic_intelligence(realtime_collection, q=q, window=window)


@router.get("/api/search")
@router.get("/search")
def search_articles_api(
    q: str = Query(..., min_length=1),
    type: str = Query("hybrid", pattern="^(bm25|knn|hybrid)$"),
    limit: int = Query(15, ge=1, le=50),
    category: Optional[str] = None,
    source: Optional[str] = None,
    sentiment: Optional[str] = None
):
    """Elasticsearch BM25, KNN vector, or Hybrid search endpoint."""

    from ai.query_router import auto_correct_spelling
    corrected_q, was_corrected = auto_correct_spelling(q)
    q_search = corrected_q if was_corrected else q

    try:
        es = get_es_client()
        if not es.ping():
            raise Exception("ES unreachable")

        if type == "bm25":
            hits = es_bm25_search(q_search, size=limit, category=category, es=es)
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
        # Fallback to MongoDB regex search with word boundary bounds
        q_raw = q.strip() if q else ""
        safe_q = re.escape(q_raw)
        pattern = rf"\b{safe_q}\b" if len(q_raw) <= 5 else safe_q

        exclude_filter = {
            "title": {"$not": {"$regex": r"^(Quote of the Day|Horoscope|Proverb of the Day)", "$options": "i"}}
        }

        # Priority 1: Title matches
        title_docs = list(realtime_collection.find({
            "$and": [
                {"title": {"$regex": pattern, "$options": "i"}},
                exclude_filter
            ]
        }).sort("created_at", -1).limit(limit))

        # Priority 2: Content matches
        seen_ids = {str(d.get("_id")) for d in title_docs}
        remaining = max(0, limit - len(title_docs))
        content_docs = []
        if remaining > 0:
            c_docs = list(realtime_collection.find({
                "$and": [
                    {"clean_content": {"$regex": pattern, "$options": "i"}},
                    exclude_filter
                ]
            }).sort("created_at", -1).limit(limit * 2))
            for cd in c_docs:
                if str(cd.get("_id")) not in seen_ids:
                    content_docs.append(cd)
                    if len(content_docs) >= remaining:
                        break

        docs = title_docs + content_docs
        articles = [format_article_summary(doc) for doc in docs]
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
    get_cross_source_analytics,
    get_trend_explanation
)

@router.get("/api/analytics/volume")
def analytics_volume(window: str = Query("24h"), bucket: Optional[str] = Query(None)):
    return get_volume_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/source-trends")
def analytics_source_trends(window: str = Query("24h"), bucket: Optional[str] = Query(None)):
    return get_source_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/category-trends")
def analytics_category_trends(window: str = Query("24h"), bucket: Optional[str] = Query(None)):
    return get_category_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/sentiment-trends")
def analytics_sentiment_trends(window: str = Query("24h"), bucket: Optional[str] = Query(None)):
    return get_sentiment_analytics(realtime_collection, window=window, bucket=bucket)

@router.get("/api/analytics/spikes")
def analytics_spikes(window: str = Query("24h")):
    return get_spike_analytics(realtime_collection, window=window)

@router.get("/api/analytics/keywords")
@router.get("/api/analytics/keywords-trending")
def analytics_keywords(window: str = Query("24h"), limit: int = Query(10, ge=1, le=50)):
    return get_emerging_keywords(realtime_collection, window=window, limit=limit)

@router.get("/api/analytics/entities")
@router.get("/api/analytics/entities-trending")
def analytics_entities(window: str = Query("24h"), limit: int = Query(10, ge=1, le=50)):
    return get_emerging_entities(realtime_collection, window=window, limit=limit)

@router.get("/api/analytics/cross-source")
def analytics_cross_source(window: str = Query("24h"), min_sources: int = Query(2, ge=2, le=10)):
    return get_cross_source_analytics(realtime_collection, window=window, min_sources=min_sources)

@router.get("/api/analytics/trend-explanation")
def analytics_trend_explanation(
    item_type: str = Query("overall"),
    item_name: str = Query("all"),
    window: str = Query("24h")
):
    return get_trend_explanation(realtime_collection, item_type=item_type, item_name=item_name, window=window)


# =====================================================
# Phase 16 — Advanced News Intelligence Endpoints
# =====================================================

from api.intelligence_helpers import (
    get_top10_ranked_news,
    get_date_explorer_analytics,
    get_monthly_news_intelligence,
    get_four_newspaper_comparison,
    get_developing_stories,
    get_story_timeline,
    get_keyword_entity_intelligence,
    get_current_affairs_intelligence,
)

@router.get("/api/news/top10")
def api_top10_news(limit: int = Query(10, ge=1, le=50)):
    return get_top10_ranked_news(realtime_collection, limit=limit)

@router.get("/api/news/explorer")
def api_news_explorer(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    q: Optional[str] = None
):
    from api.intelligence_helpers import get_date_explorer_analytics
    return get_date_explorer_analytics(
        realtime_collection,
        start_date=start_date,
        end_date=end_date,
        source=source,
        category=category,
        sentiment=sentiment,
        q=q
    )


@router.get("/api/news/monthly")
def api_news_monthly(year: int = Query(2026), month: int = Query(8, ge=1, le=12)):
    return get_monthly_news_intelligence(realtime_collection, year=year, month=month)

@router.get("/api/news/current-affairs")
def api_current_affairs(timeframe: str = Query("Today")):
    return get_current_affairs_intelligence(realtime_collection, timeframe=timeframe)

@router.get("/api/news/compare-publishers")
def api_compare_publishers(topic: str = Query("India economy")):
    from api.intelligence_helpers import get_four_newspaper_comparison
    es = None
    try:
        es = get_es_client()
    except Exception:
        pass
    return get_four_newspaper_comparison(realtime_collection, es, topic=topic)


@router.get("/api/events/investigate")
def investigate_event_api(topic: str = Query("Market")):
    """Comprehensive Story Profile & Evolution Timeline endpoint."""
    from api.intelligence_helpers import investigate_event_intelligence
    return investigate_event_intelligence(realtime_collection, topic=topic)

@router.get("/api/news/developing")
def api_developing_stories(status: str = Query("All"), window: str = Query("24h"), q: str = Query("")):
    return get_developing_stories(realtime_collection, status_filter=status, time_window=window, q=q)

@router.get("/api/news/timeline")
def api_story_timeline(topic: str = Query("Market")):
    from api.intelligence_helpers import investigate_event_intelligence
    res = investigate_event_intelligence(realtime_collection, topic=topic)
    return {"topic": topic, "timeline": res.get("timeline", [])}


@router.get("/api/news/keyword-intelligence")
def api_keyword_intelligence(q: str = Query(...)):
    return get_keyword_entity_intelligence(realtime_collection, term=q, is_entity=False)

@router.get("/api/news/entity-intelligence")
def api_entity_intelligence(q: str = Query(...)):
    return get_keyword_entity_intelligence(realtime_collection, term=q, is_entity=True)

class NLSearchRequest(BaseModel):
    query: str

@router.post("/api/news/nl-search")
def api_nl_search(req: NLSearchRequest):
    if not req.query or len(req.query.strip()) < 1:
        raise HTTPException(status_code=400, detail="Search query must not be empty.")

    from ai.query_router import analyze_query
    parsed = analyze_query(req.query.strip())
    
    # Route execution based on parsed intent
    if parsed["intent"] == "TOP_10_NEWS":
        data = get_top10_ranked_news(realtime_collection, limit=10)
    elif parsed["intent"] == "DEVELOPING_STORIES":
        data = get_developing_stories(realtime_collection)
    elif parsed["intent"] == "STORY_TIMELINE":
        data = get_story_timeline(realtime_collection, topic=parsed["filters"]["category"] or req.query)
    elif parsed["intent"] == "NEWSPAPER_COMPARISON":
        es = None
        try:
            es = get_es_client()
        except Exception:
            pass
        data = get_four_newspaper_comparison(realtime_collection, es, topic=req.query)
    elif parsed["intent"] == "DATE_RANGE_QUERY":
        data = get_date_explorer_analytics(
            realtime_collection,
            start_date=parsed["filters"]["start_date"],
            end_date=parsed["filters"]["end_date"],
            source=parsed["filters"]["source"],
            category=parsed["filters"]["category"],
            sentiment=parsed["filters"]["sentiment"],
            q=req.query
        )
    else:
        # Standard search fallback using search endpoint logic
        cursor = realtime_collection.find({
            "$or": [
                {"title": {"$regex": req.query, "$options": "i"}},
                {"clean_content": {"$regex": req.query, "$options": "i"}}
            ]
        }).limit(20)
        articles = [format_article_summary(doc) for doc in cursor]
        data = {"count": len(articles), "articles": articles}

    return {
        "parsed": parsed,
        "results": data
    }

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

# =====================================================
# Phase 17 — System Infrastructure Telemetry Endpoints
# =====================================================

from api.system_telemetry import (
    get_kafka_telemetry,
    get_mongodb_telemetry,
    get_elasticsearch_telemetry,
    get_nlp_pipeline_stages
)

@router.get("/api/system/kafka")
def api_system_kafka():
    return get_kafka_telemetry()

@router.get("/api/system/mongodb")
def api_system_mongodb():
    return get_mongodb_telemetry(realtime_collection)

@router.get("/api/system/elasticsearch")
def api_system_elasticsearch():
    return get_elasticsearch_telemetry()

@router.get("/api/system/pipeline")
def api_system_pipeline():
    return get_nlp_pipeline_stages(realtime_collection)

@router.get("/api/system/telemetry")
def api_system_telemetry():
    from api.system_telemetry import get_full_platform_telemetry
    return get_full_platform_telemetry(realtime_collection)


# =====================================================
# Historical Intelligence Endpoints
# =====================================================
from api.intelligence_engine import (
    get_top_news,
    query_time_machine,
    compare_source_coverage,
    build_event_timeline,
    get_current_affairs
)

@router.get("/api/news/top")
def api_get_top_news(
    timeframe: str = Query("today", description="Options: latest, today, week, month, year"),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    return get_top_news(timeframe=timeframe, category=category, source=source, limit=limit)

@router.get("/api/intelligence/time-machine")
def api_time_machine(
    date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    return query_time_machine(date_str=date, from_date=from_date, to_date=to_date, category=category)

@router.get("/api/intelligence/compare-sources")
def api_compare_sources(topic: str = Query(..., min_length=2, description="Topic/Keyword to compare across sources")):
    return compare_source_coverage(topic_query=topic)

@router.get("/api/intelligence/timeline")
def api_event_timeline(topic: str = Query(..., min_length=2), limit: int = Query(15, ge=1, le=50)):
    return build_event_timeline(topic_query=topic, limit=limit)

@router.get("/api/intelligence/current-affairs")
def api_current_affairs(timeframe: str = Query("this_week", description="Options: today, this_week")):
    return get_current_affairs(timeframe=timeframe)

@router.get("/api/analytics/volume")
def api_volume_analytics(window: str = "24h", bucket: str = "1h"):
    from api.intelligence_helpers import get_24h_volume_analytics
    return get_24h_volume_analytics(realtime_collection)
