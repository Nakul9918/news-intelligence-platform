import requests
from bs4 import BeautifulSoup

url = "https://www.ndtv.com/sitemap.xml?yyyy=2025&mm=6&sitename=ndtv-news&category="

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

print(response.text[:500])
