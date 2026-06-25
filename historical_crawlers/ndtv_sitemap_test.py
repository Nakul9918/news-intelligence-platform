import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.ndtv.com/",
    "Connection": "keep-alive"
}

URL = "https://www.ndtv.com/sitemap.xml?yyyy=2026&mm=6&sitename=ndtv-news&category="

session = requests.Session()

response = session.get(
    URL,
    headers=HEADERS,
    timeout=30,
    allow_redirects=True
)

print("=" * 70)
print("Status Code :", response.status_code)
print("=" * 70)

print("\nFinal URL")
print(response.url)

print("\nContent Type")
print(response.headers.get("Content-Type"))

print("\nServer")
print(response.headers.get("Server"))

print("\nFirst 3000 Characters\n")
print(response.text[:3000])