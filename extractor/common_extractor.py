"""
=========================================================
Common Extractor

Shared utilities for all newspaper extractors.

Responsibilities
----------------
Download Article HTML
↓
Parse HTML
↓
Clean Text
↓
Common Helper Functions
=========================================================
"""

# =====================================================
# Standard Library
# =====================================================

import logging
import re
import time

from datetime import (
    datetime,
    UTC,
)

# =====================================================
# Third Party Libraries
# =====================================================

import requests

from bs4 import (
    BeautifulSoup,
)

from requests.adapters import (
    HTTPAdapter,
)

from urllib3.util.retry import Retry
from config import (
    HEADERS,
    TIMEOUT,
    MAX_RETRIES,
    LOG_SEPARATOR,
)



# =====================================================
# Logging
# =====================================================

logger = logging.getLogger(
    "CommonExtractor"
)

# =====================================================
# HTTP Session
# =====================================================

session = requests.Session()

session.headers.update(
    HEADERS
)

retry_strategy = Retry(

    total=MAX_RETRIES,

    backoff_factor=2,

    status_forcelist=[
        429,
        500,
        502,
        503,
        504,
    ],

    allowed_methods=[
        "GET"
    ],

)

adapter = HTTPAdapter(

    max_retries=retry_strategy,

    pool_connections=20,

    pool_maxsize=20,

)

session.mount(
    "http://",
    adapter,
)

session.mount(
    "https://",
    adapter,
)

# =====================================================
# Configuration
# =====================================================

REQUEST_DELAY = 1

DEFAULT_PARSER = "html.parser"

DEFAULT_ENCODING = "utf-8"

MAX_CONTENT_LENGTH = 500000

# =====================================================
# Download Article HTML
# =====================================================

def download_article(
    article_url
):
    """
    Download article HTML.

    Parameters
    ----------
    article_url : str

    Returns
    -------
    BeautifulSoup
    """

    if not article_url:

        raise ValueError(
            "Article URL cannot be empty."
        )

    logger.info(LOG_SEPARATOR)
    logger.info("Downloading Article")
    logger.info(f"URL : {article_url}")

    started = time.perf_counter()

    try:
        time.sleep(REQUEST_DELAY)
        response = session.get(

            article_url,

            timeout=TIMEOUT

        )

        response.raise_for_status()
        response.encoding = response.apparent_encoding

        duration = round(

            time.perf_counter() - started,

            3

        )

        logger.info(
    f"Status Code : {response.status_code}"
)

        logger.info(
    f"Download Completed ({duration:.3f} sec)"
)

        logger.info(LOG_SEPARATOR)

        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(
            response.text,
            DEFAULT_PARSER
        )

        if not article_exists(soup):
            return None

        return soup
    except requests.exceptions.Timeout:

        logger.exception(
            "Request Timeout"
        )

    except requests.exceptions.ConnectionError:

        logger.exception(
            "Connection Error"
        )

    except requests.exceptions.HTTPError:

        logger.exception(
            "HTTP Error"
        )

    except requests.exceptions.RequestException:

        logger.exception(
            "Request Failed"
        )

    except Exception:

        logger.exception(
            "Unexpected Error"
        )

    return None


# =====================================================
# Validate HTML
# =====================================================

def is_valid_html(
    soup
):
    """
    Validate downloaded HTML.
    """

    if soup is None:

        return False

    if soup.find("html") is None:

        return False

    return True


# =====================================================
# Get Meta Content
# =====================================================

def get_meta_content(
    soup,
    property_name
):
    """
    Read meta tag value safely.

    Example
    -------
    og:title

    description

    author
    """

    if not is_valid_html(soup):

        return ""

    tag = soup.find(

        "meta",

        attrs={

            "property": property_name

        }

    )

    if tag is None:

        tag = soup.find(

            "meta",

            attrs={

                "name": property_name

            }

        )

    if tag is None:

        return ""

    return tag.get(

        "content",

        ""

    ).strip()

# =====================================================
# Get HTML Title
# =====================================================

def get_html_title(
    soup
):
    """
    Read HTML <title>.
    """

    if not is_valid_html(soup):

        return ""

    if soup.title is None:

        return ""

    return soup.title.get_text(

        strip=True

    )
# =====================================================
# Remove Extra Spaces
# =====================================================

def remove_extra_spaces(
    text
):
    """
    Remove unnecessary whitespace.
    """

    if not text:

        return ""

    return re.sub(

        r"\s+",

        " ",

        text

    ).strip()


# =====================================================
# Remove HTML Tags
# =====================================================

def remove_html_tags(
    html
):
    """
    Remove HTML tags from text.
    """

    if not html:

        return ""

    soup = BeautifulSoup(

        html,

        DEFAULT_PARSER

    )

    return remove_extra_spaces(

        soup.get_text(

            separator=" "

        )

    )


# =====================================================
# Normalize Text
# =====================================================

def normalize_text(
    text
):
    """
    Normalize article text.
    """

    if not text:

        return ""

    text = remove_html_tags(
        text
    )

    text = text.replace(

        "\xa0",

        " "

    )

    text = text.replace(

        "\u200b",

        ""

    )

    text = text.replace(

        "\ufeff",

        ""

    )

    text = remove_extra_spaces(
        text
    )

    return text


# =====================================================
# Safe Text
# =====================================================

