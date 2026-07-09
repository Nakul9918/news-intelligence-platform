import yake

# =====================================================
# YAKE Keyword Extractor
# =====================================================

keyword_extractor = yake.KeywordExtractor(
    lan="en",
    n=2,
    dedupLim=0.9,
    top=15
)


# =====================================================
# Extract Keywords
# =====================================================

def extract_keywords(content):

    if not content:
        return []

    try:

        results = keyword_extractor.extract_keywords(content)

        keywords = []

        for keyword, score in results:

            keyword = keyword.strip()

            if len(keyword) < 3:
                continue

            duplicate = False

            for existing in keywords:

                if keyword.lower() in existing.lower():

                    duplicate = True
                    break

            if not duplicate:
                keywords.append(keyword)

            if len(keywords) == 10:
                break

        return keywords

    except Exception as e:

        print("Keyword Error :", e)

        return []