import yake

# =====================================================
# YAKE Keyword Extractor
# =====================================================

kw_extractor = yake.KeywordExtractor(
    lan="en",
    n=1,
    top=10
)

# =====================================================
# Extract Keywords
# =====================================================

def extract_keywords(text):

    if not text:
        return []

    try:

        keywords = kw_extractor.extract_keywords(text)

        return [keyword for keyword, score in keywords]

    except Exception as e:

        print(f"Keyword Error: {e}")

        return []