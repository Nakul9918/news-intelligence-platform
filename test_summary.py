from nlp.summarizer import generate_summary

text = """
Artificial intelligence is transforming industries worldwide.
Companies are investing billions in AI research.
Governments are creating regulations to ensure AI is used responsibly.
Experts believe AI will change healthcare, education,
finance and manufacturing over the next decade.
"""

summary = generate_summary(text)

print("\nSummary:\n")
print(summary)