# News Intelligence Platform — Step-by-Step Demonstration Guide

This guide provides an exact, step-by-step demonstration sequence for presenting the News Intelligence Platform.

---

## 🚀 Step 1: One-Command System Launch

1. Open **PowerShell**.
2. Navigate to the project directory:
   ```powershell
   cd d:\project\news-intelligence-platform\project
   ```
3. Run the automated master startup script:
   ```powershell
   .\start_project.ps1
   ```
4. Verify all 5 background application daemons report **RUNNING**:
   - `Automatic Ingestion Service` (PID active)
   - `Realtime Kafka Consumer` (PID active)
   - `Pipeline Orchestrator` (PID active)
   - `FastAPI Backend API` (`http://localhost:8000`)
   - `Streamlit Dashboard` (`http://localhost:8501`)

---

## 📊 Step 2: Open Real-Time Dashboard

1. Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```
2. Point out the **System Status Bar** showing green active indicators for API (`http://localhost:8000`), MongoDB (`localhost:27017`), and Elasticsearch (`localhost:9200`).
3. View the metric summary cards: **Total Articles Ingested** (10,446+), **Today's Articles**, **Enriched & Completed %, and Pending Count.

---

## 🔴 Step 3: Live Incoming News Feed

1. Click on the **🔴 Live News Feed** tab.
2. Demonstrate live auto-updating feed showing new incoming articles with Time, Source, Category, Sentiment, and Headline columns.

---

## 🤖 Step 4: AI Assistant & Grounded RAG

1. Click on the **🤖 AI Assistant & RAG** tab.
2. Click the quick button: `"What are the major news topics trending today?"`
3. Click **Ask AI Assistant**.
4. Highlight:
   - **Grounded Answer**: Concise summary derived strictly from indexed news data.
   - **Evidence & Source Citations**: Verified source links, article titles, published dates, and sentiment labels.
   - **Agent Observability**: Displays Query Intent (`TREND_ANALYSIS`), Retrieval Method (`hybrid`), Executed Tools list, and Provider.
5. Demonstrate **Hallucination Guardrail**:
   - Type a question with no news evidence (e.g., *"What happened on Mars in 1842?"*).
   - Show that the AI responds: `"Insufficient evidence was found in the indexed news data to answer this question."` without fabricating facts.

---

## ⏳ Step 5: Temporal Intelligence & Trend Analytics

1. Click on the **⏳ Temporal Intelligence** tab.
2. Point out the **Spike Detection Banner** showing current article volume vs. baseline activity.
3. Select **Time Window**: `24h` and **Bucket Size**: `1h`.
4. Show the live time-series charts:
   - **News Volume over Time**
   - **Source Activity over Time**
   - **Category Volume over Time**
   - **Sentiment Timeline**
5. Highlight **Emerging Keywords (% Growth)**, **Emerging Entities (% Growth)**, and **Cross-Source Activity Signals**.

---

## 📊 Step 6: Distribution Analytics & Search

1. Click on **📊 Source & Category Distribution** tab to view bar charts for publisher distribution, category breakdown, sentiment distribution, and top NER entities.
2. Click on **🔍 Hybrid Search** tab:
   - Type query `"economy growth in India"`.
   - Select Search Mode: **Hybrid**.
   - Show combined BM25 text relevance and 384-dimensional dense vector KNN search results with similarity scores.

---

## 🛑 Step 7: Graceful System Shutdown

1. Return to PowerShell.
2. Run the graceful shutdown script:
   ```powershell
   .\stop_project.ps1
   ```
3. Confirm all background daemons stop cleanly and PID files are removed.
