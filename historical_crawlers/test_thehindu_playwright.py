from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://www.thehindu.com/archive/web/2025/07/11/"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ]
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        viewport={"width": 1366, "height": 768},
        locale="en-US"
    )

    page = context.new_page()

    # Block unnecessary resources
    page.route(
        "**/*",
        lambda route: (
            route.abort()
            if route.request.resource_type in ["image", "font", "media", "stylesheet"]
            else route.continue_()
        )
    )

    print("Opening page...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.wait_for_timeout(8000)

    print("Title :", page.title())
    print("URL   :", page.url)

    html = page.content()

    with open("thehindu.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\nHTML saved as thehindu.html")

    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if href.startswith("https://www.thehindu.com/"):

            if "/archive/" in href:
                continue

            if href.endswith(".jpg"):
                continue

            if href.endswith(".png"):
                continue

            if "/topic/" in href:
                continue

            if "/videos/" in href:
                continue

            if "/podcast/" in href:
                continue

            if "/gallery/" in href:
                continue

            links.add(href)

    print(f"\nFound {len(links)} unique links\n")

    for link in sorted(links):
        print(link)

    browser.close()