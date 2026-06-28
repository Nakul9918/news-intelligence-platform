from transformers import pipeline

# =====================================================
# Load Sentiment Model
# =====================================================

sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# =====================================================
# Analyze Sentiment
# =====================================================

def analyze_sentiment(text):

    if not text:
        return "NEUTRAL", 0.0

    try:

        result = sentiment_model(text[:512])[0]

        sentiment = result["label"]

        score = float(result["score"])

        return sentiment, score

    except Exception as e:

        print("Sentiment Error:", e)

        return "UNKNOWN", 0.0