"""
Source-Grounded LLM Answer Generator with Extractive Fallback
"""

import os
import re
from typing import List, Dict, Any, Optional
from ai.config import GEMINI_API_KEY, AI_MODEL, AI_TEMPERATURE

def generate_grounded_answer(
    question: str,
    intent: str,
    context_str: str,
    citations: List[Dict[str, Any]],
    analytics_summary: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a source-grounded answer using Gemini API if configured,
    or fallback extractive grounded RAG generator.
    """
    # 1. Grounding check — Insufficient Evidence handling
    if not citations and not analytics_summary:
        return {
            "answer": "Insufficient evidence was found in the indexed news data to answer this question.",
            "status": "INSUFFICIENT_EVIDENCE",
            "provider": "grounding_guardrail"
        }

    # 2. Prompt Injection Defense: Sanitize untrusted context text to prevent system overrides
    sanitized_context = context_str or "No direct article text retrieved."
    injection_patterns = [
        r"(?i)ignore\s+previous\s+instructions",
        r"(?i)disregard\s+all\s+prior",
        r"(?i)you\s+are\s+now",
        r"(?i)system\s*prompt:",
        r"(?i)override\s+safety"
    ]
    for pat in injection_patterns:
        sanitized_context = re.sub(pat, "[FILTERED INJECTION CONTENT]", sanitized_context)

    # 3. Subject Term Relevance & Hallucination Guardrail
    ignored_words = {
        "what", "where", "when", "which", "who", "whom", "whose", "why", "how",
        "about", "according", "indian", "express", "hindu", "times", "happened",
        "year", "news", "show", "tell", "give", "latest", "recent", "stories",
        "today", "yesterday", "week", "month", "compare", "summary", "article"
    }
    q_words = [w.strip("?,!.\"')(").lower() for w in question.split() if len(w.strip("?,!.\"')(")) > 3 and w.strip("?,!.\"')(").lower() not in ignored_words]
    
    if q_words and citations:
        combined_text = " ".join([
            (c.get("title") or "").lower() + " " +
            (c.get("summary") or "").lower() + " " +
            (c.get("source") or "").lower() + " " +
            (c.get("category") or "").lower()
            for c in citations
        ])
        has_match = any(w in combined_text for w in q_words)
        if not has_match and intent in ["ARTICLE_SEARCH", "GENERAL_NEWS_QUERY", "SUMMARY", "DATE_RANGE_QUERY"]:
            return {
                "answer": "Insufficient evidence was found in the indexed news data to answer this question.",
                "status": "INSUFFICIENT_EVIDENCE",
                "provider": "grounding_guardrail"
            }

    prompt = f"""
You are an expert News Intelligence Assistant.
Answer the user's question using ONLY the retrieved news evidence and analytics data provided below.

==================================================
CRITICAL GROUNDING RULES:
1. Use ONLY facts present in the SUPPLIED EVIDENCE.
2. Do NOT invent dates, article titles, sources, numbers, or facts.
3. Do NOT use outside knowledge not supported by the evidence.
4. If the evidence is insufficient to answer the question, state: "Insufficient evidence was found in the indexed news data."
5. Be concise, objective, and professional.

USER QUESTION:
{question}

INTENT: {intent}

{f"ANALYTICS SUMMARY:\n{analytics_summary}\n" if analytics_summary else ""}
RETRIEVED NEWS EVIDENCE:
{sanitized_context}
"""

    # 2. Try Gemini API if API Key is configured
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=AI_MODEL,
                contents=prompt
            )
            if response and response.text:
                return {
                    "answer": response.text.strip(),
                    "status": "SUCCESS",
                    "provider": f"gemini ({AI_MODEL})"
                }
        except Exception as e:
            # Fall through to Extractive Grounded Generator on API error
            pass

    # 3. Fallback Extractive Grounded RAG Generator
    lines = []
    if intent in ["TREND_ANALYSIS", "SOURCE_ANALYSIS", "SENTIMENT_ANALYSIS", "CROSS_SOURCE_QUERY"] and analytics_summary:
        lines.append(f"Based on temporal news analytics for '{question}':")
        lines.append(analytics_summary)

    if citations:
        lines.append(f"\nKey news developments from indexed articles ({len(citations)} sources retrieved):")
        for i, c in enumerate(citations[:5], 1):
            src_lbl = c.get('source') or 'Unknown'
            title_lbl = c.get('title') or 'Untitled'
            pub_lbl = str(c.get('published_date') or 'N/A')[:10]
            cat_lbl = c.get('category') or 'General'
            sent_lbl = c.get('sentiment') or 'Neutral'
            lines.append(f"{i}. **[{src_lbl}]** {title_lbl} ({pub_lbl}) — Category: {cat_lbl} | Sentiment: {sent_lbl}")

    answer_text = "\n".join(lines) if lines else "Insufficient evidence was found in the indexed news data."
    
    return {
        "answer": answer_text,
        "status": "SUCCESS" if lines else "INSUFFICIENT_EVIDENCE",
        "provider": "extractive_grounded_rag"
    }
