"""
=====================================================
Sentence Embeddings
=====================================================

Generates semantic embeddings for cleaned news articles.
"""

from nlp.models import embedding_model


# =====================================================
# Generate Embedding
# =====================================================

def generate_embedding(text):
    """
    Generate embedding vector for a text.

    Parameters
    ----------
    text : str

    Returns
    -------
    list
        Embedding vector.
    """

    if not text or not text.strip():
        return []

    try:

        embedding = embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    except Exception as e:

        print(f"Embedding Error: {e}")

        return []