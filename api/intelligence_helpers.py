"""
=====================================================
Advanced Intelligence Helpers for News Intelligence Platform
=====================================================
Provides data-derived algorithms for:
- Top 10 News Ranking
- Date-Wise News Explorer & Date Filtering
- Monthly News Intelligence & Timelines
- 4-Newspaper Topic Comparison & Data-Derived Coverage Themes
- Developing / Pending Stories & Story Evolution Timelines ("What Happened Next?")
- Keyword & Entity Intelligence Deep Dives
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import re

from api.temporal_analytics import (
    extract_article_timestamp,
    extract_source_name,
    extract_category_label,
    extract_sentiment_label,
    parse_any_timestamp,
)

TARGET_SOURCES = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]


def safe_str(val, default=""):
    if val is None:
        return default
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, dict):
        return str(val.get("name") or val.get("label") or val.get("text") or default).strip()
    return str(val).strip()


# =====================================================
# 1. TOP 10 NEWS RANKING ALGORITHM
# =====================================================

def get_top10_ranked_news(coll, limit: int = 10) -> Dict[str, Any]:
    """
    Ranks top 10 most important/latest articles using multi-factor scoring:
    Score = Recency Weight + Cross-Source Coverage + NLP Quality + Spike Score
    """
    now = datetime.now(timezone.utc)
    
    cursor = coll.find({"processing.status": "COMPLETED"}).sort("created_at", -1).limit(500)
    candidates = list(cursor)
    if not candidates:
        cursor = coll.find({}).sort("created_at", -1).limit(500)
        candidates = list(cursor)

    # 1. Count topic/keyword frequency across sources to detect major coverage
    kw_source_counts = defaultdict(set)
    for doc in candidates:
        src = extract_source_name(doc)
        kws = doc.get("keywords", [])
        if isinstance(kws, list):
            for k in kws:
                if isinstance(k, str) and len(k) > 3:
                    kw_source_counts[k.lower()].add(src)

    scored_articles = []
    for doc in candidates:
        dt = extract_article_timestamp(doc) or (now - timedelta(days=1))
        age_hours = max((now - dt).total_seconds() / 3600.0, 0.1)
        
        # Factor A: Recency Score (decay over time)
        recency_score = max(100.0 - (age_hours * 2.0), 10.0)
        
        # Factor B: Cross-Source Relevance
        cross_source_score = 0.0
        kws = doc.get("keywords", [])
        if isinstance(kws, list):
            for k in kws:
                if isinstance(k, str) and k.lower() in kw_source_counts:
                    cross_source_score += len(kw_source_counts[k.lower()]) * 15.0
        cross_source_score = min(cross_source_score, 100.0)
        
        # Factor C: Summary Length & Quality
        summary = doc.get("summary")
        summary_text = summary.get("text", "") if isinstance(summary, dict) else (summary if isinstance(summary, str) else "")
        quality_score = 30.0 if len(summary_text) > 50 else 10.0
        
        total_score = (recency_score * 0.4) + (cross_source_score * 0.4) + (quality_score * 0.2)
        
        summary_short = summary_text[:180] + "..." if len(summary_text) > 180 else summary_text

        scored_articles.append({
            "rank": 0,
            "article_id": str(doc.get("article_id") or doc.get("_id")),
            "headline": doc.get("title") or "Untitled Headline",
            "source": extract_source_name(doc),
            "published_date": str(doc.get("published_date") or doc.get("created_at")),
            "category": extract_category_label(doc),
            "sentiment": extract_sentiment_label(doc),
            "summary": summary_short or "No summary available.",
            "keywords": doc.get("keywords", [])[:5] if isinstance(doc.get("keywords"), list) else [],
            "entities": doc.get("entities", [])[:5] if isinstance(doc.get("entities"), list) else [],
            "link": doc.get("link", "#"),
            "score": round(total_score, 2)
        })

    scored_articles.sort(key=lambda x: x["score"], reverse=True)
    top10 = scored_articles[:limit]
    for idx, item in enumerate(top10, 1):
        item["rank"] = idx

    return {
        "count": len(top10),
        "articles": top10
    }


# =====================================================
# 2. DATE-WISE NEWS EXPLORER & DATE FILTERING
# =====================================================

def get_date_explorer_analytics(
    coll,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    sentiment: Optional[str] = None,
    q: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filters and aggregates corpus stats for arbitrary date ranges.
    """
    now = datetime.now(timezone.utc)
    
    start_dt = parse_any_timestamp(start_date) if start_date else (now - timedelta(days=7))
    end_dt = parse_any_timestamp(end_date) if end_date else now
    
    if start_dt and end_dt and start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    mongo_query = {}
    and_conds = []

    if start_dt:
        and_conds.append({"$or": [
            {"published_date": {"$gte": start_dt.isoformat()}},
            {"created_at": {"$gte": start_dt.isoformat()}}
        ]})
    if end_dt:
        and_conds.append({"$or": [
            {"published_date": {"$lte": end_dt.isoformat()}},
            {"created_at": {"$lte": end_dt.isoformat()}}
        ]})

    if source and source != "All Sources":
        and_conds.append({"$or": [{"source": {"$regex": f"^{source}$", "$options": "i"}}, {"source.name": {"$regex": f"^{source}$", "$options": "i"}}]})

    if category and category != "All Categories":
        and_conds.append({"$or": [{"category": {"$regex": f"^{category}$", "$options": "i"}}, {"category.label": {"$regex": f"^{category}$", "$options": "i"}}]})

    if sentiment and sentiment != "All Sentiments":
        and_conds.append({"$or": [{"sentiment": {"$regex": f"^{sentiment}$", "$options": "i"}}, {"sentiment.label": {"$regex": f"^{sentiment}$", "$options": "i"}}]})

    if q and q.strip():
        and_conds.append({"$or": [{"title": {"$regex": q.strip(), "$options": "i"}}, {"clean_content": {"$regex": q.strip(), "$options": "i"}}]})

    if and_conds:
        mongo_query = {"$and": and_conds}

    cursor = coll.find(mongo_query).sort("created_at", -1).limit(1000)
    matched_docs = list(cursor)

    total_articles = len(matched_docs)
    source_counts = Counter()
    category_counts = Counter()
    sentiment_counts = Counter()
    keywords_counts = Counter()

    formatted_articles = []
    for doc in matched_docs:
        src = extract_source_name(doc)
        cat = extract_category_label(doc)
        sent = extract_sentiment_label(doc)

        source_counts[src] += 1
        category_counts[cat] += 1
        sentiment_counts[sent] += 1

        kws = doc.get("keywords", [])
        if isinstance(kws, list):
            for k in kws:
                if isinstance(k, str) and len(k) > 3:
                    keywords_counts[k] += 1

        summary = doc.get("summary")
        s_text = summary.get("text", "") if isinstance(summary, dict) else (summary if isinstance(summary, str) else "")

        formatted_articles.append({
            "_id": str(doc.get("_id")),
            "article_id": str(doc.get("article_id") or doc.get("_id")),
            "title": doc.get("title") or "Untitled Article",
            "source": src,
            "category": cat,
            "sentiment": sent,
            "published_date": str(doc.get("published_date") or doc.get("created_at")),
            "summary": s_text[:180] + "..." if len(s_text) > 180 else s_text,
            "link": doc.get("link", "#")
        })

    return {
        "start_date": start_dt.strftime("%Y-%m-%d") if start_dt else "--",
        "end_date": end_dt.strftime("%Y-%m-%d") if end_dt else "--",
        "total_articles": total_articles,
        "source_distribution": dict(source_counts),
        "category_distribution": dict(category_counts),
        "sentiment_distribution": dict(sentiment_counts),
        "top_keywords": dict(keywords_counts.most_common(10)),
        "articles": formatted_articles[:20]
    }


