import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.thehindu.com/archive/web/2025/07/11/"

options = Options()

# Make Selenium look more like a normal browser
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Hide Selenium automation flag
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

driver.get(URL)

print("Please wait 15 seconds...")
time.sleep(15)

print("Title :", driver.title)
print("URL   :", driver.current_url)

html = driver.page_source

with open("thehindu.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Saved HTML.")

soup = BeautifulSoup(html, "html.parser")

links = set()

for a in soup.find_all("a", href=True):
    href = a["href"]

    if href.startswith("https://www.thehindu.com/") and "/archive/" not in href:
        links.add(href)

print(f"\nFound {len(links)} links\n")

for link in sorted(links)[:50]:
    print(link)

input("\nPress Enter to close browser...")

driver.quit()