"""
=====================================================
NLP Models
=====================================================

Loads all NLP models once at application startup.

Available Models
----------------
- Sentiment Analysis
- Text Summarization
- Named Entity Recognition (NER)
"""

import spacy
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# =====================================================
# Sentiment Analysis Model
# =====================================================

SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

sentiment_model = pipeline(
    "sentiment-analysis",
    model=SENTIMENT_MODEL,
    device=-1
)

# =====================================================
# Summarization Model
# =====================================================

SUMMARIZER_MODEL = "facebook/bart-large-cnn"

summarizer_model = pipeline(
    "summarization",
    model=SUMMARIZER_MODEL,
    device=-1
)

# =====================================================
# Named Entity Recognition (spaCy)
# =====================================================

NER_MODEL = "en_core_web_sm"

ner_model = spacy.load(NER_MODEL)

# =====================================================
# Embedding Model
# =====================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(EMBEDDING_MODEL)