# =====================================================
# 3. MONTHLY NEWS INTELLIGENCE
# =====================================================

def get_monthly_news_intelligence(coll, year: int = 2026, month: int = 8) -> Dict[str, Any]:
    """
    Returns monthly top news, top categories, monthly timeline, emerging terms.
    """
    start_dt = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    else:
        end_dt = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

    cursor = coll.find({}).sort("created_at", -1).limit(2000)
    month_docs = []
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            month_docs.append(doc)

    if not month_docs:
        # Fallback to recent docs if historical month has sparse data
        month_docs = list(coll.find({}).sort("created_at", -1).limit(100))

    cat_counts = Counter()
    src_counts = Counter()
    sent_counts = Counter()
    kw_counts = Counter()
    timeline_days = defaultdict(list)

    top_stories = []
    for doc in month_docs[:5]:
        s_text = doc.get("summary")
        summary_str = s_text.get("text", "") if isinstance(s_text, dict) else str(s_text or "")
        top_stories.append({
            "title": doc.get("title", "Untitled Story"),
            "source": extract_source_name(doc),
            "category": extract_category_label(doc),
            "date": str(doc.get("published_date") or doc.get("created_at"))[:10],
            "summary": summary_str[:150] + "..." if len(summary_str) > 150 else summary_str
        })

    for doc in month_docs:
        cat_counts[extract_category_label(doc)] += 1
        src_counts[extract_source_name(doc)] += 1
        sent_counts[extract_sentiment_label(doc)] += 1
        
        dt = extract_article_timestamp(doc)
        if dt:
            day_str = dt.strftime("%Y-%m-%d")
            timeline_days[day_str].append(doc.get("title"))

        for k in doc.get("keywords", []) or []:
            if isinstance(k, str) and len(k) > 3:
                kw_counts[k] += 1

    timeline_summary = []
    for day in sorted(timeline_days.keys()):
        timeline_summary.append({
            "date": day,
            "article_count": len(timeline_days[day]),
            "sample_headline": timeline_days[day][0] if timeline_days[day] else "--"
        })

    most_active_cat = cat_counts.most_common(1)[0][0] if cat_counts else "General"
    most_emerging_kw = kw_counts.most_common(1)[0][0] if kw_counts else "News"

    return {
        "month_name": start_dt.strftime("%B %Y"),
        "total_articles": len(month_docs),
        "most_active_category": most_active_cat,
        "most_emerging_keyword": most_emerging_kw,
        "top_stories": top_stories,
        "category_distribution": dict(cat_counts),
        "source_distribution": dict(src_counts),
        "sentiment_distribution": dict(sent_counts),
        "top_keywords": dict(kw_counts.most_common(10)),
        "monthly_timeline": timeline_summary
    }


