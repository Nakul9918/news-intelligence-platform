import json

from nlp.gemini_client import client, MODEL

# =====================================================
# Gemini Processor
# =====================================================

def process_article(content):

    if not content:

        return {
            "clean_content": "",
            "summary": "",
            "category": "General"
        }

    prompt = f"""
You are an expert News Intelligence AI.

Perform ALL of the following tasks.

==================================================

TASK 1 - CLEAN ARTICLE

Remove ONLY:

- Advertisements
- Sponsored content
- Website headers
- Website footers
- Navigation menus
- Subscribe prompts
- Login prompts
- Read More
- Continue Reading
- Related Stories
- Duplicate headings
- Duplicate paragraphs

DO NOT:

- Rewrite the article
- Improve grammar
- Change sentence order
- Remove facts
- Remove names
- Remove dates
- Remove numbers

==================================================

TASK 2 - SUMMARY

Generate a concise summary.

Rules:

- Maximum 120 words
- Preserve facts
- Preserve names
- Preserve dates
- Preserve numbers
- Preserve locations

==================================================

TASK 3 - CATEGORY

Choose ONLY ONE category.

Categories:

Politics
Business
Technology
Sports
Health
Entertainment
Science
World
Education
Crime
Environment
General

==================================================

Return ONLY valid JSON.

Example:

{{
    "clean_content": "...",
    "summary": "...",
    "category": "Business"
}}

Article:

{content}
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        response_text = response.text.strip()

        # -----------------------------------------
        # Remove Markdown Code Block
        # -----------------------------------------

        if response_text.startswith("```"):

            response_text = (
                response_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        # -----------------------------------------
        # Convert JSON
        # -----------------------------------------

        result = json.loads(response_text)

        return {

            "clean_content": result.get(
                "clean_content",
                content
            ),

            "summary": result.get(
                "summary",
                ""
            ),

            "category": result.get(
                "category",
                "General"
            )

        }

    except Exception as e:

        print(f"Gemini Processor Error: {e}")

        return {

            "clean_content": content,

            "summary": "",

            "category": "General"

        }