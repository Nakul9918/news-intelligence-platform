import requests
from bs4 import BeautifulSoup
from datetime import datetime
from collections import Counter


feeds = [
    "india-news",
    "world-news",
    "sports",
    "business",
    "entertainment",
    "lifestyle",
    "technology",
]

start = datetime(2026, 8, 1)
end = datetime(2026, 8, 7, 23, 59, 59)

unique = {}


for category in feeds:

    url = (
        f"https://www.hindustantimes.com/"
        f"feeds/rss/{category}/rssfeed.xml"
    )

    print(f"Checking: {category}")

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    )

    print(f"Status: {response.status_code}")

    soup = BeautifulSoup(
        response.content,
        "xml"
    )

    for item in soup.find_all("item"):

        link_tag = item.find("link")
        date_tag = item.find("pubDate")

        if not link_tag or not date_tag:
            continue

        link = link_tag.text.strip()

        published = datetime.strptime(
            date_tag.text.strip(),
            "%a, %d %b %Y %H:%M:%S %z"
        )

        published_naive = published.replace(
            tzinfo=None
        )

        if start <= published_naive <= end:

            unique.setdefault(
                link,
                published
            )


dates = list(
    unique.values()
)


print()
print("=" * 70)
print("HT UNIQUE AUG 1–7 RESULT")
print("=" * 70)

print(
    "UNIQUE ARTICLES:",
    len(unique)
)

print()
print("BY DATE:")

counter = Counter(
    d.date()
    for d in dates
)

for date, count in sorted(
    counter.items()
):

    print(
        date,
        count
    )

print("=" * 70)