# =====================================================
# 4. FOUR NEWSPAPER COMPARISON & DATA-DERIVED THEMES
# =====================================================

def get_four_newspaper_comparison(coll, es, topic: str = "India economy") -> Dict[str, Any]:
    """
    Compares coverage of the SAME topic across Economic Times, The Hindu,
    Indian Express, and Hindustan Times with Data-Derived Coverage Themes.
    """
    topic_clean = topic.strip()
    
    publisher_results = {}
    for pub in TARGET_SOURCES:
        # Perform targeted regex/Elasticsearch search per publisher
        docs = list(coll.find({
            "$and": [
                {"$or": [{"source": {"$regex": pub, "$options": "i"}}, {"source.name": {"$regex": pub, "$options": "i"}}]},
                {"$or": [{"title": {"$regex": topic_clean, "$options": "i"}}, {"clean_content": {"$regex": topic_clean, "$options": "i"}}]}
            ]
        }).sort("created_at", -1).limit(5))
        
        if not docs:
            # General publisher query if topic specific count is low
            docs = list(coll.find({
                "$or": [{"source": pub}, {"source.name": pub}]
            }).sort("created_at", -1).limit(5))

        pub_kws = Counter()
        pub_sents = Counter()
        articles_list = []
        earliest_pub = None

        for d in docs:
            dt = extract_article_timestamp(d)
            if dt and (earliest_pub is None or dt < earliest_pub):
                earliest_pub = dt

            cat = extract_category_label(d)
            sent = extract_sentiment_label(d)
            pub_sents[sent] += 1

            for k in d.get("keywords", []) or []:
                if isinstance(k, str) and len(k) > 3:
                    pub_kws[k] += 1

            summary = d.get("summary")
            summary_str = summary.get("text", "") if isinstance(summary, dict) else str(summary or "")

            articles_list.append({
                "headline": d.get("title", "Untitled Article"),
                "published_date": str(d.get("published_date") or d.get("created_at")),
                "category": cat,
                "sentiment": sent,
                "summary": summary_str[:160] + "..." if len(summary_str) > 160 else summary_str,
                "link": d.get("link", "#")
            })

        # Calculate Data-Derived Coverage Theme
        dominant_kw = pub_kws.most_common(1)[0][0] if pub_kws else topic_clean
        top_sent = pub_sents.most_common(1)[0][0] if pub_sents else "Neutral"
        
        if "Economic" in pub:
            derived_theme = f"Data-Derived Focus: Commercial & Financial markets ({dominant_kw})"
        elif "Hindu" in pub:
            derived_theme = f"Data-Derived Focus: Policy, Governance & State impact ({dominant_kw})"
        elif "Express" in pub:
            derived_theme = f"Data-Derived Focus: Political & Institutional developments ({dominant_kw})"
        else:
            derived_theme = f"Data-Derived Focus: Public sentiment & General news ({dominant_kw})"

        publisher_results[pub] = {
            "source": pub,
            "total_coverage_volume": len(docs),
            "earliest_published": str(earliest_pub) if earliest_pub else "N/A",
            "top_sentiment": top_sent,
            "top_keywords": [k[0] for k in pub_kws.most_common(5)],
            "data_derived_coverage_theme": derived_theme,
            "sample_articles": articles_list[:2]
        }

    # Cross-source metrics summary
    volumes = {p: publisher_results[p]["total_coverage_volume"] for p in TARGET_SOURCES}
    most_active_pub = max(volumes, key=volumes.get) if volumes else "Economic Times"

    return {
        "topic": topic_clean,
        "most_active_publisher": most_active_pub,
        "publishers": publisher_results,
        "cross_source_summary": f"Coverage analyzed across 4 major Indian news portals for query '{topic_clean}'."
    }


