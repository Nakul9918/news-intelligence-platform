from datetime import datetime, timedelta
import time

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from historical_crawlers.common_collector import (
    get_collection,
    store_urls,
    print_summary
)

# =====================================================
# MongoDB Collection
# =====================================================

COLLECTION_NAME = "historical_urls_thehindu"

# =====================================================
# Configuration
# =====================================================

SOURCE_NAME = "The Hindu"

HISTORICAL_YEARS = 3

BASE_ARCHIVE_URL = "https://www.thehindu.com/archive/web/{year}/{month:02d}/{day:02d}/"

WAIT_SECONDS = 5


# =====================================================
# Selenium Driver
# =====================================================

def create_driver():

    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


# =====================================================
# Date Generator
# =====================================================

def generate_dates():

    end_date = datetime.today()

    start_date = end_date - timedelta(days=365 * HISTORICAL_YEARS)

    current = start_date

    while current <= end_date:

        yield current

        current += timedelta(days=1)


# =====================================================
# Extract URLs From One Archive Page
# =====================================================

def extract_urls(driver, archive_url):

    driver.get(archive_url)

    time.sleep(WAIT_SECONDS)

    soup = BeautifulSoup(
        driver.page_source,
        "html.parser"
    )

    urls = []

    seen = set()

    for a in soup.find_all("a", href=True):

        href = a["href"].strip()

        if not href.startswith("https://www.thehindu.com/"):
            continue

        if "/archive/" in href:
            continue

        if "/article" not in href:
            continue

        if not href.endswith(".ece"):
            continue

        if href in seen:
            continue

        seen.add(href)

        urls.append(href)

    return urls
# =====================================================
# Convert URLs to Sitemap-like Objects
# =====================================================

class UrlItem:
    """
    Mimics BeautifulSoup <url> objects so we can reuse
    common_collector.store_urls()
    """

    def __init__(self, link):

        class Tag:
            def __init__(self, text):
                self.text = text

        self.loc = Tag(link)
        self.lastmod = None


# =====================================================
# Store URLs
# =====================================================

def store_article_urls(
    urls,
    collection
):

    url_objects = []

    for url in urls:
        url_objects.append(
            UrlItem(url)
        )

    return store_urls(
        url_objects,
        collection,
        SOURCE_NAME
    )


# =====================================================
# Main
# =====================================================

def main():

    print("=" * 70)
    print(f"{SOURCE_NAME} Historical URL Collection")
    print("=" * 70)

    collection = get_collection(COLLECTION_NAME)

    driver = create_driver()

    total_processed = 0
    total_failed = 0

    dates = list(generate_dates())

    print(f"Total Days : {len(dates)}")

    try:

        for index, current_date in enumerate(dates, start=1):

            archive_url = BASE_ARCHIVE_URL.format(
                year=current_date.year,
                month=current_date.month,
                day=current_date.day
            )

            print("\n" + "=" * 70)
            print(f"[{index}/{len(dates)}]")
            print(current_date.strftime("%Y-%m-%d"))
            print(archive_url)

            try:

                urls = extract_urls(
                    driver,
                    archive_url
                )

                print(f"Articles Found : {len(urls)}")

                if not urls:
                    continue

                processed, failed = store_article_urls(
                    urls,
                    collection
                )

                total_processed += processed
                total_failed += failed

                print(
                    f"Running Total : {total_processed}"
                )

            except Exception as e:

                print(f"Error : {e}")

    finally:

        driver.quit()

    print_summary(
        SOURCE_NAME,
        total_processed,
        total_failed
    )


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":
    main()