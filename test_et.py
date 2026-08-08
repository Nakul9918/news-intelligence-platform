import requests
from bs4 import BeautifulSoup

url = input("Article URL: ")

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(url, headers=headers).text

print("Downloaded:", len(html))

soup = BeautifulSoup(html, "html.parser")

selectors = [
    ".artText p",
    ".article_wrap p",
    ".Normal",
    "article p",
    ".story-content p",
    ".article-content p",
    "p"
]

for selector in selectors:

    elements = soup.select(selector)

    print("\n", "=" * 60)
    print(selector)
    print("Found:", len(elements))

    if elements:

        print(elements[0].get_text(strip=True)[:300])