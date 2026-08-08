"""
Query Understanding & Deterministic Intent Router
"""

import re
from typing import Dict, List, Any

KNOWN_SOURCES = {
    "economic times": "Economic Times",
    "et": "Economic Times",
    "the hindu": "The Hindu",
    "hindu": "The Hindu",
    "indian express": "Indian Express",
    "hindustan times": "Hindustan Times",
    "ht": "Hindustan Times"
}

KNOWN_CATEGORIES = {
    "business": "Business",
    "technology": "Technology",
    "tech": "Technology",
    "politics": "Politics",
    "sports": "Sports",
    "health": "Health",
    "entertainment": "Entertainment",
    "world": "World",
    "crime": "Crime",
    "environment": "Environment"
}

def analyze_query(query: str) -> Dict[str, Any]:
    q_lower = query.lower().strip()
    
    # 1. Extract Filters
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

    # 2. Determine Intent & Tools
    tools = []
    if any(term in q_lower for term in ["cross-source", "multiple sources", "different sources", "covered by multiple", "reported by"]):
        intent = "CROSS_SOURCE_QUERY"
        tools = ["get_cross_source_analytics", "search_hybrid"]
    elif any(term in q_lower for term in ["compare", "versus", "vs", "difference"]):
        intent = "COMPARISON"
        tools = ["search_hybrid", "get_source_analytics", "get_cross_source_analytics"]
    elif any(term in q_lower for term in ["trending", "trend", "emerging", "popular"]):
        intent = "TREND_ANALYSIS"
        tools = ["get_emerging_keywords", "get_emerging_entities", "get_volume_analytics"]
    elif any(term in q_lower for term in ["spike", "unusual", "surge", "anomaly"]):
        intent = "TREND_ANALYSIS"
        tools = ["get_spike_analytics", "get_volume_analytics"]
    elif any(term in q_lower for term in ["sentiment", "feeling", "mood", "positive news", "negative news"]):
        intent = "SENTIMENT_ANALYSIS"
        tools = ["get_sentiment_analytics", "search_hybrid"]
    elif any(term in q_lower for term in ["entity", "entities", "people", "persons", "organizations"]):
        intent = "ENTITY_ANALYSIS"
        tools = ["get_emerging_entities", "search_hybrid"]
    elif any(term in q_lower for term in ["source", "publisher", "newspaper"]):
        intent = "SOURCE_ANALYSIS"
        tools = ["get_source_analytics", "search_hybrid"]
    elif any(term in q_lower for term in ["summarize", "summary", "overview"]):
        intent = "SUMMARY"
        tools = ["search_hybrid", "get_volume_analytics"]
    elif any(term in q_lower for term in ["today", "latest", "breaking", "biggest stories"]):
        intent = "GENERAL_NEWS_QUERY"
        tools = ["search_hybrid", "get_latest_articles"]
    else:
        intent = "ARTICLE_SEARCH"
        tools = ["search_hybrid"]

    return {
        "query": query,
        "intent": intent,
        "tools": tools,
        "filters": {
            "source": source_filter,
            "category": category_filter,
            "sentiment": sentiment_filter,
            "time_window": time_window
        }
    }