def safe_text(
    element
):
    """
    Safely extract text from a BeautifulSoup element.
    """

    if element is None:

        return ""

    try:

        return normalize_text(

            element.get_text(

                separator=" ",

                strip=True

            )

        )

    except Exception:

        return ""


# =====================================================
# Safe Attribute
# =====================================================

def safe_attribute(
    element,
    attribute
):
    """
    Safely read an HTML attribute.
    """

    if element is None:

        return ""

    return str(

        element.get(

            attribute,

            ""

        )

    ).strip()

# =====================================================
# Extract First Match
# =====================================================

def extract_first_match(
    soup,
    selectors
):
    """
    Return first matching value
    from a list of CSS selectors.
    """

    if not is_valid_html(soup):

        return ""

    for selector in selectors:

        element = soup.select_one(selector)

        if element is None:

            continue

        # Try common HTML attributes
        for attribute in [

            "content",

            "datetime",

        ]:

            value = safe_attribute(

                element,

                attribute

            )

            if value:

                return normalize_text(value)

        # Normal HTML text
        value = safe_text(
            element
        )

        if value:

            return normalize_text(value)

    return ""
# =====================================================
# Truncate Text
# =====================================================

def truncate_text(
    text,
    max_length=MAX_CONTENT_LENGTH
):
    """
    Prevent oversized MongoDB documents.
    """

    if not text:

        return ""

    if len(text) <= max_length:

        return text

    logger.warning(

        "Content truncated because it exceeded "
        f"{max_length} characters."

    )

    return text[:max_length]


# =====================================================
# Validate Content
# =====================================================

def has_content(
    text,
    minimum_length=100
):
    """
    Check whether extracted content is useful.
    """

    if not text:

        return False

    text = normalize_text(
        text
    )

    return len(text) >= minimum_length
# =====================================================
# Extract Paragraphs
# =====================================================

def extract_paragraphs(
    soup,
    selectors
):
    """
    Extract article paragraphs using a list of CSS selectors.

    Parameters
    ----------
    soup : BeautifulSoup

    selectors : list[str]

    Returns
    -------
    str
    """

    if not is_valid_html(soup):

        return ""

    for selector in selectors:

        elements = soup.select(selector)

        if not elements:

            continue

        paragraphs = []

        for element in elements:

            text = safe_text(element)

            if text:

                paragraphs.append(text)

        content = "\n\n".join(paragraphs)

        content = truncate_text(
            normalize_text(content)
        )

        if has_content(content):

            return content

    return ""


# =====================================================
# Extract Authors
# =====================================================

def extract_authors(
    soup,
    selectors
):
    """
    Extract article authors.

    Returns
    -------
    list
    """

    if not is_valid_html(soup):

        return ["Unknown"]

    authors = []

    for selector in selectors:

        elements = soup.select(selector)

        if not elements:

            continue

        for element in elements:

            author = safe_text(element)

            if author:

                authors.append(author)

        if authors:

            break

    authors = list(dict.fromkeys(authors))

    return authors if authors else ["Unknown"]


# =====================================================
# Extract Published Date
# =====================================================


def extract_published_date(
    soup,
    selectors
):
    """
    Extract article published date.
    """

    return extract_first_match(

        soup,

        selectors

    )

# =====================================================
# Extract Description
# =====================================================

def extract_description(
    soup,
    selectors
):
    """
    Extract article description.
    """

    return extract_first_match(

        soup,

        selectors

    )
# =====================================================
# Extract Title
# =====================================================

def extract_title(
    soup,
    selectors
):
    """
    Extract article title.
    """

    return extract_first_match(

        soup,

        selectors

    )
# =====================================================
# Check Article Download
# =====================================================

def article_exists(
    soup
):
    """
    Check whether the article page
    is valid and contains useful HTML.
    """

    if not is_valid_html(soup):

        return False

    body = soup.find("body")

    if body is None:

        return False

    return True


# =====================================================
# Build Extraction Result
# =====================================================

def build_result(

    title="",

    description="",

    authors=None,

    content="",

    published_date="",

    extraction_method="BeautifulSoup",

):
    """
    Build standard extraction dictionary.
    """

    if authors is None:

        authors = ["Unknown"]

    return {

        "title": normalize_text(title),

        "description": normalize_text(description),

        "authors": authors,

        "content": truncate_text(

            normalize_text(content)

        ),

        "published_date": published_date,

        "extraction_method": extraction_method,

    }

# =====================================================
# Close HTTP Session
# =====================================================

def close_session():
    """
    Close HTTP session.
    """

    session.close()

    logger.info(

        "HTTP Session Closed"

    )


# =====================================================
# Extractor Health Check
# =====================================================

def extractor_health():
    """
    Verify extractor configuration.
    """

    logger.info(LOG_SEPARATOR)

    logger.info(

        "Common Extractor Ready"

    )

    logger.info(

        f"Parser        : {DEFAULT_PARSER}"

    )

    logger.info(

        f"Timeout       : {TIMEOUT}"

    )

    logger.info(

        f"Retries       : {MAX_RETRIES}"

    )
    logger.info(
    f"Max Content : {MAX_CONTENT_LENGTH}"
)

    logger.info(

        f"Request Delay : {REQUEST_DELAY}"

    )

    logger.info(LOG_SEPARATOR)