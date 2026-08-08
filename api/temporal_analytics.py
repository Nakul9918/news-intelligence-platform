"""
=====================================================
Temporal Analytics Engine for News Intelligence Platform
=====================================================
Provides read-only temporal volume trends, source/category/sentiment
timelines, spike detection, emerging keywords/entities, and cross-source
activity correlation.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

def parse_any_timestamp(ts) -> Optional[datetime]:
    """Safely parse string, datetime, or BSON timestamp into UTC datetime."""
    if not ts:
        return None
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)
    if isinstance(ts, str):
        ts_clean = ts.strip()
        try:
            return datetime.fromisoformat(ts_clean.replace(" ", "T"))
        except Exception:
            try:
                from dateutil import parser
                return parser.parse(ts_clean).astimezone(timezone.utc)
            except Exception:
                return None
    return None

def extract_article_timestamp(article: dict) -> Optional[datetime]:
    """Extract primary published_date with fallback to created_at or updated_at."""
    return (
        parse_any_timestamp(article.get("published_date")) or
        parse_any_timestamp(article.get("created_at")) or
        parse_any_timestamp(article.get("updated_at")) or
        parse_any_timestamp(article.get("fetched_at"))
    )

def extract_source_name(article: dict) -> str:
    """Extract string source name from article dict."""
    src = article.get("source")
    if isinstance(src, dict):
        return src.get("name") or "Unknown"
    return str(src or "Unknown")

def extract_category_label(article: dict) -> str:
    """Extract string category label from article dict."""
    cat = article.get("category")
    if isinstance(cat, dict):
        return cat.get("label") or "General"
    return str(cat or "General")

def extract_sentiment_label(article: dict) -> str:
    """Extract string sentiment label from article dict."""
    sent = article.get("sentiment")
    if isinstance(sent, dict):
        return sent.get("label") or "Neutral"
    return str(sent or "Neutral")

def bucket_timestamp(dt: datetime, bucket: str) -> str:
    """Format datetime into target bucket string (5m, 15m, 30m, 1h, 1d)."""
    if bucket == "5m":
        minute = (dt.minute // 5) * 5
        b_dt = dt.replace(minute=minute, second=0, microsecond=0)
        return b_dt.strftime("%Y-%m-%d %H:%M")
    elif bucket == "15m":
        minute = (dt.minute // 15) * 15
        b_dt = dt.replace(minute=minute, second=0, microsecond=0)
        return b_dt.strftime("%Y-%m-%d %H:%M")
    elif bucket == "30m":
        minute = (dt.minute // 30) * 30
        b_dt = dt.replace(minute=minute, second=0, microsecond=0)
        return b_dt.strftime("%Y-%m-%d %H:%M")
    elif bucket == "1d":
        return dt.strftime("%Y-%m-%d")
    else: # 1h default
        b_dt = dt.replace(minute=0, second=0, microsecond=0)
        return b_dt.strftime("%Y-%m-%d %H:00")

def get_window_cutoff(coll, window_str: str) -> tuple[datetime, datetime]:
    """
    Returns (start_cutoff, end_cutoff).
    Uses the latest timestamp in the database as reference if historical,
    or current UTC time.
    """
    now = datetime.now(timezone.utc)
    
    # Get latest article timestamp in DB to anchor historical trends
    latest_doc = coll.find_one({}, sort=[("_id", -1)])
    latest_dt = extract_article_timestamp(latest_doc) if latest_doc else None
    anchor_dt = latest_dt if (latest_dt and latest_dt > now - timedelta(days=365)) else now

    if window_str == "1h":
        start_dt = anchor_dt - timedelta(hours=1)
    elif window_str == "6h":
        start_dt = anchor_dt - timedelta(hours=6)
    elif window_str == "24h":
        start_dt = anchor_dt - timedelta(hours=24)
    elif window_str == "7d":
        start_dt = anchor_dt - timedelta(days=7)
    elif window_str == "30d":
        start_dt = anchor_dt - timedelta(days=30)
    else: # all
        start_dt = anchor_dt - timedelta(days=365)

    return start_dt, anchor_dt

def get_volume_analytics(coll, window: str = "24h", bucket: str = "1h") -> dict:
    """Calculates news article volume over time buckets."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    
    bucket_counts = Counter()
    cursor = coll.find({}, {"published_date": 1, "created_at": 1, "updated_at": 1}).sort("created_at", -1).limit(5000)

    total_matched = 0
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            b_key = bucket_timestamp(dt, bucket)
            bucket_counts[b_key] += 1
            total_matched += 1

    sorted_buckets = sorted(bucket_counts.items(), key=lambda x: x[0])
    data_points = [{"timestamp": k, "count": v} for k, v in sorted_buckets]

    return {
        "window": window,
        "bucket": bucket,
        "total_count": total_matched,
        "data": data_points
    }

