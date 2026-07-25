
"""
extractor.py

Article Extraction Module

Extraction Order:
1. newspaper3k
2. trafilatura
3. BeautifulSoup

Version 2
"""

from newspaper import Article
import trafilatura
import requests

from bs4 import BeautifulSoup


# =====================================================
# Configuration
# =====================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Connection": "keep-alive"
}

REQUEST_TIMEOUT = 15


HOMEPAGES = {

    "https://www.bbc.com/news",
    "https://www.reuters.com",
    "https://www.thehindu.com",
    "https://indianexpress.com",
    "https://timesofindia.indiatimes.com"

}


# =====================================================
# URL Validation
# =====================================================

def is_valid_url(url):

    if not url:
        return False

    if not url.startswith(("http://", "https://")):
        return False

    if url.rstrip("/") in HOMEPAGES:
        return False

    return True


# =====================================================
# Clean Text
# =====================================================

def clean_text(text):

    if not text:
        return ""

    return " ".join(str(text).split())


# =====================================================
# Normalize Authors
# =====================================================

def normalize_authors(authors):
    """
    Always return authors as a clean list.
    If no author is found, return ['Unknown'].
    """

    if authors is None:
        return ["Unknown"]

    if isinstance(authors, str):
        authors = [authors]

    if not isinstance(authors, list):
        return ["Unknown"]

    cleaned = []

    for author in authors:

        if not isinstance(author, str):
            continue

        author = author.strip()

        if not author:
            continue

        if author not in cleaned:
            cleaned.append(author)

    if not cleaned:
        return ["Unknown"]

    return cleaned
# =====================================================
# Method 1 : newspaper3k
# =====================================================

def extract_with_newspaper(url):

    try:

        article = Article(url)

        article.download()

        article.parse()

        title = clean_text(article.title)

        content = clean_text(article.text)

        authors = normalize_authors(article.authors)

        if not content:

            print("[newspaper3k] Empty content.")

            return None

        return {

            "title": title,

            "authors": authors,

            "content": content,

            "method": "newspaper3k"

        }

    except Exception as e:

        print(f"[newspaper3k] {e}")

        return None
# =====================================================
# Method 2 : Trafilatura
# =====================================================

def extract_with_trafilatura(url):

    try:

        # Download page using browser headers
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        html = response.text

        # Extract article content
        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if not content:

            print("[trafilatura] Empty content.")

            return None

        soup = BeautifulSoup(html, "html.parser")

        # --------------------------------------------
        # Title Extraction
        # --------------------------------------------

        title = ""

        # 1. Open Graph Title
        og_title = soup.find("meta", property="og:title")

        if og_title and og_title.get("content"):

            title = clean_text(og_title["content"])

        # 2. HTML Title
        if not title and soup.title:

            title = clean_text(soup.title.get_text())

        # --------------------------------------------
        # Author Extraction
        # --------------------------------------------

        authors = []

        meta_author = soup.find("meta", attrs={"name": "author"})

        if meta_author and meta_author.get("content"):

            authors.append(meta_author["content"])

        authors = normalize_authors(authors)

        return {

            "title": title,

            "authors": authors,

            "content": clean_text(content),

            "method": "trafilatura"

        }

    except Exception as e:

        print(f"[trafilatura] {e}")

        return None
# =====================================================
# Method 3 : BeautifulSoup
# =====================================================

def extract_with_bs4(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # --------------------------------------------
        # Title Extraction
        # --------------------------------------------
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = clean_text(og_title["content"])
        if not title:
            twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
            if twitter_title and twitter_title.get("content"):
                title = clean_text(twitter_title["content"])
        if not title and soup.title:
            title = clean_text(soup.title.get_text())
        print("Extracted Title:", title)
        # --------------------------------------------
        # Author Extraction
        # --------------------------------------------
        authors = []
        meta_author = soup.find("meta", attrs={"name": "author"})
        if meta_author and meta_author.get("content"):
            authors.append(meta_author["content"])

        authors = normalize_authors(authors)

        # --------------------------------------------
        # Content Extraction
        # --------------------------------------------

        article = soup.find("article")

        if article:

            paragraphs = article.find_all("p")

        else:

            paragraphs = soup.find_all("p")

        content = "\n".join(

            p.get_text(" ", strip=True)

            for p in paragraphs

        )

        content = clean_text(content)

        if not content:

            print("[BeautifulSoup] Empty content.")

            return None

        return {

            "title": title,

            "authors": authors,

            "content": content,

            "method": "beautifulsoup"

        }

    except Exception as e:

        print(f"[BeautifulSoup] {e}")

        return None
# =====================================================
# Master Extraction Function
# =====================================================

def extract_article(url):

    if not is_valid_url(url):

        print("Invalid URL")

        return None

    methods = [

        extract_with_newspaper,

        extract_with_trafilatura,

        extract_with_bs4

    ]

    for method in methods:

        print(f"\nTrying {method.__name__}...")

        result = method(url)

        if not result:
            continue

        title = clean_text(result.get("title"))

        content = clean_text(result.get("content"))

        authors = normalize_authors(result.get("authors"))

        if not content:
            continue

        print(f"✓ Success using {result['method']}")

        return {

            "title": title,

            "authors": authors,

            "content": content,

            "method": result["method"]

        }

    print("\n✗ All extraction methods failed.")

    return None


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    url = input("Enter article URL: ").strip()

    result = extract_article(url)
    print("TITLE FROM EXTRACTOR:", result["title"])
    

    if result:

        print("\n" + "=" * 80)

        print("TITLE")
        print(result["title"])

        print("\nMETHOD")
        print(result["method"])

        print("\nAUTHORS")
        print(result["authors"])

        print("\nCONTENT PREVIEW")
        print(result["content"][:1000])

        print("\n" + "=" * 80)

    else:

        print("\nExtraction failed.")