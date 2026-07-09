from nlp.gemini_client import client, MODEL

# =====================================================
# AI Content Cleaner
# =====================================================

def ai_clean_content(text):

    if not text:
        return ""

    prompt = f"""
You are an expert News Article Cleaner.

Your ONLY responsibility is to clean the article.

IMPORTANT RULES

DO NOT:
- Summarize
- Rewrite
- Improve grammar
- Change wording
- Change sentence order
- Shorten the article
- Add your own text
- Remove factual information

Remove ONLY website boilerplate such as:

• Advertisements
• Sponsored content
• Website headers
• Website footers
• Navigation menus
• Read More
• Continue Reading
• Related Stories
• Recommended Articles
• Share buttons
• Login prompts
• Register prompts
• Subscription banners
• Cookie banners
• Newsletter prompts
• Download App banners
• Promotional messages
• Duplicate headings
• Duplicate paragraphs

Remove promotional sentences like:

- Follow us on WhatsApp
- Join our WhatsApp Channel
- Follow us on Telegram
- Join our Telegram Channel
- Share on Facebook
- Follow us on Twitter
- Follow us on Instagram
- Download our App
- Subscribe Now

IMPORTANT

If WhatsApp, Telegram, Facebook, Twitter, Instagram,
or any company/person/place is mentioned as part of the
actual news article,

DO NOT REMOVE IT.

If you are unsure whether a sentence belongs to the
actual news article,

KEEP IT.

Always preserve:

- Facts
- Dates
- Numbers
- Quotes
- Names
- Places
- Organizations
- Statistics
- Complete paragraphs

Return ONLY the cleaned article.

Article:

{text}
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return text

    except Exception as e:

        print(f"Gemini Cleaner Error: {e}")

        return text