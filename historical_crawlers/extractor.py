"""
extractor.py

Article Extraction Module

Extraction Pipeline

1. newspaper3k
2. trafilatura
3. BeautifulSoup

Version 4
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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

REQUEST_TIMEOUT = 20


# =====================================================
# Supported News Homepages
# =====================================================

HOMEPAGES = {

    "https://www.thehindu.com",
    "https://indianexpress.com",
    "https://timesofindia.indiatimes.com",
    "https://www.hindustantimes.com"

}


# =====================================================
# Paywall / Invalid Content Detection
# =====================================================

PAYWALL_PATTERNS = {

    # Login
    "login",
    "log in",
    "sign in",
    "sign up",
    "signup",
    "register",
    "register now",
    "create account",
    "already have an account",
    "new user",

    # Password / OTP
    "welcome back",
    "forgot password",
    "show password",
    "enter password",
    "mobile number",
    "email address",
    "otp",
    "verify otp",

    # Social Login
    "continue with google",
    "continue with facebook",
    "continue with apple",
    "google",
    "facebook",
    "apple",

    # Subscription
    "subscribe",
    "subscription",
    "premium",
    "premium article",
    "premium content",
    "member benefits",
    "member only",
    "unlock this article",
    "continue reading",
    "already an etprime member",
    "etprime member",

    # Other
    "access denied",
    "cookie policy",
    "accept cookies"

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
# Validate Extracted Content
# =====================================================

def is_valid_content(content):

    if not content:
        return False

    content = clean_text(content)

    if len(content) < 300:
        print("Rejected : Content too short")
        return False

    lower = content.lower()

    matched_patterns = []

    for pattern in PAYWALL_PATTERNS:

        if pattern in lower:
            matched_patterns.append(pattern)

    # Reject only if multiple suspicious patterns are found
    if len(matched_patterns) >= 3:

        print("\nRejected : Login / Paywall Page Detected")
        print("Matched Patterns:", matched_patterns)

        return False

    return True

# =====================================================
# Normalize Authors
# =====================================================

def normalize_authors(authors):

    if authors is None:
        return ["Unknown"]

    if isinstance(authors, str):
        authors = [authors]

    if not isinstance(authors, list):
        return ["Unknown"]

    invalid = {

        "",
        "author",
        "authors",
        "staff",
        "staff reporter",
        "agency",
        "editor",
        "admin",
        "news desk",
        "updated",
        "hour ago",
        "hours ago",
        "minute ago",
        "minutes ago",
        "day ago",
        "days ago"

    }

    cleaned = []

    for author in authors:

        if not isinstance(author, str):
            continue

        author = author.strip()

        if author.lower() in invalid:
            continue

        if author not in cleaned:
            cleaned.append(author)

    if not cleaned:
        cleaned.append("Unknown")

    return cleaned
def is_valid_author(authors):

    invalid_patterns = {

        "login",
        "sign in",
        "show password",
        "forgot password",
        "google",
        "facebook",
        "apple",
        "otp",
        "register",
        "subscribe"

    }

    if authors == ["Unknown"]:
        return True

    author_text = " ".join(authors).lower()

    for pattern in invalid_patterns:

        if pattern in author_text:

            print("Rejected : Invalid author field")

            return False

    return True


# =====================================================
# Extract Title
# =====================================================

def extract_title(soup):

    og = soup.find("meta", property="og:title")

    if og and og.get("content"):
        return clean_text(og["content"])

    twitter = soup.find("meta", attrs={"name": "twitter:title"})

    if twitter and twitter.get("content"):
        return clean_text(twitter["content"])

    if soup.title:
        return clean_text(soup.title.get_text())

    return ""


# =====================================================
# Extract Authors
# =====================================================

def extract_authors(soup):

    authors = []

    meta_author = soup.find("meta", attrs={"name": "author"})

    if meta_author and meta_author.get("content"):
        authors.append(meta_author["content"])

    return normalize_authors(authors)


# =====================================================
# Logging Helper
# =====================================================

def log_result(method, success):

    if success:
        print(f"✓ {method} succeeded")
    else:
        print(f"✗ {method} failed")

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

        # Validation is handled in extract_article()

        log_result("newspaper3k", True)

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

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        html = response.text

        content = trafilatura.extract(

            html,

            include_comments=False,

            include_tables=False,

            favor_precision=True

        )

        if not is_valid_content(content):

            log_result("trafilatura", False)

            return None

        soup = BeautifulSoup(html, "html.parser")

        title = extract_title(soup)

        authors = extract_authors(soup)

        log_result("trafilatura", True)

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

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = extract_title(soup)

        authors = extract_authors(soup)

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

        if not is_valid_content(content):

            log_result("beautifulsoup", False)

            return None

        log_result("beautifulsoup", True)

        return {

            "title": title,

            "authors": authors,

            "content": content,
            
            "method": "beautifulsoup"

        }

    except Exception as e:

        print(f"[BeautifulSoup] {e}")

        return None
# # =====================================================
# # Master Extraction Function
# # =====================================================

# def extract_article(url):

#     print("\n" + "=" * 70)
#     print("Starting Article Extraction")
#     print("=" * 70)

#     if not is_valid_url(url):

#         print("Invalid URL")

#         return None

#     methods = [

#         extract_with_newspaper,
#         extract_with_trafilatura,
#         extract_with_bs4

#     ]

#     for method in methods:

#         print(f"\nTrying {method.__name__}...")

#         result = method(url)

#         if result is None:

#             print("Trying next extraction method...")

#             continue

#         title = clean_text(result.get("title"))

#         content = clean_text(result.get("content"))

#         authors = normalize_authors(result.get("authors"))

#         if not is_valid_content(content):

#             print("Invalid extracted content.")

#             continue
#         if not is_valid_content(content):

#              print("Invalid extracted content.")

#         continue

#         print("\n" + "=" * 70)
#         print("Article Extracted Successfully")
#         print("=" * 70)

#         print("Method :", result["method"])
#         print("Title  :", title)
#         print("Author :", ", ".join(authors))
#         print("Length :", len(content), "characters")

#         return {

#             "title": title,

#             "authors": authors,

#             "content": content,

#             "method": result["method"]

#         }

#     print("\n" + "=" * 70)
#     print("All Extraction Methods Failed")
#     print("=" * 70)

#     return None


# =====================================================
# Master Extraction Function
# =====================================================

def extract_article(url):

    print("\n" + "=" * 70)
    print("Starting Article Extraction")
    print("=" * 70)

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

        if result is None:
            print("Trying next extraction method...")
            continue

        title = clean_text(result.get("title"))
        content = clean_text(result.get("content"))
        authors = normalize_authors(result.get("authors"))

        # Validate extracted content
        if not is_valid_content(content):
            print("Invalid extracted content.")
            continue

        # Validate author
        if not is_valid_author(authors):
            print("Invalid author information.")
            continue

        print("\n" + "=" * 70)
        print("Article Extracted Successfully")
        print("=" * 70)

        print("Method :", result["method"])
        print("Title  :", title)
        print("Author :", ", ".join(authors))
        print("Length :", len(content), "characters")

        return {
            "title": title,
            "authors": authors,
            "content": content,
            "method": result["method"]
        }

    print("\n" + "=" * 70)
    print("All Extraction Methods Failed")
    print("=" * 70)

    return None


# =====================================================
# Test
# =====================================================

if __name__ == "__main__":

    print("=" * 70)
    print("News Article Extractor")
    print("=" * 70)

    url = input("\nEnter Article URL : ").strip()

    result = extract_article(url)

    if result:

        print("\n" + "=" * 70)
        print("Extraction Result")
        print("=" * 70)

        print("\nTitle")
        print("-" * 70)
        print(result["title"])

        print("\nMethod")
        print("-" * 70)
        print(result["method"])

        print("\nAuthors")
        print("-" * 70)
        print(result["authors"])

        print("\nContent Preview")
        print("-" * 70)

        preview = result["content"][:1200]

        print(preview)

        if len(result["content"]) > 1200:
            print("\n...")
            print("\n(Content Truncated)")

        print("\n" + "=" * 70)

    else:

        print("\nExtraction Failed.")