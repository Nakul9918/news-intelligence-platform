#from newspaper import Article

#url = "https://www.bbc.com/news/articles/cgjx5qw75v8o?at_medium=RSS&at_campaign=rss"

#article = Article(url)

#article.download()
#article.parse()

#print("TITLE:")
#print(article.title)

#print("\nCONTENT:")
#print(article.text[:3000])

from pymongo import MongoClient
from newspaper import Article

client = MongoClient("mongodb://localhost:27017/")
db = client["news_db"]
collection = db["articles"]

articles = collection.find({"link": {"$exists": True}})

for news in articles:

    url = news["link"]

    try:
        article = Article(url)

        article.download()
        article.parse()

        content = article.text

        collection.update_one(
            {"_id": news["_id"]},
            {
                "$set": {
                    "content": content
                }
            }
        )

        print("Updated:", news["title"])

    except Exception as e:
        print("Failed:", url)
        print(e)
        
collection.update_one(
    {"_id": news["_id"]},
    {
        "$set": {
            "content": content,
            "processing_status": "content_extracted"
        }
    }
)