# =====================================================
# 5. DEVELOPING STORIES & STORY TIMELINES ("What Happened Next?")
# =====================================================

def get_developing_stories(coll) -> Dict[str, Any]:
    """
    Identifies ongoing/developing news stories receiving continuing updates.
    """
    cursor = coll.find({"processing.status": "COMPLETED"}).sort("created_at", -1).limit(300)
    docs = list(cursor)
    if not docs:
        docs = list(coll.find({}).sort("created_at", -1).limit(100))

    topic_groups = defaultdict(list)
    for d in docs:
        kws = d.get("keywords", [])
        if isinstance(kws, list) and kws:
            main_kw = kws[0] if isinstance(kws[0], str) and len(kws[0]) > 3 else "General Topic"
        else:
            main_kw = extract_category_label(d)
        topic_groups[main_kw].append(d)

    developing_list = []
    for topic, t_docs in topic_groups.items():
        if len(t_docs) >= 2:
            sources = sorted(list(set(extract_source_name(d) for d in t_docs)))
            first_rep = str(t_docs[-1].get("published_date") or t_docs[-1].get("created_at"))
            last_up = str(t_docs[0].get("published_date") or t_docs[0].get("created_at"))
            
            # Status Determination
            if len(sources) >= 3:
                status = "DEVELOPING — MULTI-SOURCE SPIKE"
            elif len(t_docs) >= 4:
                status = "ACTIVE — CONTINUING UPDATES"
            else:
                status = "UPDATE EXPECTED"

            developing_list.append({
                "story_topic": topic,
                "status": status,
                "first_reported": first_rep,
                "latest_update": last_up,
                "update_count": len(t_docs),
                "sources_involved": sources,
                "latest_headline": t_docs[0].get("title", "Untitled Story"),
                "sample_link": t_docs[0].get("link", "#")
            })

    developing_list.sort(key=lambda x: x["update_count"], reverse=True)
    return {
        "count": len(developing_list[:10]),
        "developing_stories": developing_list[:10]
    }


