"""
=====================================================
Query Understanding & Deterministic Intent Router
=====================================================
Parses natural language queries with automatic spelling auto-correction:
- Typo & Spelling Auto-Correction (difflib fuzzy matching)
- Source & Category extraction
- Sentiment filters
- Natural Language Date & Time Windows (e.g. "August 1 to August 7", "yesterday", "this month")
- Specialized Intents: TOP_10, DEVELOPING_STORIES, STORY_TIMELINE, NEWSPAPER_COMPARISON, etc.
"""

import re
import difflib
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta

KNOWN_SOURCES = {
    "economic times": "Economic Times",
    "et": "Economic Times",
    "the hindu": "The Hindu",
    "hindu": "The Hindu",
    "indian express": "Indian Express",
    "express": "Indian Express",
    "hindustan times": "Hindustan Times",
    "ht": "Hindustan Times"
}

KNOWN_CATEGORIES = {
    "business": "Business",
    "technology": "Technology",
    "tech": "Technology",
    "politics": "Politics",
    "political": "Politics",
    "sports": "Sports",
    "sport": "Sports",
    "health": "Health",
    "entertainment": "Entertainment",
    "world": "World",
    "crime": "Crime",
    "criminal": "Crime",
    "environment": "Environment",
    "india": "India",
    "science": "Science",
    "finance": "Finance",
    "education": "Education"
}

MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}

SPELLING_VOCABULARY = [
    "politics", "political", "business", "technology", "tech", "sports", "sport",
    "entertainment", "crime", "criminal", "health", "science", "finance", "education",
    "world", "india", "environment", "economic", "times", "hindu", "express", "hindustan",
    "market", "inflation", "elections", "cricket", "olympics", "government", "police",
    "court", "accused", "investigation", "narendra", "modi", "rbi", "reliance", "tata",
    "today", "yesterday", "month", "week", "developing", "timeline", "compare", "spikes"
]


def auto_correct_spelling(query: str) -> tuple[str, bool]:
    """
    Fuzzy auto-corrects typos in user search query.
    Returns (corrected_query, was_corrected_flag).
    """
    tokens = query.strip().split()
    corrected_tokens = []
    was_corrected = False

    for token in tokens:
        clean_tok = token.lower().strip(".,!?\"'()")
        if len(clean_tok) <= 3 or clean_tok.isdigit():
            corrected_tokens.append(token)
            continue
        
        matches = difflib.get_close_matches(clean_tok, SPELLING_VOCABULARY, n=1, cutoff=0.7)
        if matches and matches[0] != clean_tok:
            # Preserve original casing if title/upper
            new_tok = matches[0].capitalize() if token.istitle() else matches[0]
            corrected_tokens.append(new_tok)
            was_corrected = True
        else:
            corrected_tokens.append(token)

    corrected_str = " ".join(corrected_tokens)
    return corrected_str, was_corrected


