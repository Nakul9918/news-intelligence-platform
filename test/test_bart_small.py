from transformers import pipeline

print("Creating pipeline...")

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
)

print("Pipeline created.")

text = """
Apple introduced a new AI-powered MacBook.
Tim Cook announced several AI features.
The laptop offers better battery life and improved performance.
"""

print(
    summarizer(
        text,
        max_length=50,
        min_length=20,
        do_sample=False,
    )
)