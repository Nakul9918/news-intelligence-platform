from nlp.summarizer import generate_summary

text = """
Artificial Intelligence is transforming industries worldwide.
Machine Learning is being adopted by healthcare,
finance, education and cybersecurity.
Many companies are investing billions into AI research.
Data Engineers are responsible for building scalable pipelines.
Natural Language Processing is one of the fastest growing AI fields.
"""

summary = generate_summary(text)

print(summary)