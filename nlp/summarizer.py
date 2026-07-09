from nlp.gemini_client import client, MODEL

# =====================================================
# Generate Summary
# =====================================================

def generate_summary(text):

    if not text:
        return ""

    prompt = f"""
You are an expert news summarizer.

Summarize the following news article.

Rules:

- Keep important facts.
- Keep names.
- Keep dates.
- Keep numbers.
- Keep locations.
- Do NOT add information.
- Maximum 5 sentences.
- Return only the summary.

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

        return ""

    except Exception as e:

        print(f"Summary Error: {e}")

        return ""