import os

from dotenv import load_dotenv
from google import genai

# =====================================================
# Load Environment Variables
# =====================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# =====================================================
# Gemini Client
# =====================================================

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash"

# =====================================================
# AI Content Cleaner
# =====================================================

def ai_clean_content(text):

    if not text:
        return ""

    prompt = f"""
You are an expert News Content Cleaner.

Your job is ONLY to clean the article.

DO NOT summarize.
DO NOT rewrite.
DO NOT change sentence order.
DO NOT improve grammar.
DO NOT shorten the article.

Remove ONLY:

• Advertisements
• Sponsored content
• Subscribe prompts
• Login prompts
• Website headers
• Website footers
• Navigation menus
• Read More
• Continue Reading
• Related Stories
• Share buttons
• WhatsApp
• Facebook
• Twitter
• Telegram
• View All
• Live Events
• Breaking News banners
• Trending sections
• Promotional text
• Duplicate headings
• Duplicate paragraphs
• Quote of the Day headings
• "Who is ..."
• "What does ..."
• "How ..."

If the article begins with website junk,
remove everything until the actual news begins.

Keep:

• Facts
• Quotes
• Numbers
• Dates
• Locations
• Names
• Complete paragraphs
• Original wording

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

        print("Gemini Cleaner Error:", e)

        return text