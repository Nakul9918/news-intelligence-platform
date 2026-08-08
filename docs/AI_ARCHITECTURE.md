# Agentic AI + RAG Architecture Documentation

## Overview
The News Intelligence Platform integrates a deterministic **Agentic AI & Retrieval-Augmented Generation (RAG)** layer designed for news understanding, trend analysis, cross-source activity tracking, and source-grounded question answering.

The AI system is strictly **READ-ONLY** and does not alter database state, publish Kafka messages, or execute unconstrained code.

---

## System Architecture Diagram

```
                 USER QUESTION
                       │
                       ▼
             QUERY UNDERSTANDING
            (Intent Classification)
                       │
                       ▼
                 QUERY ROUTER
         (Deterministic Tool Selection)
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
     RETRIEVAL     ANALYTICS     TEMPORAL
    (BM25/KNN/     (MongoDB     (Phase 14
     Hybrid)      Aggregations)  Engine)
         └─────────────┼─────────────┘
                       │
                       ▼
              RAG CONTEXT BUILDER
         (Deduplication & Formatting)
                       │
                       ▼
             GROUNDED GENERATION
         (Gemini 2.5 Flash / Fallback)
                       │
                       ▼
             VERIFIED CITATIONS
       (Article IDs, Titles, Sources, URLs)
```

---

## Core Components

### 1. Centralized AI Configuration (`ai/config.py`)
- `AI_PROVIDER`: `"gemini"` (default)
- `AI_MODEL`: `"gemini-2.5-flash"`
- `GEMINI_API_KEY`: Loaded safely from environment `.env` (Never hardcoded).
- `AI_TEMPERATURE`: `0.2`
- `AI_MAX_CONTEXT_ARTICLES`: `8`

### 2. Query Understanding & Routing (`ai/query_router.py`)
Classifies user questions into intent categories:
- `ARTICLE_SEARCH`: Keyword/topic queries.
- `SUMMARY`: Requests for overview.
- `COMPARISON`: Multi-publisher comparative queries.
- `TREND_ANALYSIS`: Volume surges, breaking news, or emerging terms.
- `SENTIMENT_ANALYSIS`: Positive/Negative/Neutral breakdown over time.
- `SOURCE_ANALYSIS`: Publisher distribution.
- `ENTITY_ANALYSIS`: NER person/org/location queries.
- `CROSS_SOURCE_QUERY`: Multi-source event topics.
- `GENERAL_NEWS_QUERY`: Top stories today.

### 3. Retrieval & Tool Execution (`ai/rag_engine.py`)
- **Elasticsearch Hybrid Search**: Combines BM25 text relevance score and 384-dimensional dense vector cosine similarity score (`all-MiniLM-L6-v2`).
- **Phase 14 Temporal Analytics**: Volume trends, source/category timelines, statistical spike detection, emerging keywords/entities (% growth), and cross-source correlation.

### 4. RAG Context Builder & Citation Tracking (`ai/context_builder.py`)
- Deduplicates retrieved documents by `article_id`.
- Formats structured evidence blocks.
- Constructs verified citations (`article_id`, `title`, `source`, `published_date`, `url`).

### 5. Grounded LLM Generation & Hallucination Guardrails (`ai/llm_client.py`)
- Uses `gemini-2.5-flash` model via Google GenAI SDK.
- Enforces strict grounding rules: Answers MUST be derived strictly from supplied evidence.
- **Insufficient Evidence Guardrail**: If 0 evidence articles or analytics match the query, returns `"Insufficient evidence was found in the indexed news data."` instead of hallucinating facts.
- **Extractive Grounded RAG Fallback**: If Gemini API key is unconfigured or temporarily unreachable, uses an extractive rule-based generator ensuring 100% offline functionality.

---

## API Endpoint Reference

### `POST /api/ai/ask`
**Request:**
```json
{
  "question": "What are the major news topics trending today?"
}
```

**Response:**
```json
{
  "question": "What are the major news topics trending today?",
  "intent": "TREND_ANALYSIS",
  "answer": "Based on temporal news analytics...\n1. [Economic Times] RBI macro guidelines...",
  "sources": [
    {
      "article_id": "e2e_test_article_...",
      "title": "India news Live Updates",
      "source": "Economic Times",
      "published_date": "2026-08-08T10:00:00Z",
      "url": "https://..."
    }
  ],
  "retrieval": {
    "method": "hybrid",
    "results_count": 8
  },
  "tools_executed": ["get_emerging_keywords", "get_cross_source_analytics", "search_hybrid"],
  "status": "SUCCESS",
  "provider": "gemini (gemini-2.5-flash)"
}
```

---

## Security & Observability Rules
1. **Zero Hardcoded Secrets**: Credentials managed via environment variables.
2. **Read-Only Operation**: The AI engine cannot alter database state, delete articles, or publish Kafka events.
3. **No Unsafe Execution**: No dynamic `eval()` or shell execution.
4. **Tool Observability**: All executed tools and retrieval methods are explicitly returned in response metadata.
