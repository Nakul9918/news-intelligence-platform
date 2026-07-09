from transformers import pipeline

# =====================================================
# Load Models Only Once
# =====================================================

# Sentiment Analysis Model

sentiment_model = pipeline(
    "sentiment-analysis"
)