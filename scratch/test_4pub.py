from pymongo import MongoClient
import re

client = MongoClient("mongodb://127.0.0.1:27017")
db = client["news_db"]
coll = db["realtime_articles"]

TARGET_SOURCES = ["Economic Times", "The Hindu", "Indian Express", "Hindustan Times"]

NOISE_TERMS = [
    "horoscope", "zodiac", "numerology", "astrology", "tarot", "bitchat", 
    "suneel darshan", "sobhita", "bollywood", "celebrity", "gossip", "ipl",
    "movie review", "film review", "actor", "actress", "dolby"
]
noise_pattern = re.compile("|".join(NOISE_TERMS), re.IGNORECASE)

def clean_url_headline(url: str) -> str:
    if not url:
        return "Untitled Article"
    # Extract slug from URL
    slug = url.rstrip("/").split("/")[-1]
    if "articleshow" in slug or ".cms" in slug or ".html" in slug:
        parts = url.rstrip("/").split("/")
        slug = parts[-2] if len(parts) >= 2 else parts[-1]
    slug = re.sub(r"articleshow.*|\.cms|\.html|\d+$", "", slug)
    headline = slug.replace("-", " ").replace("_", " ").strip()
    if len(headline) < 5:
        return "National News Update"
    return headline.title()

topic = "India economy"
topic_words = [w.lower() for w in topic.split() if len(w) > 2]

print("=== TESTING 4-NEWSPAPER COMPARISON FOR TOPIC:", topic, "===")

for pub in TARGET_SOURCES:
    docs = list(coll.find({
        "$or": [
            {"source": {"$regex": re.escape(pub), "$options": "i"}},
            {"source.name": {"$regex": re.escape(pub), "$options": "i"}},
            {"link": {"$regex": re.escape(pub.replace(" ", "").lower()), "$options": "i"}}
        ]
    }).limit(100))
    
    valid_articles = []
    for d in docs:
        link = d.get("link", "")
        title = d.get("title") or clean_url_headline(link)
        
        # Check noise
        if noise_pattern.search(title) or noise_pattern.search(link):
            continue
            
        valid_articles.append(title)
        if len(valid_articles) >= 5:
            break
            
    print(f"\n{pub} ({len(valid_articles)} articles):")
    for title in valid_articles:
        print("  -", title)
