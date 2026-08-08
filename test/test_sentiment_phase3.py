from nlp.sentiment import predict_sentiment

texts = [

    "India achieved record economic growth this year with strong exports and new investments.",

    "Heavy floods caused severe damage and thousands of people were displaced.",

    "The meeting was held in New Delhi on Monday to discuss policy changes.",

]

for text in texts:

    result = predict_sentiment(text)

    print("-" * 50)
    print(text)
    print(result)