def get_source_analytics(coll, window: str = "24h", bucket: str = "1h") -> dict:
    """Calculates article activity by news source over time buckets."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    
    source_buckets = defaultdict(Counter)
    all_sources = set()

    cursor = coll.find({}, {"source": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            src = extract_source_name(doc)
            all_sources.add(src)
            b_key = bucket_timestamp(dt, bucket)
            source_buckets[b_key][src] += 1

    sorted_times = sorted(source_buckets.keys())
    sources_list = sorted(list(all_sources))
    
    data_points = []
    for t in sorted_times:
        item = {"timestamp": t}
        for s in sources_list:
            item[s] = source_buckets[t][s]
        data_points.append(item)

    return {
        "window": window,
        "bucket": bucket,
        "sources": sources_list,
        "data": data_points
    }

def get_category_analytics(coll, window: str = "24h", bucket: str = "1h") -> dict:
    """Calculates article activity by NLP category over time buckets."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    
    cat_buckets = defaultdict(Counter)
    all_categories = set()

    cursor = coll.find({}, {"category": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            cat = extract_category_label(doc)
            all_categories.add(cat)
            b_key = bucket_timestamp(dt, bucket)
            cat_buckets[b_key][cat] += 1

    sorted_times = sorted(cat_buckets.keys())
    categories_list = sorted(list(all_categories))
    
    data_points = []
    for t in sorted_times:
        item = {"timestamp": t}
        for c in categories_list:
            item[c] = cat_buckets[t][c]
        data_points.append(item)

    return {
        "window": window,
        "bucket": bucket,
        "categories": categories_list,
        "data": data_points
    }

def get_sentiment_analytics(coll, window: str = "24h", bucket: str = "1h") -> dict:
    """Calculates sentiment trend breakdown over time buckets."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    
    sent_buckets = defaultdict(Counter)

    cursor = coll.find({}, {"sentiment": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            sent = extract_sentiment_label(doc)
            b_key = bucket_timestamp(dt, bucket)
            sent_buckets[b_key][sent] += 1

    sorted_times = sorted(sent_buckets.keys())
    data_points = []
    for t in sorted_times:
        data_points.append({
            "timestamp": t,
            "Positive": sent_buckets[t]["Positive"],
            "Neutral": sent_buckets[t]["Neutral"],
            "Negative": sent_buckets[t]["Negative"]
        })

    return {
        "window": window,
        "bucket": bucket,
        "data": data_points
    }

def get_spike_analytics(coll, window: str = "24h", multiplier: float = 2.0) -> dict:
    """Detects volume spikes in overall news, sources, and categories against baseline."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    mid_dt = start_dt + (end_dt - start_dt) / 2

    recent_counts = Counter()
    baseline_counts = Counter()
    
    source_recent = Counter()
    source_baseline = Counter()
    
    category_recent = Counter()
    category_baseline = Counter()

    cursor = coll.find({}, {"source": 1, "category": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            src = extract_source_name(doc)
            cat = extract_category_label(doc)
            if dt >= mid_dt:
                recent_counts["total"] += 1
                source_recent[src] += 1
                category_recent[cat] += 1
            else:
                baseline_counts["total"] += 1
                source_baseline[src] += 1
                category_baseline[cat] += 1

    curr_vol = recent_counts["total"]
    base_vol = max(baseline_counts["total"], 1)
    is_overall_spike = (curr_vol >= base_vol * multiplier) and (curr_vol > 5)

    source_spikes = []
    for src, count in source_recent.items():
        base = max(source_baseline[src], 1)
        if count >= base * multiplier and count > 3:
            source_spikes.append({
                "source": src,
                "current_volume": count,
                "baseline_volume": base,
                "status": "UNUSUAL_ACTIVITY"
            })

    category_spikes = []
    for cat, count in category_recent.items():
        base = max(category_baseline[cat], 1)
        if count >= base * multiplier and count > 3:
            category_spikes.append({
                "category": cat,
                "current_volume": count,
                "baseline_volume": base,
                "status": "UNUSUAL_ACTIVITY"
            })

    return {
        "overall": {
            "status": "UNUSUAL_ACTIVITY" if is_overall_spike else "NORMAL",
            "current_volume": curr_vol,
            "baseline_volume": base_vol,
            "multiplier": multiplier,
            "message": "Unusual news activity detected" if is_overall_spike else "News activity normal"
        },
        "source_spikes": source_spikes,
        "category_spikes": category_spikes
    }

def get_emerging_keywords(coll, limit: int = 10) -> dict:
    """Calculates top emerging keywords with percentage growth."""
    kw_recent = Counter()
    kw_baseline = Counter()
    
    cursor = coll.find({"processing.status": "COMPLETED"}, {"keywords": 1, "created_at": 1}).sort("created_at", -1).limit(2000)
    docs = list(cursor)
    half = len(docs) // 2

    for i, doc in enumerate(docs):
        kws = doc.get("keywords", [])
        if not isinstance(kws, list):
            continue
        for kw in kws:
            if isinstance(kw, str) and len(kw) > 3:
                if i < half:
                    kw_recent[kw] += 1
                else:
                    kw_baseline[kw] += 1

    emerging = []
    for kw, recent_cnt in kw_recent.most_common(50):
        base_cnt = kw_baseline[kw]
        pct = ((recent_cnt - base_cnt) / max(base_cnt, 1)) * 100.0
        emerging.append({
            "keyword": kw,
            "recent_mentions": recent_cnt,
            "previous_mentions": base_cnt,
            "growth_pct": round(pct, 1)
        })

    emerging.sort(key=lambda x: x["growth_pct"], reverse=True)
    return {"keywords": emerging[:limit]}

def get_emerging_entities(coll, limit: int = 10) -> dict:
    """Calculates top emerging NER entities with percentage growth."""
    ent_recent = Counter()
    ent_baseline = Counter()
    ent_types = {}

    cursor = coll.find({"processing.status": "COMPLETED"}, {"entities": 1, "created_at": 1}).sort("created_at", -1).limit(2000)
    docs = list(cursor)
    half = len(docs) // 2

    for i, doc in enumerate(docs):
        entities = doc.get("entities", [])
        if not isinstance(entities, list):
            continue
        for item in entities:
            if isinstance(item, dict):
                e_name = item.get("entity") or item.get("text")
                e_type = item.get("type") or item.get("label") or "ENTITY"
            elif isinstance(item, str):
                e_name = item
                e_type = "ENTITY"
            else:
                continue

            if e_name and len(e_name) > 2:
                ent_types[e_name] = e_type
                if i < half:
                    ent_recent[e_name] += 1
                else:
                    ent_baseline[e_name] += 1

    emerging = []
    for e_name, recent_cnt in ent_recent.most_common(50):
        base_cnt = ent_baseline[e_name]
        pct = ((recent_cnt - base_cnt) / max(base_cnt, 1)) * 100.0
        emerging.append({
            "entity": e_name,
            "type": ent_types.get(e_name, "ENTITY"),
            "recent_mentions": recent_cnt,
            "previous_mentions": base_cnt,
            "growth_pct": round(pct, 1)
        })

    emerging.sort(key=lambda x: x["growth_pct"], reverse=True)
    return {"entities": emerging[:limit]}

def get_cross_source_analytics(coll, min_sources: int = 2) -> dict:
    """Identifies topics/keywords reported across multiple distinct sources."""
    topic_sources = defaultdict(set)
    topic_count = Counter()

    cursor = coll.find({"processing.status": "COMPLETED"}, {"keywords": 1, "entities": 1, "source": 1}).sort("created_at", -1).limit(1000)
    for doc in cursor:
        src = extract_source_name(doc)
        kws = doc.get("keywords", [])
        if isinstance(kws, list):
            for kw in kws:
                if isinstance(kw, str) and len(kw) > 3:
                    topic_sources[kw].add(src)
                    topic_count[kw] += 1

        entities = doc.get("entities", [])
        if isinstance(entities, list):
            for ent in entities:
                e_name = ent.get("entity") if isinstance(ent, dict) else (ent if isinstance(ent, str) else None)
                if e_name and len(e_name) > 2:
                    topic_sources[e_name].add(src)
                    topic_count[e_name] += 1

    cross_topics = []
    for topic, sources in topic_sources.items():
        if len(sources) >= min_sources:
            cross_topics.append({
                "topic": topic,
                "sources_count": len(sources),
                "sources": sorted(list(sources)),
                "article_count": topic_count[topic],
                "signal": "Potential Cross-Source Topic"
            })

    cross_topics.sort(key=lambda x: (x["sources_count"], x["article_count"]), reverse=True)
    return {"topics": cross_topics[:10]}
