import requests
from bs4 import BeautifulSoup

url = "https://www.thehindu.com/archive/web/2025/07/11/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

for a in soup.find_all("a", href=True):
    href = a["href"]

    if href.startswith("https://www.thehindu.com/") and "/archive/" not in href:
        print(href)