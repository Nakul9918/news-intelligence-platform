# Search + AI Intelligence Specification

## 1. Business & Product Purpose
The **Search + AI Intelligence** workspace serves as the central investigation engine of the News Intelligence Platform. It combines BM25 keyword relevance, dense vector KNN semantic search, hybrid retrieval, multi-faceted filtering, canonical article inspection, and grounded RAG AI synthesis with verified source citations.

---

## 2. Core Questions Answered
1. **"How can I search millions of indexed news signals?"** (Natural language, keyword, source, category, date, and entity search with Hybrid/BM25/Vector options)
2. **"What news articles match my filters?"** (Paginated search results with relevance scores, retrieval badges, and key entities)
3. **"Can I inspect the full evidence for an article?"** (Article Inspector drawer displaying stored summary, content snippet, entities, keywords, and original URL)
4. **"What is the AI analysis for my question?"** (Grounded answer synthesized by LLM using retrieved news evidence)
5. **"Which exact articles support the AI answer?"** (Verified Citation Cards `[1]`, `[2]` linking back to stored canonical articles)
6. **"What happens if no evidence exists?"** (Strict `INSUFFICIENT EVIDENCE` guardrail preventing hallucinations)

---

## 3. Architecture & Data Flow

```
Real-time News Stream / MongoDB / Elasticsearch
    ↓
Hybrid Retrieval & Intent Router (BM25 + Vector KNN + Query Router)
    ├── Search Filters (Date, Source, Category, Sentiment, Sort order)
    ├── Canonical Article Inspector (Summary, Content, Entities, Keywords)
    ├── RAG Context Builder (Top 8 verified articles + Temporal & Event context)
    ├── Grounded LLM Synthesizer (Gemini integration with evidence grounding)
    └── Citation Verifier (Validates article_id & canonical URL)
    ↓
FastAPI Backend (/api/news/nl-search & /api/ai/ask)
    ↓
Streamlit Dashboard Workspace 11 (Search & AI Investigation Center)
```

---

## 4. API Endpoints Contract

1. `POST /api/news/nl-search`
   - Body: `{"query": "search query"}`
   - Returns parsed intent, tools executed, and matched article search results.

2. `POST /api/ai/ask`
   - Body: `{"question": "natural language question"}`
   - Returns grounded answer text, verified citation cards list, retrieval metadata, intent, and evidence status.

---

## 5. UI/UX Workflow & Components

1. **Header & Live Pipeline Status**: Telemetry indicator (`● LIVE PIPELINE — STREAMING`).
2. **Primary Search Bar & Retrieval Selector**: Large search input + Selector (`Hybrid`, `BM25`, `Vector`).
3. **Filter Toolbar**: Date, Source, Category, Sentiment, and Sort order controls.
4. **Prompt Library (10 Quick Prompts)**: One-click search/RAG buttons (`Top News Today`, `Compare 4 Sources`, `What Changed Today?`, `Summarize News`, `Cross-Source Stories`, `Developing Stories`, `Economy`, `Politics`, `AI & Tech`, `Crime`).
5. **Search Results & Relevance Cards**: Relevance scores (`Relevance: 0.92`), retrieval badges, keywords/entities, pagination, and `[OPEN ARTICLE]` / `[ASK AI ABOUT THIS]` buttons.
6. **Article Inspector Drawer (`[OPEN ARTICLE]`)**: Canonical summary, content snippet, keywords, entities, and original source URL link.
7. **Grounded AI News Analyst (RAG Engine)**:
   - **Analysis Trace**: System execution trace (`QUERY UNDERSTANDING ✓`, `RETRIEVAL MODE ✓`, `RAG CONTEXT (8 Docs)`).
   - **Grounded Answer Panel**: Synthesized response text.
   - **Verified Citations Cards**: Clickable cards `[1]`, `[2]` linked to original source URLs.
   - **Insufficient Evidence Guardrail**: `INSUFFICIENT EVIDENCE` display for unknown/non-indexed facts.
8. **Conversational Follow-Up**: Input for follow-up questions (`"Why?"`, `"Show more sources"`).
