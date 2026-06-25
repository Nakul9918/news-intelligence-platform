import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

url = "https://www.thehindu.com/sitemap/googlenews/all/all.xml"

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)

if response.status_code != 200:
    print("Failed to fetch sitemap")
    exit()

soup = BeautifulSoup(
    response.text,
    "xml"
)

urls = soup.find_all("url")

print("Total URLs:", len(urls))
print()

for item in urls[:10]:
    try:
        print(item.loc.text)
    except:
        pass