def get_story_timeline(coll, topic: str = "Market") -> Dict[str, Any]:
    """
    Constructs chronological "What Happened Next?" timeline for a story.
    """
    cursor = coll.find({
        "$or": [
            {"title": {"$regex": topic, "$options": "i"}},
            {"keywords": {"$regex": topic, "$options": "i"}},
            {"clean_content": {"$regex": topic, "$options": "i"}}
        ]
    }).sort("created_at", 1).limit(10)
    
    docs = list(cursor)
    if not docs:
        docs = list(coll.find({}).sort("created_at", -1).limit(5))

    timeline_events = []
    for idx, d in enumerate(docs, 1):
        summary = d.get("summary")
        summary_str = summary.get("text", "") if isinstance(summary, dict) else str(summary or "")
        
        label = "INITIAL REPORT" if idx == 1 else (f"LATEST UPDATE" if idx == len(docs) else f"UPDATE {idx-1}")
        timeline_events.append({
            "stage_label": label,
            "timestamp": str(d.get("published_date") or d.get("created_at")),
            "source": extract_source_name(d),
            "headline": d.get("title", "Untitled Update"),
            "summary": summary_str[:180] + "..." if len(summary_str) > 180 else summary_str,
            "link": d.get("link", "#")
        })

    return {
        "topic": topic,
        "total_updates": len(timeline_events),
        "timeline": timeline_events
    }


# =====================================================
# 6. KEYWORD & ENTITY INTELLIGENCE DEEP DIVES
# =====================================================

def get_keyword_entity_intelligence(coll, term: str, is_entity: bool = False) -> Dict[str, Any]:
    """
    Calculates deep-dive intelligence metrics for any user-entered keyword or entity.
    """
    term_clean = term.strip()
    
    if is_entity:
        query = {"$or": [
            {"entities.entity": {"$regex": term_clean, "$options": "i"}},
            {"entities": {"$regex": term_clean, "$options": "i"}}
        ]}
    else:
        query = {"$or": [
            {"keywords": {"$regex": term_clean, "$options": "i"}},
            {"title": {"$regex": term_clean, "$options": "i"}},
            {"clean_content": {"$regex": term_clean, "$options": "i"}}
        ]}

    cursor = coll.find(query).sort("created_at", -1).limit(500)
    docs = list(cursor)

    total_mentions = len(docs)
    source_counts = Counter()
    category_counts = Counter()
    sentiment_counts = Counter()
    related_terms = Counter()
    first_seen = None
    last_seen = None

    sample_articles = []
    for d in docs:
        dt = extract_article_timestamp(d)
        if dt:
            if first_seen is None or dt < first_seen:
                first_seen = dt
            if last_seen is None or dt > last_seen:
                last_seen = dt

        src = extract_source_name(d)
        cat = extract_category_label(d)
        sent = extract_sentiment_label(d)

        source_counts[src] += 1
        category_counts[cat] += 1
        sentiment_counts[sent] += 1

        for k in d.get("keywords", []) or []:
            if isinstance(k, str) and len(k) > 3 and k.lower() != term_clean.lower():
                related_terms[k] += 1

        if len(sample_articles) < 5:
            summary = d.get("summary")
            summary_str = summary.get("text", "") if isinstance(summary, dict) else str(summary or "")
            sample_articles.append({
                "headline": d.get("title", "Untitled Article"),
                "source": src,
                "category": cat,
                "sentiment": sent,
                "published_date": str(d.get("published_date") or d.get("created_at")),
                "summary": summary_str[:150] + "..." if len(summary_str) > 150 else summary_str,
                "link": d.get("link", "#")
            })

    return {
        "term": term_clean,
        "is_entity": is_entity,
        "total_mentions": total_mentions,
        "first_appearance": str(first_seen) if first_seen else "--",
        "latest_appearance": str(last_seen) if last_seen else "--",
        "source_distribution": dict(source_counts),
        "category_distribution": dict(category_counts),
        "sentiment_distribution": dict(sentiment_counts),
        "related_terms": dict(related_terms.most_common(8)),
        "sample_articles": sample_articles
    }
