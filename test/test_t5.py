from transformers import pipeline

print("Creating T5 pipeline...")

pipe = pipeline(
    "text2text-generation",
    model="google/flan-t5-small",
)

print("Pipeline created.")

print(
    pipe(
        "Summarize: Apple introduced a new AI-powered MacBook with better battery life.",
        max_new_tokens=30,
    )
)
