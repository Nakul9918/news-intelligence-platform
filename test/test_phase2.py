from nlp.summarizer import (
    is_valid_input,
    preprocess_text,
    tokenize_text,
)

article = """
Prime Minister Narendra Modi visited Mumbai today
to inaugurate a new infrastructure project.
Officials from the Maharashtra Government
also attended the ceremony.
"""

print(is_valid_input(article))

clean = preprocess_text(article)

print(clean)

tokens = tokenize_text(clean)

print(tokens["input_ids"].shape)

# =====================================================
# Generate Summary
# =====================================================

def generate_summary(text: str) -> str:
    """
    Generate a summary from cleaned article text.

    Parameters
    ----------
    text : str
        Cleaned article text.

    Returns
    -------
    str
        Generated summary.
    """

    if not is_valid_input(text):
        return ""

    try:

        # Preprocess
        text = preprocess_text(text)

        # Tokenize
        inputs = tokenize_text(text)

        # Generate summary
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=MAX_SUMMARY_LENGTH,
            min_length=MIN_SUMMARY_LENGTH,
            num_beams=NUM_BEAMS,
            length_penalty=LENGTH_PENALTY,
            early_stopping=EARLY_STOPPING,
        )

        # Decode summary
        summary = tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        return summary.strip()

    except Exception as exc:

        logger.exception(
            "Summary generation failed: %s",
            exc,
        )

        return ""

