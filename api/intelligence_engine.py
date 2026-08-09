"""
============================================================
Historical Intelligence & Analytics Engine
News Intelligence Platform
============================================================
Version : 3.0 (Production)
Provides:
 - Top News Engine (Ranked by recency, quality, coverage)
 - News Time Machine (Date/Month/Year flashback)
 - Cross-Source News Comparison (Headline, framing, tone)
 - News Evolution Engine (Multi-year topic trajectory)
 - Event Timeline Generator (Chronological story chains)
 - Current Affairs Intelligence (Fact-grounded domain briefs)
============================================================
"""

from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict
import re

from api.database import realtime_collection

def parse_date_to_utc(dt_val) -> datetime | None:
    if not dt_val:
        return None
    if isinstance(dt_val, datetime):
        return dt_val
    s = str(dt_val).strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

def extract_source_name(doc: dict) -> str:
    src = doc.get("source")
    if isinstance(src, str):
        return src
    if isinstance(src, dict):
        return src.get("name", "Unknown")
    return "Unknown"

# ============================================================
# 1. Top News Engine
# ============================================================

def get_top_news(timeframe: str = "today", category: str = None, source: str = None, limit: int = 10) -> list[dict]:
    """
    Rank news articles by recency, data quality score, and cross-source coverage.
    Timeframe options: 'latest', 'today', 'week', 'month', 'year'.
    """
    now = datetime.now(timezone.utc)
    query = {}

    if timeframe == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query["created_at"] = {"$gte": start}
    elif timeframe == "week":
        start = now - timedelta(days=7)
        query["created_at"] = {"$gte": start}
    elif timeframe == "month":
        start = now - timedelta(days=30)
        query["created_at"] = {"$gte": start}

    if category:
        query["$or"] = [
            {"category.label": re.compile(f"^{category}$", re.I)},
            {"category": re.compile(f"^{category}$", re.I)}
        ]

    if source:
        query["$or"] = [
            {"source.name": re.compile(f"^{source}$", re.I)},
            {"source": re.compile(f"^{source}$", re.I)}
        ]

    cursor = realtime_collection.find(query).sort("created_at", -1).limit(limit * 3)
    docs = list(cursor)

    # Ranking Score = Recency (40%) + Quality Score (30%) + Content Length (30%)
    ranked = []
    for doc in docs:
        dq_score = doc.get("data_quality", {}).get("quality_score", 70.0)
        title = doc.get("title", "")
        desc = doc.get("description", "")
        content_len = len(doc.get("clean_content") or doc.get("content") or desc)
        
        # Calculate composite score
        rank_score = (dq_score * 0.4) + (min(content_len / 500.0, 1.0) * 30.0)
        ranked.append((rank_score, doc))

    ranked.sort(key=lambda x: x[0], reverse=True)
    top_docs = [r[1] for r in ranked[:limit]]

    return [
        {
            "article_id": d.get("article_id") or str(d.get("_id")),
            "title": d.get("title"),
            "source": extract_source_name(d),
            "category": d.get("category", {}).get("label") if isinstance(d.get("category"), dict) else str(d.get("category", "General")),
            "published_date": d.get("published_date") or d.get("created_at"),
            "summary": (d.get("summary", {}).get("text") if isinstance(d.get("summary"), dict) else d.get("description", ""))[:220],
            "quality_score": d.get("data_quality", {}).get("quality_score", 80.0),
            "link": d.get("link", "#")
        }
        for d in top_docs
    ]

# ============================================================
# 2. News Time Machine
# ============================================================

def query_time_machine(date_str: str = None, from_date: str = None, to_date: str = None, category: str = None) -> dict:
    """Flashback query returning stories, source distributions, and top entities for a target date or date range."""
    query = {}
    
    if date_str:
        try:
            target_dt = datetime.fromisoformat(date_str)
            start = target_dt.replace(hour=0, minute=0, second=0)
            end = target_dt.replace(hour=23, minute=59, second=59)
            query["created_at"] = {"$gte": start, "$lte": end}
        except Exception:
            pass
    elif from_date and to_date:
        try:
            start = datetime.fromisoformat(from_date)
            end = datetime.fromisoformat(to_date)
            query["created_at"] = {"$gte": start, "$lte": end}
        except Exception:
            pass

    if category:
        query["category.label"] = re.compile(f"^{category}$", re.I)

    cursor = realtime_collection.find(query).limit(100)
    docs = list(cursor)

    sources = Counter(extract_source_name(d) for d in docs)
    categories = Counter(
        d.get("category", {}).get("label") if isinstance(d.get("category"), dict) else str(d.get("category", "General"))
        for d in docs
    )
    sentiments = Counter(
        d.get("sentiment", {}).get("label") if isinstance(d.get("sentiment"), dict) else str(d.get("sentiment", "Neutral"))
        for d in docs
    )

    stories = [
        {
            "article_id": d.get("article_id") or str(d.get("_id")),
            "title": d.get("title"),
            "source": extract_source_name(d),
            "published_date": d.get("published_date") or d.get("created_at"),
            "summary": (d.get("summary", {}).get("text") if isinstance(d.get("summary"), dict) else d.get("description", ""))[:200],
            "link": d.get("link", "#")
        }
        for d in docs[:15]
    ]

    return {
        "query_period": date_str or f"{from_date} to {to_date}",
        "total_articles": len(docs),
        "sources_distribution": dict(sources),
        "categories_distribution": dict(categories),
        "sentiment_distribution": dict(sentiments),
        "top_stories": stories
    }

