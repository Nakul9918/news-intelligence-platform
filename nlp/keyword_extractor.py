"""
=====================================================
Keyword Extractor
Version : 4.0
=====================================================

Extracts keywords using KeyBERT.

Features
--------
✓ KeyBERT + SentenceTransformers
✓ Loads model only once
✓ Exception handling
✓ Configurable parameters
✓ Returns keyword with confidence score
✓ Production ready
"""

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# =====================================================
# Configuration
# =====================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_N = 15
DEFAULT_MIN_NGRAM = 1
DEFAULT_MAX_NGRAM = 3
DEFAULT_NR_CANDIDATES = 30

MIN_WORDS = 30
MIN_SCORE = 0.35

# =====================================================
# Load Embedding Model (Only Once)
# =====================================================

try:
    embedding_model = SentenceTransformer(MODEL_NAME)
    kw_model = KeyBERT(embedding_model)

    print(f"✓ KeyBERT Model Loaded : {MODEL_NAME}")

except Exception as e:

    kw_model = None

    print(f"✗ Failed to load KeyBERT model")
    print(e)


# =====================================================
# Extract Keywords
# =====================================================

def extract_keywords(
    text,
    top_n=DEFAULT_TOP_N,
    min_ngram=DEFAULT_MIN_NGRAM,
    max_ngram=DEFAULT_MAX_NGRAM,
):
    """
    Extract keywords from article.

    Parameters
    ----------
    text : str

    Returns
    -------
    list

    Example

    [
        {
            "text":"Artificial Intelligence",
            "score":0.8123
        }
    ]
    """

    if kw_model is None:
        return []

    if not text:
        return []

    text = text.strip()

    if not text:
        return []

    # Ignore very small articles
    if len(text.split()) < MIN_WORDS:
        return []

    try:

        keywords = kw_model.extract_keywords(

            text,

            keyphrase_ngram_range=(
                min_ngram,
                max_ngram
            ),

            stop_words="english",

            top_n=top_n,

            use_maxsum=True,

            nr_candidates=DEFAULT_NR_CANDIDATES

        )

        results = []

        for keyword, score in keywords:

            score = float(score)

            if score < MIN_SCORE:
                continue

            results.append({

                "text": keyword,

                "score": round(score, 4)

            })

        return results

    except Exception as e:

        print(f"Keyword Extraction Error : {e}")

        return []