def parse_date_range_from_text(q_lower: str) -> tuple[Optional[str], Optional[str]]:
    """Extract start_date and end_date strings (YYYY-MM-DD) from natural language text."""
    now = datetime.now(timezone.utc)
    
    if "yesterday" in q_lower:
        yest = now - timedelta(days=1)
        y_str = yest.strftime("%Y-%m-%d")
        return y_str, y_str
    elif "today" in q_lower:
        t_str = now.strftime("%Y-%m-%d")
        return t_str, t_str
    elif "this month" in q_lower:
        start_m = now.replace(day=1).strftime("%Y-%m-%d")
        return start_m, now.strftime("%Y-%m-%d")
    elif "last week" in q_lower or "past week" in q_lower or "last 7 days" in q_lower:
        start_w = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        return start_w, now.strftime("%Y-%m-%d")
    elif "last 30 days" in q_lower or "past month" in q_lower:
        start_m = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        return start_m, now.strftime("%Y-%m-%d")

    # Match patterns like "august 1 to august 7" or "aug 1 - aug 7" or "august 1 to 7"
    m_range = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})\s*(?:to|-|until)\s*(?:(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+)?(\d{1,2})', q_lower)
    if m_range:
        m1_str, d1_str, m2_str, d2_str = m_range.groups()
        m1 = MONTH_MAP.get(m1_str.lower(), now.month)
        m2 = MONTH_MAP.get(m2_str.lower(), m1) if m2_str else m1
        d1 = int(d1_str)
        d2 = int(d2_str)
        yr = now.year
        try:
            dt1 = datetime(yr, m1, d1)
            dt2 = datetime(yr, m2, d2)
            return dt1.strftime("%Y-%m-%d"), dt2.strftime("%Y-%m-%d")
        except Exception:
            pass

    return None, None


def analyze_query(query: str) -> Dict[str, Any]:
    # 1. Apply Automatic Spelling Correction
    corrected_query, was_corrected = auto_correct_spelling(query)
    q_lower = corrected_query.lower().strip()
    
    # 2. Extract Filters
    source_filter = None
    for k, v in KNOWN_SOURCES.items():
        if k in q_lower:
            source_filter = v
            break

    category_filter = None
    for k, v in KNOWN_CATEGORIES.items():
        if k in q_lower:
            category_filter = v
            break

    sentiment_filter = None
    if "positive" in q_lower:
        sentiment_filter = "Positive"
    elif "negative" in q_lower:
        sentiment_filter = "Negative"
    elif "neutral" in q_lower:
        sentiment_filter = "Neutral"

    time_window = "24h"
    if "1 hour" in q_lower or "last hour" in q_lower:
        time_window = "1h"
    elif "6 hour" in q_lower:
        time_window = "6h"
    elif "7 day" in q_lower or "week" in q_lower:
        time_window = "7d"
    elif "30 day" in q_lower or "month" in q_lower:
        time_window = "30d"

    start_date, end_date = parse_date_range_from_text(q_lower)

    # 3. Determine Intent & Tools
    tools = []
    if any(term in q_lower for term in ["top 10", "top ten", "top 10 news", "top stories"]):
        intent = "TOP_10_NEWS"
        tools = ["get_top10_ranked_news", "search_hybrid"]
    elif any(term in q_lower for term in ["developing", "pending", "ongoing", "developing stories"]):
        intent = "DEVELOPING_STORIES"
        tools = ["get_developing_stories", "search_hybrid"]
    elif any(term in q_lower for term in ["timeline", "what happened next", "story evolution", "after this", "follow-up"]):
        intent = "STORY_TIMELINE"
        tools = ["get_story_timeline", "search_hybrid"]
    elif any(term in q_lower for term in ["compare", "versus", "vs", "difference", "four newspapers", "all newspapers"]):
        intent = "NEWSPAPER_COMPARISON"
        tools = ["get_four_newspaper_comparison", "get_cross_source_analytics", "search_hybrid"]
    elif any(term in q_lower for term in ["cross-source", "multiple sources", "different sources", "covered by multiple"]):
        intent = "CROSS_SOURCE_QUERY"
        tools = ["get_cross_source_analytics", "search_hybrid"]
    elif any(term in q_lower for term in ["trending", "trend", "emerging", "popular"]):
        intent = "TREND_ANALYSIS"
        tools = ["get_emerging_keywords", "get_emerging_entities", "get_volume_analytics"]
    elif any(term in q_lower for term in ["spike", "unusual", "surge", "anomaly"]):
        intent = "TREND_ANALYSIS"
        tools = ["get_spike_analytics", "get_volume_analytics"]
    elif any(term in q_lower for term in ["sentiment", "feeling", "mood", "positive news", "negative news"]):
        intent = "SENTIMENT_ANALYSIS"
        tools = ["get_sentiment_analytics", "search_hybrid"]
    elif any(term in q_lower for term in ["entity", "person", "company", "place", "organization", "leader"]):
        intent = "ENTITY_DEEPDIVE"
        tools = ["get_keyword_entity_intelligence", "search_hybrid"]
    elif start_date or end_date:
        intent = "DATE_RANGE_QUERY"
        tools = ["get_date_explorer_analytics", "search_hybrid"]
    else:
        intent = "ARTICLE_SEARCH"
        tools = ["search_hybrid"]

    return {
        "original_query": query,
        "query": corrected_query,
        "was_auto_corrected": was_corrected,
        "intent": intent,
        "tools": tools,
        "filters": {
            "source": source_filter,
            "category": category_filter,
            "sentiment": sentiment_filter,
            "time_window": time_window,
            "start_date": start_date,
            "end_date": end_date
        }
    }
