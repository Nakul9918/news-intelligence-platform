"""
=====================================================
Keyword Extractor
Version : 5.0
=====================================================

Extracts keywords using KeyBERT.

Features
--------
✓ KeyBERT + SentenceTransformers
✓ Loads model only once
✓ Faster execution
✓ Debug logging
✓ Exception handling
✓ Returns keyword with confidence score
✓ Production ready
"""

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# =====================================================
# Configuration
# =====================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_N = 8
DEFAULT_MIN_NGRAM = 1
DEFAULT_MAX_NGRAM = 3
DEFAULT_NR_CANDIDATES = 10

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

    print("✗ Failed to load KeyBERT model")
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

    Returns
    -------
    List[dict]
    """

    if kw_model is None:
        print("✗ KeyBERT model not available")
        return []

    if not text:
        print("✗ Empty text")
        return []

    text = text.strip()

    if not text:
        print("✗ Empty text after strip")
        return []

    # Ignore very small articles
    if len(text.split()) < MIN_WORDS:
        print("✗ Article too short for keyword extraction")
        return []

    # Limit article size for faster processing
    text = " ".join(text.split()[:500])

    try:

        print("=" * 70)
        print("STEP 1 - Starting KeyBERT")
        print("=" * 70)

        keywords = kw_model.extract_keywords(

            text,

            keyphrase_ngram_range=(
                min_ngram,
                max_ngram
            ),

            stop_words="english",

            top_n=top_n,

            # Faster than MaxSum
            use_maxsum=False,

            nr_candidates=DEFAULT_NR_CANDIDATES,

        )

        print("=" * 70)
        print("STEP 2 - KeyBERT Finished")
        print("=" * 70)

        results = []

        for keyword, score in keywords:

            score = float(score)

            if score < MIN_SCORE:
                continue

            results.append(
                {
                    "text": keyword,
                    "score": round(score, 4),
                }
            )

        print(f"✓ Keywords Extracted : {len(results)}")

        return results

    except Exception as e:

        print("=" * 70)
        print("✗ Keyword Extraction Error")
        print("=" * 70)
        print(type(e).__name__)
        print(e)

        return []