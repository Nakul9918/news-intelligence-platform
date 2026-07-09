from nlp.sentiment import analyze_sentiment

text = """
India defeated Australia in a thrilling match.
The fans celebrated the magnificent victory.
"""

sentiment, score = analyze_sentiment(text)

print("Sentiment :", sentiment)
print("Score :", score)