# Entity Intelligence Specification

## 1. Business & Product Purpose
The **Entity Intelligence** workspace transforms entity tracking into a company-grade entity investigation module. It allows users to search any person, organization, location, or event across live and historical news articles, providing deep insights into mention volume, 4-newspaper source distribution, model sentiment, mention timelines, co-occurring entity relationships, and supporting article evidence.

---

## 2. Core Questions Answered
1. **"WHO is being mentioned?"** (People entities)
2. **"WHICH ORGANIZATIONS are being mentioned?"** (Company & Institution entities)
3. **"WHERE are events happening?"** (Location & Country entities)
4. **"HOW OFTEN are they mentioned?"** (Total mention count & article coverage volume)
5. **"WHEN did coverage increase?"** (Mention Timeline & Trend Direction)
6. **"WHICH SOURCES mention them?"** (4-Newspaper Source Coverage: *Economic Times*, *The Hindu*, *Indian Express*, *Hindustan Times*)
7. **"WHAT TOPICS & KEYWORDS are associated with them?"** (Co-occurring keywords with one-click Topic Intelligence search)
8. **"WHAT SENTIMENT surrounds their coverage?"** (Model-generated sentiment breakdown: Positive %, Neutral %, Negative %)
9. **"WHICH OTHER ENTITIES appear with them?"** (Co-occurrence network: Related People, Organizations, Locations)
10. **"WHICH ARTICLES provide the evidence?"** (Full article cards & evidence lineage drawer)

---

## 3. Architecture & Data Flow

```
Entity Query ("Narendra Modi" / "RBI" / "Mumbai" / "Donald Trump" / "OpenAI")
    ↓
FastAPI Backend (/api/entities/investigate)
    ├── Entity Normalizer & Regex Matcher
    ├── Mention & Volume Aggregator (Mentions, Articles, 4-Source ratio, Trend Direction)
    ├── Mention Timeline Engine (Bucketed time-series mention counts)
    ├── Source Coverage Engine (ET, The Hindu, IE, HT volume & share)
    ├── Model Sentiment Engine (Positive %, Neutral %, Negative %)
    ├── Co-occurrence Relationship Engine (Related People, Orgs, Locations)
    └── Supporting Article Evidence Provider (Title, Published Date, Summary, Link)
    ↓
Streamlit Dashboard Workspace 08 (Entity Investigation Workspace)
```

---

## 4. API Endpoint Contract

`GET /api/entities/investigate?entity={entity_name}&type={all|PER|ORG|LOC}&window={window}`

**Response Schema**:
```json
{
  "entity": "Narendra Modi",
  "type": "PER",
  "total_mentions": 1284,
  "total_articles": 426,
  "coverage_ratio": "4 / 4 major sources",
  "trend_direction": "RISING",
  "dominant_sentiment": "Neutral",
  "first_seen": "2026-08-01",
  "last_seen": "2026-08-09",
  "sentiment_breakdown": {
    "Positive": 18.0,
    "Neutral": 61.0,
    "Negative": 21.0
  },
  "source_coverage": {
    "Economic Times": {"articles": 142, "mentions": 410, "share_pct": 33.3},
    "The Hindu": {"articles": 96, "mentions": 280, "share_pct": 22.5},
    "Indian Express": {"articles": 87, "mentions": 260, "share_pct": 20.4},
    "Hindustan Times": {"articles": 101, "mentions": 334, "share_pct": 23.8}
  },
  "related_entities": {
    "people": [{"entity": "Amit Shah", "count": 42}],
    "organizations": [{"entity": "BJP", "count": 98}, {"entity": "RBI", "count": 34}],
    "locations": [{"entity": "Delhi", "count": 120}, {"entity": "Mumbai", "count": 88}]
  },
  "associated_keywords": [{"keyword": "Elections", "count": 56}],
  "timeline": [{"date": "2026-08-01", "count": 42}],
  "sample_articles": []
}
```

---

## 5. UI/UX Workflow & Components

1. **Hero Entity Search Bar**: Large text input supporting any Person, Organization, Location, or Event with quick recommendation chips (`Narendra Modi`, `RBI`, `Mumbai`, `Donald Trump`, `OpenAI`, `Delhi`, `Virat Kohli`).
2. **Compact Entity Type Filters**: `[ ALL ENTITIES ]`, `[ PEOPLE (PER) ]`, `[ ORGANIZATIONS (ORG) ]`, `[ LOCATIONS (LOC) ]`.
3. **Entity Profile Overview**: Mentions count, Total Articles, Publisher Coverage ratio, Trend Direction badge (`RISING`, `STABLE`, `DECLINING`), First Seen date, Last Seen date.
4. **Entity Mention Activity Timeline**: Bucketed Plotly time-series chart showing mention frequency over time.
5. **4-Newspaper Source Coverage & Category Breakdown**: Side-by-side comparison across *Economic Times*, *The Hindu*, *Indian Express*, and *Hindustan Times*.
6. **Model Sentiment Intelligence**: Sentiment breakdown (Positive %, Neutral %, Negative %) labeled as `MODEL-GENERATED SENTIMENT`.
7. **Co-occurring Entity Relationships**: Grouped breakdown for People (`PER`), Organizations (`ORG`), and Locations (`LOC`).
8. **Associated Topics & Keywords**: Clickable keywords with instant connection to Topic & Keyword Intelligence.
9. **Statistical Mention Spike Alert**: Anomaly alert if entity mentions surge above baseline ($\mu + 2\sigma$).
10. **Article Evidence Drawer**: Detailed article cards with `[VIEW INTELLIGENCE]` modal for stored summary, keywords, and original links.
