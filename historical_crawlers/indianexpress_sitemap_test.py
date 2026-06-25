import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SITEMAP_URL = "https://indianexpress.com/sitemap.xml"

try:

    response = requests.get(
        SITEMAP_URL,
        headers=HEADERS,
        timeout=30
    )

    print("Status:", response.status_code)

    print("\nFirst 3000 Characters\n")
    print(response.text[:3000])

    soup = BeautifulSoup(
        response.text,
        "xml"
    )

    print("\nRoot Tag :", soup.find().name)

    sitemap_count = len(
        soup.find_all("sitemap")
    )

    url_count = len(
        soup.find_all("url")
    )

    print("Sitemap Count :", sitemap_count)
    print("URL Count :", url_count)

    print("\nFirst 10 Sitemap URLs\n")

    for sitemap in soup.find_all("sitemap")[:10]:

        print(
            sitemap.loc.text
        )

except Exception as e:

    print(e)