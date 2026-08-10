"""
=====================================================
Temporal Analytics Engine for News Intelligence Platform
=====================================================
Production-grade, statistically defensible engine providing temporal volume dynamics,
deterministic trend direction, rolling standard-deviation spike intelligence,
emerging keywords/entities growth, cross-source topic correlation, and evidence lineage drill-down.
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
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
                dt = parser.parse(ts_clean)
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                return None
    return None


def extract_article_timestamp_with_quality(article: dict) -> Tuple[Optional[datetime], str]:
    """
    Extract primary published_date with fallback to created_at/updated_at.
    Returns (datetime, source_field_name).
    """
    p_dt = parse_any_timestamp(article.get("published_date"))
    if p_dt:
        return p_dt, "published_date"

    c_dt = parse_any_timestamp(article.get("created_at"))
    if c_dt:
        return c_dt, "created_at"

    u_dt = parse_any_timestamp(article.get("updated_at"))
    if u_dt:
        return u_dt, "updated_at"

    f_dt = parse_any_timestamp(article.get("fetched_at"))
    if f_dt:
        return f_dt, "fetched_at"

    return None, "invalid"


def extract_article_timestamp(article: dict) -> Optional[datetime]:
    """Extract datetime using canonical timestamp rules."""
    dt, _ = extract_article_timestamp_with_quality(article)
    return dt


def extract_source_name(article: dict) -> str:
    """Extract string source name from article dict."""
    src = article.get("source")
    if isinstance(src, dict):
        return src.get("name") or "Unknown Source"
    return str(src or "Unknown Source")


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


def get_recommended_bucket(window_str: str) -> str:
    """Determine optimal granularity bucket for a given date window."""
    w = window_str.lower()
    if w in ["1h", "6h", "24h", "48h", "2d", "today"]:
        return "1h"
    elif w in ["7d", "30d", "month", "this_month"]:
        return "1d"
    elif w in ["3m", "90d"]:
        return "1w"
    elif w in ["12m", "365d", "year", "all"]:
        return "1m"
    return "1d"


def bucket_timestamp(dt: datetime, bucket: str) -> str:
    """Format datetime into target bucket string (1h, 1d, 1w, 1m)."""
    b = bucket.lower()
    if b == "1h":
        b_dt = dt.replace(minute=0, second=0, microsecond=0)
        return b_dt.strftime("%Y-%m-%d %H:00")
    elif b == "1d":
        return dt.strftime("%Y-%m-%d")
    elif b == "1w":
        # Start of ISO week (Monday)
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    elif b == "1m":
        return dt.strftime("%Y-%m")
    else:  # default 1h
        b_dt = dt.replace(minute=0, second=0, microsecond=0)
        return b_dt.strftime("%Y-%m-%d %H:00")


def get_window_cutoff(coll, window_str: str) -> Tuple[datetime, datetime]:
    """Returns (start_cutoff, end_cutoff) anchored in real UTC time."""
    now = datetime.now(timezone.utc)
    w = window_str.lower()

    if w == "1h":
        start_dt = now - timedelta(hours=1)
    elif w == "6h":
        start_dt = now - timedelta(hours=6)
    elif w in ["24h", "today"]:
        start_dt = now - timedelta(hours=24)
    elif w in ["48h", "2d", "2days"]:
        start_dt = now - timedelta(hours=48)
    elif w == "7d":
        start_dt = now - timedelta(days=7)
    elif w in ["30d", "month", "this_month"]:
        start_dt = now - timedelta(days=30)
    elif w in ["3m", "90d"]:
        start_dt = now - timedelta(days=90)
    elif w in ["12m", "365d", "year"]:
        start_dt = now - timedelta(days=365)
    else:
        start_dt = now - timedelta(days=365)

    return start_dt, now


def get_data_quality_metrics(coll, window_str: str = "24h") -> Dict[str, Any]:
    """Evaluates data quality metrics for article publication timestamps."""
    start_dt, end_dt = get_window_cutoff(coll, window_str)
    cursor = coll.find({}, {"published_date": 1, "created_at": 1, "updated_at": 1, "fetched_at": 1}).sort("_id", -1).limit(5000)

    total_docs = 0
    valid_pub_dates = 0
    fallback_dates = 0
    invalid_dates = 0

    for d in cursor:
        total_docs += 1
        dt, field_used = extract_article_timestamp_with_quality(d)
        if field_used == "published_date":
            valid_pub_dates += 1
        elif field_used in ["created_at", "updated_at", "fetched_at"]:
            fallback_dates += 1
        else:
            invalid_dates += 1

    valid_pct = round(((valid_pub_dates + fallback_dates) / max(total_docs, 1)) * 100.0, 1)

    return {
        "total_records_inspected": total_docs,
        "primary_published_dates": valid_pub_dates,
        "fallback_system_dates": fallback_dates,
        "invalid_or_missing_dates": invalid_dates,
        "valid_date_pct": valid_pct,
        "quality_status": "EXCELLENT" if valid_pct >= 90 else ("ACCEPTABLE" if valid_pct >= 70 else "DEGRADED")
    }


def compute_trend_direction(curr_count: int, prev_count: int, min_baseline: int = 3) -> Dict[str, Any]:
    """
    Computes deterministic trend direction (RISING, STABLE, DECLINING, INSUFFICIENT BASELINE).
    """
    diff = curr_count - prev_count
    if prev_count < min_baseline:
        return {
            "direction": "INSUFFICIENT BASELINE",
            "growth_pct": 0.0,
            "abs_change": diff,
            "message": f"Baseline volume ({prev_count}) is below minimum statistical threshold ({min_baseline})."
        }

    pct = (diff / float(prev_count)) * 100.0
    if pct >= 10.0:
        dir_str = "RISING"
    elif pct <= -10.0:
        dir_str = "DECLINING"
    else:
        dir_str = "STABLE"

    return {
        "direction": dir_str,
        "growth_pct": round(pct, 1),
        "abs_change": diff,
        "message": f"{dir_str}: {pct:+.1f}% vs previous comparable period"
    }


def get_volume_analytics(coll, window: str = "24h", bucket: Optional[str] = None) -> dict:
    """Calculates news volume dynamics, bucket time-series, and trend direction."""
    if not bucket:
        bucket = get_recommended_bucket(window)

    start_dt, end_dt = get_window_cutoff(coll, window)
    window_duration = end_dt - start_dt
    prev_start_dt = start_dt - window_duration

    bucket_counts = Counter()
    curr_total = 0
    prev_total = 0

    cursor = coll.find({}, {"published_date": 1, "created_at": 1, "updated_at": 1}).sort("created_at", -1).limit(5000)

    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if not dt:
            continue
        if start_dt <= dt <= end_dt:
            b_key = bucket_timestamp(dt, bucket)
            bucket_counts[b_key] += 1
            curr_total += 1
        elif prev_start_dt <= dt < start_dt:
            prev_total += 1

    sorted_buckets = sorted(bucket_counts.items(), key=lambda x: x[0])
    counts = [v for _, v in sorted_buckets]

    avg_bucket = round(sum(counts) / max(len(counts), 1), 1) if counts else 0.0
    peak_val = max(counts) if counts else 0
    lowest_val = min(counts) if counts else 0
    latest_val = counts[-1] if counts else 0

    trend_eval = compute_trend_direction(curr_total, prev_total, min_baseline=3)
    dq_metrics = get_data_quality_metrics(coll, window)

    return {
        "window": window,
        "bucket": bucket,
        "total_count": curr_total,
        "previous_period_count": prev_total,
        "average_per_bucket": avg_bucket,
        "peak_bucket_count": peak_val,
        "lowest_bucket_count": lowest_val,
        "current_bucket_count": latest_val,
        "trend_direction": trend_eval["direction"],
        "growth_pct": trend_eval["growth_pct"],
        "abs_change": trend_eval["abs_change"],
        "trend_summary": trend_eval["message"],
        "data_quality": dq_metrics,
        "data": [{"timestamp": k, "count": v} for k, v in sorted_buckets]
    }


def get_source_analytics(coll, window: str = "24h", bucket: Optional[str] = None) -> dict:
    """Calculates article activity & volume share by source over time buckets."""
    if not bucket:
        bucket = get_recommended_bucket(window)

    start_dt, end_dt = get_window_cutoff(coll, window)
    source_buckets = defaultdict(Counter)
    source_totals = Counter()
    all_sources = set()

    cursor = coll.find({}, {"source": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            src = extract_source_name(doc)
            all_sources.add(src)
            b_key = bucket_timestamp(dt, bucket)
            source_buckets[b_key][src] += 1
            source_totals[src] += 1

    sorted_times = sorted(source_buckets.keys())
    sources_list = sorted(list(all_sources))
    total_vol = max(sum(source_totals.values()), 1)

    source_shares = [
        {"source": s, "volume": source_totals[s], "share_pct": round((source_totals[s] / total_vol) * 100.0, 1)}
        for s in sources_list
    ]
    source_shares.sort(key=lambda x: x["volume"], reverse=True)

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
        "source_shares": source_shares,
        "data": data_points
    }


def get_category_analytics(coll, window: str = "24h", bucket: Optional[str] = None) -> dict:
    """Calculates article activity by NLP category over time buckets."""
    if not bucket:
        bucket = get_recommended_bucket(window)

    start_dt, end_dt = get_window_cutoff(coll, window)
    cat_buckets = defaultdict(Counter)
    cat_totals = Counter()
    all_categories = set()

    cursor = coll.find({}, {"category": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)
    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            cat = extract_category_label(doc)
            all_categories.add(cat)
            b_key = bucket_timestamp(dt, bucket)
            cat_buckets[b_key][cat] += 1
            cat_totals[cat] += 1

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
        "top_category": cat_totals.most_common(1)[0][0] if cat_totals else "General",
        "data": data_points
    }


def get_sentiment_analytics(coll, window: str = "24h", bucket: Optional[str] = None) -> dict:
    """Calculates model-generated sentiment breakdown over time buckets."""
    if not bucket:
        bucket = get_recommended_bucket(window)

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


def get_spike_analytics(coll, window: str = "24h") -> dict:
    """
    Detects statistical volume spikes (mu + 2*sigma) in overall news, sources, and categories.
    Returns INSUFFICIENT BASELINE if historical sample size < 5 buckets.
    """
    bucket = get_recommended_bucket(window)
    start_dt, end_dt = get_window_cutoff(coll, window)

    bucket_counts = Counter()
    source_buckets = defaultdict(Counter)
    category_buckets = defaultdict(Counter)

    cursor = coll.find({}, {"source": 1, "category": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)

    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            src = extract_source_name(doc)
            cat = extract_category_label(doc)
            b_key = bucket_timestamp(dt, bucket)
            bucket_counts[b_key] += 1
            source_buckets[b_key][src] += 1
            category_buckets[b_key][cat] += 1

    sorted_buckets = sorted(bucket_counts.keys())
    n_buckets = len(sorted_buckets)

    if n_buckets < 5:
        return {
            "overall": {
                "status": "INSUFFICIENT BASELINE",
                "current_volume": bucket_counts[sorted_buckets[-1]] if sorted_buckets else 0,
                "baseline_mean": 0.0,
                "baseline_std": 0.0,
                "spike_threshold": 0.0,
                "message": f"Insufficient historical baseline ({n_buckets} buckets). Minimum 5 required."
            },
            "source_spikes": [],
            "category_spikes": []
        }

    # Historical baseline excluding latest bucket
    hist_counts = [bucket_counts[b] for b in sorted_buckets[:-1]]
    curr_vol = bucket_counts[sorted_buckets[-1]]

    mean_vol = sum(hist_counts) / max(len(hist_counts), 1)
    var_vol = sum((x - mean_vol) ** 2 for x in hist_counts) / max(len(hist_counts), 1)
    std_vol = math.sqrt(var_vol)

    spike_thresh = max(round(mean_vol + 2.0 * std_vol, 1), 5.0)
    is_overall_spike = (curr_vol >= spike_thresh)

    # Source Spikes
    source_spikes = []
    all_sources = set(src for b in sorted_buckets for src in source_buckets[b])

    for src in all_sources:
        s_hist = [source_buckets[b][src] for b in sorted_buckets[:-1]]
        s_curr = source_buckets[sorted_buckets[-1]][src]
        s_mean = sum(s_hist) / max(len(s_hist), 1)
        s_var = sum((x - s_mean) ** 2 for x in s_hist) / max(len(s_hist), 1)
        s_std = math.sqrt(s_var)
        s_thresh = max(round(s_mean + 2.0 * s_std, 1), 3.0)

        if s_curr >= s_thresh and s_curr >= 3:
            s_diff = s_curr - s_mean
            s_pct = round((s_diff / max(s_mean, 1.0)) * 100.0, 1)
            source_spikes.append({
                "source": src,
                "current_volume": s_curr,
                "baseline_mean": round(s_mean, 1),
                "threshold": s_thresh,
                "growth_pct": s_pct,
                "status": "UNUSUAL_ACTIVITY"
            })

    # Category Spikes
    category_spikes = []
    all_categories = set(cat for b in sorted_buckets for cat in category_buckets[b])

    for cat in all_categories:
        c_hist = [category_buckets[b][cat] for b in sorted_buckets[:-1]]
        c_curr = category_buckets[sorted_buckets[-1]][cat]
        c_mean = sum(c_hist) / max(len(c_hist), 1)
        c_var = sum((x - c_mean) ** 2 for x in c_hist) / max(len(c_hist), 1)
        c_std = math.sqrt(c_var)
        c_thresh = max(round(c_mean + 2.0 * c_std, 1), 3.0)

        if c_curr >= c_thresh and c_curr >= 3:
            c_diff = c_curr - c_mean
            c_pct = round((c_diff / max(c_mean, 1.0)) * 100.0, 1)
            category_spikes.append({
                "category": cat,
                "current_volume": c_curr,
                "baseline_mean": round(c_mean, 1),
                "threshold": c_thresh,
                "growth_pct": c_pct,
                "status": "UNUSUAL_ACTIVITY"
            })

    return {
        "overall": {
            "status": "UNUSUAL_ACTIVITY" if is_overall_spike else "NORMAL",
            "current_volume": curr_vol,
            "baseline_mean": round(mean_vol, 1),
            "baseline_std": round(std_vol, 1),
            "spike_threshold": spike_thresh,
            "message": f"Unusual spike detected ({curr_vol} vs threshold {spike_thresh})" if is_overall_spike else "News activity normal"
        },
        "source_spikes": source_spikes,
        "category_spikes": category_spikes
    }


def get_emerging_keywords(coll, window: str = "24h", limit: int = 10) -> dict:
    """Calculates top emerging keywords comparing current period vs baseline period."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    window_duration = end_dt - start_dt
    prev_start_dt = start_dt - window_duration

    kw_recent = Counter()
    kw_baseline = Counter()

    cursor = coll.find({}, {"keywords": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)

    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if not dt:
            continue
        kws = doc.get("keywords", [])
        if not isinstance(kws, list):
            continue

        for kw in kws:
            if isinstance(kw, str) and len(kw) > 3:
                if start_dt <= dt <= end_dt:
                    kw_recent[kw] += 1
                elif prev_start_dt <= dt < start_dt:
                    kw_baseline[kw] += 1

    emerging = []
    for kw, recent_cnt in kw_recent.most_common(50):
        base_cnt = kw_baseline[kw]
        diff = recent_cnt - base_cnt
        pct = ((diff) / max(base_cnt, 1)) * 100.0
        confidence = "HIGH" if (recent_cnt + base_cnt) >= 4 else "LOW CONFIDENCE"

        emerging.append({
            "keyword": kw,
            "recent_mentions": recent_cnt,
            "previous_mentions": base_cnt,
            "growth_pct": round(pct, 1),
            "confidence": confidence
        })

    emerging.sort(key=lambda x: x["growth_pct"], reverse=True)
    return {"keywords": emerging[:limit]}


def get_emerging_entities(coll, window: str = "24h", limit: int = 10) -> dict:
    """Calculates top emerging NER entities with growth percentage."""
    start_dt, end_dt = get_window_cutoff(coll, window)
    window_duration = end_dt - start_dt
    prev_start_dt = start_dt - window_duration

    ent_recent = Counter()
    ent_baseline = Counter()
    ent_types = {}

    cursor = coll.find({}, {"entities": 1, "published_date": 1, "created_at": 1}).sort("created_at", -1).limit(5000)

    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if not dt:
            continue
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
                if start_dt <= dt <= end_dt:
                    ent_recent[e_name] += 1
                elif prev_start_dt <= dt < start_dt:
                    ent_baseline[e_name] += 1

    emerging = []
    for e_name, recent_cnt in ent_recent.most_common(50):
        base_cnt = ent_baseline[e_name]
        diff = recent_cnt - base_cnt
        pct = ((diff) / max(base_cnt, 1)) * 100.0
        confidence = "HIGH" if (recent_cnt + base_cnt) >= 4 else "LOW CONFIDENCE"

        emerging.append({
            "entity": e_name,
            "type": ent_types.get(e_name, "ENTITY"),
            "recent_mentions": recent_cnt,
            "previous_mentions": base_cnt,
            "growth_pct": round(pct, 1),
            "confidence": confidence
        })

    emerging.sort(key=lambda x: x["growth_pct"], reverse=True)
    return {"entities": emerging[:limit]}


def get_cross_source_analytics(coll, window: str = "24h", min_sources: int = 2) -> dict:
    """Identifies developing topics covered across multiple distinct news sources."""
    start_dt, end_dt = get_window_cutoff(coll, window)

    topic_sources = defaultdict(set)
    topic_count = Counter()
    topic_samples = defaultdict(list)

    cursor = coll.find({}, {
        "keywords": 1, "entities": 1, "source": 1, "title": 1, "link": 1, "published_date": 1, "created_at": 1
    }).sort("created_at", -1).limit(3000)

    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if dt and start_dt <= dt <= end_dt:
            src = extract_source_name(doc)
            title = doc.get("title") or "Untitled Story"
            link = doc.get("link", "#")

            kws = doc.get("keywords", []) or []
            if isinstance(kws, list):
                for kw in kws:
                    if isinstance(kw, str) and len(kw) > 3:
                        topic_sources[kw].add(src)
                        topic_count[kw] += 1
                        if len(topic_samples[kw]) < 2:
                            topic_samples[kw].append({"title": title, "source": src, "link": link})

    cross_topics = []
    for topic, sources in topic_sources.items():
        if len(sources) >= min_sources:
            cross_topics.append({
                "topic": topic,
                "sources_count": len(sources),
                "sources": sorted(list(sources)),
                "article_count": topic_count[topic],
                "sample_articles": topic_samples[topic],
                "signal": "Multi-Publisher Topic"
            })

    cross_topics.sort(key=lambda x: (x["sources_count"], x["article_count"]), reverse=True)
    return {"topics": cross_topics[:10]}


def get_trend_explanation(coll, item_type: str = "overall", item_name: str = "all", window: str = "24h") -> dict:
    """
    Generates evidence drill-down lineage ("WHY?") for any spike or volume trend.
    Returns current vs previous counts, responsible sources, top categories, top keywords, and actual articles.
    """
    start_dt, end_dt = get_window_cutoff(coll, window)
    window_duration = end_dt - start_dt
    prev_start_dt = start_dt - window_duration

    source_counter = Counter()
    category_counter = Counter()
    keyword_counter = Counter()
    responsible_articles = []

    cursor = coll.find({}, {
        "title": 1, "link": 1, "source": 1, "category": 1, "keywords": 1, "summary": 1,
        "published_date": 1, "created_at": 1
    }).sort("created_at", -1).limit(3000)

    curr_cnt = 0
    prev_cnt = 0

    for doc in cursor:
        dt = extract_article_timestamp(doc)
        if not dt:
            continue

        src = extract_source_name(doc)
        cat = extract_category_label(doc)
        kws = doc.get("keywords", []) or []

        # Filter by target item if specific
        if item_type == "source" and item_name.lower() not in src.lower():
            continue
        elif item_type == "category" and item_name.lower() not in cat.lower():
            continue

        if start_dt <= dt <= end_dt:
            curr_cnt += 1
            source_counter[src] += 1
            category_counter[cat] += 1
            for k in kws:
                if isinstance(k, str) and len(k) > 3:
                    keyword_counter[k] += 1

            if len(responsible_articles) < 6:
                t_str = doc.get("title", "Untitled Article")
                l_str = doc.get("link", "#")
                s_dict = doc.get("summary")
                s_text = s_dict.get("text", "") if isinstance(s_dict, dict) else str(s_dict or "")

                responsible_articles.append({
                    "title": t_str,
                    "source": src,
                    "category": cat,
                    "published_date": str(dt.strftime("%Y-%m-%d %H:%M UTC")),
                    "summary": s_text[:180] + "..." if len(s_text) > 180 else f"Article report from {src}.",
                    "link": l_str
                })

        elif prev_start_dt <= dt < start_dt:
            prev_cnt += 1

    trend_eval = compute_trend_direction(curr_cnt, prev_cnt, min_baseline=3)

    return {
        "item_type": item_type,
        "item_name": item_name,
        "window": window,
        "current_period_count": curr_cnt,
        "previous_period_count": prev_cnt,
        "growth_pct": trend_eval["growth_pct"],
        "trend_direction": trend_eval["direction"],
        "top_responsible_sources": [{"source": k, "count": v} for k, v in source_counter.most_common(5)],
        "top_responsible_categories": [{"category": k, "count": v} for k, v in category_counter.most_common(5)],
        "top_responsible_keywords": [{"keyword": k, "count": v} for k, v in keyword_counter.most_common(5)],
        "responsible_articles": responsible_articles
    }
