"""
=====================================================
News Category Classifier
Version : 3.0
=====================================================

Uses HuggingFace Zero-Shot Classification

Model:
    MoritzLaurer/deberta-v3-base-zeroshot-v1.1

Features
--------
✓ Loads model once
✓ Zero-shot classification
✓ Confidence score
✓ Top-3 predictions
✓ Production ready
✓ Exception handling
"""

from transformers import pipeline

# =====================================================
# Configuration
# =====================================================

MODEL_NAME = "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33"
CATEGORIES = [

    "Politics",

    "Business",

    "Technology",

    "Sports",

    "Health",

    "Entertainment",

    "Education",

    "Crime",

    "Environment",

    "Science",

    "World",

    "General"

]

MAX_TEXT_LENGTH = 1500

TOP_K = 3

# =====================================================
# Load Model
# =====================================================

try:

    classifier = pipeline(

        task="zero-shot-classification",

        model=MODEL_NAME,

        device=-1          # CPU

    )

    print(f"✓ Category Model Loaded : {MODEL_NAME}")

except Exception as e:

    classifier = None

    print("✗ Failed to load category model")

    print(e)


# =====================================================
# Prepare Text
# =====================================================

def prepare_text(title="", content=""):

    text = f"{title}. {content}"

    text = text.strip()

    if len(text) > MAX_TEXT_LENGTH:

        text = text[:MAX_TEXT_LENGTH]

    return text


# =====================================================
# Classify Category
# =====================================================

def classify_category(title="", content=""):

    """
    Returns

    {
        "category":"Technology",

        "score":0.98,

        "predictions":[...]

    }
    """

    if classifier is None:

        return {

            "category": "General",

            "score": 0.0,

            "predictions": []

        }

    text = prepare_text(title, content)

    if not text:
        return {
            "category": "General",
            "score": 0.0,
            "predictions": []
        }

    try:

        # Get tokenizer from the zero-shot pipeline
        tokenizer = classifier.tokenizer

        # Tokenize and truncate to model's maximum input size
        inputs = tokenizer(
            text,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        # Convert truncated tokens back to text
        truncated_text = tokenizer.decode(
            inputs["input_ids"][0],
            skip_special_tokens=True
        )

        result = classifier(
            sequences=truncated_text,
            candidate_labels=CATEGORIES,
            multi_label=False
        )

        predictions = []

        for label, score in zip(
            result["labels"][:TOP_K],
            result["scores"][:TOP_K]
        ):
            predictions.append(
                {
                    "label": label,
                    "score": round(float(score), 4)
                }
            )

        if not predictions:
            return {
                "category": "General",
                "score": 0.0,
                "predictions": []
            }

        return {
            "category": predictions[0]["label"],
            "score": predictions[0]["score"],
            "predictions": predictions
        }

    except Exception as e:

        print("Category Classification Error")
        print(e)

        return {
            "category": "General",
            "score": 0.0,
            "predictions": []
        }


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    title = "India launches new AI chip"

    content = """
    India announced a new semiconductor manufacturing
    policy to boost artificial intelligence and
    chip production.
    """

    print(classify_category(title, content))