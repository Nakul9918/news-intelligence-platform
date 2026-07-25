from nlp.models import summarizer_model

# =====================================================
# News Summarization
# =====================================================

def generate_summary(text):

    if not text or not text.strip():
        return ""

    try:

        # Prevent extremely large character inputs
        text = text[:4000]

        # Get tokenizer from the summarization pipeline
        tokenizer = summarizer_model.tokenizer

        # Tokenize and truncate to the model's maximum input size
        inputs = tokenizer(
            text,
            truncation=True,
            max_length=1024,
            return_tensors="pt"
        )

        # Convert truncated tokens back to text
        truncated_text = tokenizer.decode(
            inputs["input_ids"][0],
            skip_special_tokens=True
        )

        # Calculate approximate input length after truncation
        input_length = inputs["input_ids"].shape[1]

        # Dynamic summary lengths
        max_length = min(150, max(50, input_length // 2))
        min_length = min(40, max(20, input_length // 4))

        result = summarizer_model(
            truncated_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )[0]

        return result["summary_text"]

    except Exception as e:

        print(f"Summary Error : {e}")

        return ""