"""
RAG Context Builder & Citation Formatter
"""

from typing import List, Dict, Any

def build_rag_context(articles: List[Dict[str, Any]], max_articles: int = 8) -> tuple[str, List[Dict[str, Any]]]:
    """
    Deduplicates articles, constructs structured LLM evidence context,
    and builds verified source citations.
    """
    seen_ids = set()
    deduped_articles = []

    for art in articles:
        aid = art.get("article_id") or str(art.get("_id"))
        if aid not in seen_ids:
            seen_ids.add(aid)
            deduped_articles.append(art)

    selected_articles = deduped_articles[:max_articles]
    
    context_lines = []
    citations = []

    for idx, art in enumerate(selected_articles, start=1):
        aid = art.get("article_id") or str(art.get("_id"))
        title = art.get("title") or "Untitled Article"
        src = art.get("source")
        src_name = src.get("name") if isinstance(src, dict) else str(src or "Unknown")
        pub_date = art.get("published_date") or art.get("created_at") or "N/A"
        summary = art.get("summary") or art.get("description") or ""
        content = art.get("clean_content") or art.get("content") or ""
        url = art.get("link") or "#"

        cat = art.get("category")
        cat_label = cat.get("label") if isinstance(cat, dict) else str(cat or "General")

        sent = art.get("sentiment")
        sent_label = sent.get("label") if isinstance(sent, dict) else str(sent or "Neutral")

        # Include content snippet up to 500 chars per article
        snippet = summary if len(summary) > 50 else content[:500]

        context_lines.append(
            f"--- ARTICLE [{idx}] ---\n"
            f"Title: {title}\n"
            f"Source: {src_name}\n"
            f"Published: {pub_date}\n"
            f"Category: {cat_label} | Sentiment: {sent_label}\n"
            f"Content: {snippet}\n"
            f"URL: {url}\n"
        )

        citations.append({
            "article_id": aid,
            "title": title,
            "source": src_name,
            "published_date": str(pub_date),
            "category": cat_label,
            "sentiment": sent_label,
            "url": url
        })

    context_str = "\n".join(context_lines)
    return context_str, citations
