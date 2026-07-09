from nlp.models import sentiment_model

# =====================================================
# Sentiment Analysis
# =====================================================

def analyze_sentiment(text):

    if not text:
        return {
            "label": "UNKNOWN",
            "score": 0.0
        }

    try:

        MAX_LENGTH = 512

        text = text[:1500]

        result = sentiment_model(
        text,
         truncation=True,
        max_length=MAX_LENGTH
    )[0]

        return {

            "label": result["label"],

            "score": round(
                result["score"],
                4
            )

        }

    except Exception as e:

        print(f"Sentiment Error: {e}")

        return {

            "label": "UNKNOWN",

            "score": 0.0

        }