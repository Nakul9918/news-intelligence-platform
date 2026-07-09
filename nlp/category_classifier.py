"""
=====================================================
News Category Classifier
Version : 1.0
=====================================================
"""

CATEGORY_KEYWORDS = {

    "Sports": [
        "cricket", "football", "fifa", "ipl",
        "olympics", "tennis", "badminton",
        "hockey", "kabaddi", "match",
        "player", "coach", "tournament"
    ],

    "Business": [
        "stock", "stocks", "share", "shares",
        "ipo", "market", "economy",
        "finance", "investment",
        "bank", "company", "startup"
    ],

    "Politics": [
        "government", "minister",
        "parliament", "election",
        "politics", "bjp",
        "congress", "policy"
    ],

    "Technology": [
        "artificial intelligence",
        "ai",
        "machine learning",
        "software",
        "hardware",
        "google",
        "microsoft",
        "apple",
        "openai",
        "chatgpt",
        "cybersecurity"
    ],

    "Health": [
        "doctor",
        "hospital",
        "medicine",
        "covid",
        "virus",
        "vaccine",
        "patient",
        "health"
    ],

    "Entertainment": [
        "movie",
        "film",
        "actor",
        "actress",
        "bollywood",
        "hollywood",
        "music",
        "song",
        "cinema"
    ],

    "Education": [
        "school",
        "college",
        "neet",
        "jee",
        "exam",
        "student",
        "education",
        "university"
    ],

    "Crime": [
        "police",
        "crime",
        "arrest",
        "murder",
        "fraud",
        "court",
        "judge"
    ],

    "Environment": [
        "climate",
        "environment",
        "rain",
        "weather",
        "flood",
        "forest"
    ]

}


def classify_category(text):

    text = text.lower()

    scores = {}

    for category, words in CATEGORY_KEYWORDS.items():

        score = 0

        for word in words:

            if word in text:

                score += 1

        scores[category] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:

        return "General"

    return best