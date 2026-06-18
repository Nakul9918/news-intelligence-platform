import requests
from bs4 import BeautifulSoup

url = "https://economictimes.indiatimes.com/etstatic/sitemaps/et/news/2025-June-1.xml"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "xml")

urls = soup.find_all("url")

print("Total URLs:", len(urls))

for item in urls[:5]:
    print(item.loc.text)
