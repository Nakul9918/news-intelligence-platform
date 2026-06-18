import streamlit as st
from pymongo import MongoClient
import pandas as pd

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles"]

st.title("News Intelligence Dashboard")

# Total Articles
total_articles = collection.count_documents({})

st.metric(
    "Total Articles",
    total_articles
)

# Latest 10 Articles
articles = list(
    collection.find(
        {},
        {
            "title": 1,
            "source": 1,
            "category": 1,
            "sentiment": 1
        }
    ).limit(10)
)

df = pd.DataFrame(articles)

st.subheader("Latest News")

st.dataframe(df)
