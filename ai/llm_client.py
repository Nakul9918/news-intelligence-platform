"""
Source-Grounded LLM Answer Generator with Extractive Fallback
"""

import os
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

    # Subject Term Relevance Guardrail:
    # If the user query specifies subject nouns not present in any retrieved article title/summary, reject as insufficient evidence.
    ignored_words = {"what", "where", "when", "which", "about", "according", "indian", "express", "hindu", "times", "happened", "year", "news", "show", "tell", "give"}
    q_words = [w.strip("?,!.") for w in question.lower().split() if len(w) > 3 and w.strip("?,!.") not in ignored_words]
    
    if q_words and citations:
        combined_text = " ".join([c.get("title", "").lower() + " " + c.get("summary", "").lower() for c in citations])
        has_match = any(w in combined_text for w in q_words)
        if not has_match and intent in ["ARTICLE_SEARCH", "GENERAL_NEWS_QUERY", "SUMMARY"]:
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
{context_str if context_str else "No direct article text retrieved."}
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
            lines.append(f"{i}. **[{c['source']}]** {c['title']} ({c['published_date'][:10]}) — Category: {c['category']} | Sentiment: {c['sentiment']}")

    answer_text = "\n".join(lines) if lines else "Insufficient evidence was found in the indexed news data."
    
    return {
        "answer": answer_text,
        "status": "SUCCESS" if lines else "INSUFFICIENT_EVIDENCE",
        "provider": "extractive_grounded_rag"
    }
