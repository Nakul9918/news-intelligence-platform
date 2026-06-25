from transformers import pipeline

# ==========================================
# Load Models Only Once
# ==========================================

summarizer_model = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

sentiment_model = pipeline(
    "sentiment-analysis"
)