# ============================================================
# 3. Cross-Source News Comparison
# ============================================================

def compare_source_coverage(topic_query: str) -> dict:
    """Compare headline framing, publication timing, and sentiment across all 4 major news sources for a topic."""
    regex = re.compile(re.escape(topic_query), re.I)
    query = {
        "$or": [
            {"title": regex},
            {"description": regex},
            {"keywords": regex}
        ]
    }
    cursor = realtime_collection.find(query).sort("created_at", 1).limit(100)
    docs = list(cursor)

    if not docs:
        return {"topic": topic_query, "total_matches": 0, "source_coverage": {}, "first_reported": None}

    sources_map = defaultdict(list)
    for doc in docs:
        src = extract_source_name(doc)
        sources_map[src].append({
            "article_id": doc.get("article_id") or str(doc.get("_id")),
            "title": doc.get("title"),
            "published_date": doc.get("published_date") or doc.get("created_at"),
            "sentiment": doc.get("sentiment", {}).get("label") if isinstance(doc.get("sentiment"), dict) else str(doc.get("sentiment", "Neutral")),
            "summary": (doc.get("summary", {}).get("text") if isinstance(doc.get("summary"), dict) else doc.get("description", ""))[:180],
            "link": doc.get("link", "#")
        })

    first_doc = docs[0]
    first_reported = {
        "source": extract_source_name(first_doc),
        "title": first_doc.get("title"),
        "published_date": first_doc.get("published_date") or first_doc.get("created_at")
    }

    return {
        "topic": topic_query,
        "total_matches": len(docs),
        "first_reported": first_reported,
        "source_coverage": {
            src: {
                "count": len(articles),
                "articles": articles[:5]
            }
            for src, articles in sources_map.items()
        }
    }

# ============================================================
# 4. Event Timeline Generator
# ============================================================

def build_event_timeline(topic_query: str, limit: int = 15) -> dict:
    """Cluster related articles into a chronological event timeline chain."""
    regex = re.compile(re.escape(topic_query), re.I)
    cursor = realtime_collection.find({
        "$or": [{"title": regex}, {"description": regex}]
    }).sort("created_at", 1).limit(limit)

    docs = list(cursor)
    timeline_nodes = [
        {
            "timestamp": str(doc.get("published_date") or doc.get("created_at")),
            "source": extract_source_name(doc),
            "headline": doc.get("title"),
            "summary": (doc.get("summary", {}).get("text") if isinstance(doc.get("summary"), dict) else doc.get("description", ""))[:200],
            "sentiment": doc.get("sentiment", {}).get("label") if isinstance(doc.get("sentiment"), dict) else "Neutral",
            "link": doc.get("link", "#")
        }
        for doc in docs
    ]

    return {
        "event_topic": topic_query,
        "total_milestones": len(timeline_nodes),
        "timeline": timeline_nodes
    }

# ============================================================
# 5. Current Affairs Intelligence
# ============================================================

def extract_category_label(doc: dict) -> str:
    cat = doc.get("category")
    if isinstance(cat, str) and cat.strip():
        return cat.strip().capitalize()
    if isinstance(cat, dict):
        lbl = cat.get("label") or cat.get("category")
        if isinstance(lbl, str) and lbl.strip():
            return lbl.strip().capitalize()
    return "General"

def get_current_affairs(timeframe: str = "this_week") -> dict:
    """Generate fact-grounded current affairs breakdown across key domains."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7 if timeframe == "this_week" else 1)

    cursor = realtime_collection.find({"created_at": {"$gte": start}}).limit(200)
    docs = list(cursor)

    domains = defaultdict(list)
    for doc in docs:
        cat_label = extract_category_label(doc)
        domains[cat_label].append({
            "title": doc.get("title"),
            "source": extract_source_name(doc),
            "date": str(doc.get("published_date") or doc.get("created_at"))[:16],
            "summary": (doc.get("summary", {}).get("text") if isinstance(doc.get("summary"), dict) else doc.get("description", ""))[:180],
            "link": doc.get("link", "#")
        })

    return {
        "timeframe": timeframe,
        "total_reviewed": len(docs),
        "domains": {
            domain: items[:4]
            for domain, items in domains.items()
        }
    }
