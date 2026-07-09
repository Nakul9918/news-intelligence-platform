from newspaper import Article

from nlp.content_cleaner import clean_content
from nlp.ai_cleaner import ai_clean_content

URL = "https://economictimes.indiatimes.com/us/news/quote-of-the-day-by-anna-wintour-those-who-want-things-always-to-stay-the-same-are-not-visionary-vogue-leader-advocates-staying-open-to-change/articleshow/131822180.cms"

SOURCE = "Economic Times"

print("=" * 80)
print("DOWNLOADING ARTICLE...")
print("=" * 80)

news = Article(URL)
news.download()
news.parse()

raw_content = news.text

rule_cleaned = clean_content(
    raw_content,
    SOURCE
)

# IMPORTANT:
# Send RAW article to Gemini.
# Let Gemini clean independently.

ai_cleaned = ai_clean_content(
    raw_content
)

print("\n")
print("=" * 80)
print("RAW ARTICLE")
print("=" * 80)
print(raw_content)

print("\n")
print("=" * 80)
print("RULE CLEANER")
print("=" * 80)
print(rule_cleaned)

print("\n")
print("=" * 80)
print("GEMINI CLEANER")
print("=" * 80)
print(ai_cleaned)

print("\n")
print("=" * 80)
print("STATISTICS")
print("=" * 80)

print("Raw Length         :", len(raw_content))
print("Rule Cleaner       :", len(rule_cleaned))
print("Gemini Cleaner     :", len(ai_cleaned))