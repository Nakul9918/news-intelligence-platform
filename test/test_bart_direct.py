import torch
from transformers import BartTokenizer, BartForConditionalGeneration

MODEL = "facebook/bart-large-cnn"

print("1. Loading tokenizer...")

tokenizer = BartTokenizer.from_pretrained(MODEL)

print("2. Tokenizer loaded.")

print("3. Loading model...")

model = BartForConditionalGeneration.from_pretrained(MODEL)

print("4. Model loaded.")

text = """
Apple introduced a new AI-powered MacBook.
The company announced several AI features and improved battery life.
"""

inputs = tokenizer(
    text,
    return_tensors="pt",
    max_length=1024,
    truncation=True,
)

print("5. Generating summary...")

with torch.no_grad():

    ids = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=50,
        min_length=20,
        num_beams=4,
    )

summary = tokenizer.decode(
    ids[0],
    skip_special_tokens=True,
)

print("6. Summary:")
print(summary)