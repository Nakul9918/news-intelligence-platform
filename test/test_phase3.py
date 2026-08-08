from nlp.summarizer import generate_summary

article = """
Prime Minister Narendra Modi visited Mumbai today to inaugurate a new
infrastructure project worth ₹15,000 crore.

The ceremony was attended by senior Maharashtra Government officials,
industry leaders and local representatives.

The project aims to improve transportation, reduce congestion
and create thousands of employment opportunities.
"""

summary = generate_summary(article)

print("\nSummary:\n")
print(summary)