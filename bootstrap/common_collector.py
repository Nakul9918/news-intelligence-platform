
"""
=========================================================
Common Collector

Shared utilities used by all newspaper collectors.

Workflow

Download Sitemap
        ↓
Parse XML
        ↓
Build Standard Article Schema
        ↓
Return Article List
=========================================================
"""

# =====================================================
# Standard Library
# =====================================================

import hashlib
import logging
import time
from datetime import (
    datetime,
    UTC,
)

# =====================================================
# Third Party
# =====================================================

import requests

from bs4 import BeautifulSoup

DEFAULT_PARSER = "xml"

from pymongo import MongoClient

from requests.adapters import HTTPAdapter

# =====================================================
# Project Configuration
# =====================================================

from config import (
    MONGO_URI,
    DATABASE_NAME,
    HEADERS,
    TIMEOUT,
    MAX_RETRIES,
)

# =====================================================
# Logging
# =====================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(name)s | "
        "%(levelname)s | "
        "%(message)s"
    )

)

logger = logging.getLogger(
    "CommonCollector"
)

# =====================================================
# MongoDB
# =====================================================

client = MongoClient(

    MONGO_URI,

    maxPoolSize=20,

    retryWrites=True,

    serverSelectionTimeoutMS=5000,

)

db = client[DATABASE_NAME]


def get_collection(collection_name):
    """
    Return MongoDB collection.
    """

    return db[collection_name]


# =====================================================
# HTTP Session
# =====================================================

session = requests.Session()

session.headers.update(HEADERS)

adapter = HTTPAdapter(

    pool_connections=20,

    pool_maxsize=20,

    max_retries=0,

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
# Schema Configuration
# =====================================================

SCHEMA_VERSION = "1.0.0"

PIPELINE_VERSION = "1.0.0"

COLLECTOR_VERSION = "1.0.0"

DEFAULT_LANGUAGE = "en"

DEFAULT_COUNTRY = "India"

DEFAULT_SOURCE_TYPE = "rss"

REQUEST_DELAY = 1

# =====================================================
# Utility Functions
# =====================================================

def generate_article_id(article_url):
    """
    Generate a stable SHA256 article id.

    Same URL will always generate
    the same article_id.
    """

    return hashlib.sha256(

        article_url.encode("utf-8")

    ).hexdigest()


def utc_now():
    """
    Return UTC datetime.
    """
    return datetime.now(UTC)


def article_exists(soup):
    """
    Validate that the downloaded sitemap
    contains URL entries.
    """

    if soup is None:
        return False

    return soup.find("url") is not None
# =====================================================
# Download XML
# =====================================================

def download_xml(url):
    """
    Download XML sitemap.

    Returns
    -------
    BeautifulSoup
    """

    logger.info("=" * 70)

    logger.info("Downloading Sitemap")

    logger.info(f"URL : {url}")

    logger.info("=" * 70)

    started = time.perf_counter()

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.get(

                url,

                timeout=TIMEOUT

            )

            response.raise_for_status()

            duration = round(

                time.perf_counter() - started,

                3

            )

            logger.info(

                f"Download Completed : {duration:.2f} sec"

            )

            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(
                response.text,
                DEFAULT_PARSER
            )

            if not article_exists(soup):
                return None

            return soup
        except requests.exceptions.Timeout:

            logger.warning(

                f"Timeout ({attempt}/{MAX_RETRIES})"

            )

        except requests.exceptions.ConnectionError:

            logger.warning(

                f"Connection Error ({attempt}/{MAX_RETRIES})"

            )

        except requests.exceptions.HTTPError as e:

            logger.warning(

                f"HTTP Error : {e}"

            )

        except requests.exceptions.RequestException as e:

            logger.warning(

                f"Request Error : {e}"

            )

        if attempt < MAX_RETRIES:

            wait = 2 ** attempt

            logger.info(

                f"Retrying in {wait} sec..."

            )

            time.sleep(wait)

    logger.error("=" * 70)

    logger.error("Unable To Download Sitemap")

    logger.error(url)

    logger.error("=" * 70)

    raise RuntimeError(

        f"Unable to download : {url}"

    )


# =====================================================
# Parse Published Date
# =====================================================

SUPPORTED_DATE_FORMATS = [

    "%Y-%m-%d",

    "%Y-%m-%d %H:%M:%S",

    "%Y-%m-%dT%H:%M:%S",

    "%Y-%m-%dT%H:%M:%S%z",

    "%Y-%m-%dT%H:%M:%S.%f%z",

    "%a, %d %b %Y %H:%M:%S %z",

    "%d %b %Y %H:%M:%S %z",

    "%Y/%m/%d",

]


def parse_published_date(date_string):
    """
    Convert string into datetime.

    Returns
    -------
    datetime | None
    """

    if not date_string:

        return None

    date_string = date_string.strip()

    # ----------------------------------------
    # ISO Format
    # ----------------------------------------

    try:

        parsed = datetime.fromisoformat(

            date_string.replace(

                "Z",

                "+00:00"

            )

        )

    except Exception:

        parsed = None

    if parsed is None:

        for fmt in SUPPORTED_DATE_FORMATS:

            try:

                parsed = datetime.strptime(

                    date_string,

                    fmt

                )

                break

            except ValueError:

                continue

    if parsed is None:

        logger.warning(

            f"Unsupported Date : {date_string}"

        )

        return None

    # ----------------------------------------
    # Convert Naive → UTC
    # ----------------------------------------

    if parsed.tzinfo is None:

        parsed = parsed.replace(

            tzinfo=UTC

        )

    return parsed


# =====================================================
# Date Range Validation
# =====================================================

def is_date_in_range(

    published_datetime,

    start_date,

    end_date

):
    """
    Validate bootstrap date range.

    Returns
    -------
    bool
    """

    if published_datetime is None:

        return False

    if published_datetime.tzinfo is not None:

        published_datetime = published_datetime.replace(

            tzinfo=None

        )

    if start_date.tzinfo is not None:

        start_date = start_date.replace(

            tzinfo=None

        )

    if end_date.tzinfo is not None:

        end_date = end_date.replace(

            tzinfo=None

        )

    return (

        start_date

        <=

        published_datetime

        <=

        end_date

    )
# =====================================================
# Build Article
# =====================================================

def build_article(

    article_url,

    published,

    source_name,

    ingestion_type="bootstrap"

):
    """
    Build the standard article document.

    Every pipeline component
    should use this schema.
    """

    # ---------------------------------------------
    # Common Values
    # ---------------------------------------------

    now = utc_now()

    article_id = generate_article_id(

        article_url

    )

    published_datetime = parse_published_date(

        published

    )

    # ---------------------------------------------
    # Standard Document
    # ---------------------------------------------

    article = {

        # =================================================
        # Identity
        # =================================================

        "article_id": article_id,

        "link": article_url,

        "ingestion_type": ingestion_type,

        # =================================================
        # Source
        # =================================================

        "source": {

            "name": source_name,

            "country": DEFAULT_COUNTRY,

            "language": DEFAULT_LANGUAGE,

            "type": DEFAULT_SOURCE_TYPE

        },

        # =================================================
        # Basic Information
        # =================================================

        "title": "",

        "description": "",

        "authors": [

            "Unknown"

        ],

        "language": DEFAULT_LANGUAGE,

        # =================================================
        # Dates
        # =================================================

        "published_date": published,

        "published_datetime": published_datetime,

        "created_at": now,

        "updated_at": now,

        "fetched_at": now,

        "last_pipeline_update": now,

        # =================================================
        # Content
        # =================================================

        "content": "",

        "clean_content": "",

        # =================================================
        # NLP
        # =================================================

        "keywords": [],

        "entities": [],

        "sentiment": {

            "label": "",

            "score": 0.0,

            "model": ""

        },

        "category": {

            "label": "",

            "score": 0.0,

            "model": ""

        },

        "summary": {

            "text": "",

            "model": ""

        },

        "embedding": {

            "model": "",

            "vector_id": ""

        },

        # =================================================
        # Processing
        # =================================================

        "processing": {

            "pipeline_version": PIPELINE_VERSION,

            "collector": source_name,

            "ingestion_time": 0,

            "extract_time": 0,

            "clean_time": 0,

            "keyword_time": 0,

            "sentiment_time": 0,

            "category_time": 0,

            "ner_time": 0,

            "summary_time": 0,

            "embedding_time": 0,

            "vector_time": 0,

            "total_time": 0

        },

        # =================================================
        # Status
        # =================================================

        "status": {

            "ingested": True,

            "content_extracted": False,

            "content_extract_processing": False,

            "content_extract_failed": False,

            "content_extract_retry_count": 0,

            "content_cleaned": False,

            "content_clean_processing": False,

            "content_clean_failed": False,

            "content_clean_retry_count": 0,

            "keywords_done": False,

            "keywords_processing": False,

            "keywords_failed": False,

            "keywords_retry_count": 0,

            "sentiment_done": False,

            "sentiment_processing": False,

            "sentiment_failed": False,

            "sentiment_retry_count": 0,

            "category_done": False,

            "category_processing": False,

            "category_failed": False,

            "category_retry_count": 0,

            "ner_done": False,

            "ner_processing": False,

            "ner_failed": False,

            "ner_retry_count": 0,

            "summary_done": False,

            "summary_processing": False,

            "summary_failed": False,

            "summary_retry_count": 0,

            "embedding_done": False,

            "embedding_processing": False,

            "embedding_failed": False,

            "embedding_retry_count": 0,

            "vector_indexed": False,

            "vector_index_processing": False,

            "vector_index_failed": False,

            "vector_index_retry_count": 0,

            "pipeline_completed": False

        },

        # =================================================
        # Audit
        # =================================================

        "audit": {

            "created_by": "bootstrap",

            "updated_by": "bootstrap",

            "last_updated_stage": "collector"

        },

        # =================================================
        # Metadata
        # =================================================

        "schema_version": SCHEMA_VERSION,

        "pipeline_version": PIPELINE_VERSION,

        "collector_version": COLLECTOR_VERSION,

        "last_pipeline_stage": "collector",

        "ingestion_type": "bootstrap",

        # =================================================
        # Extraction
        # =================================================

        "extraction_method": "",

        "error": None

    }

    return article
# =====================================================
# Collect Articles
# =====================================================

def collect_articles(
    xml_url,
    source_name
):
    """
    Download sitemap.

    Parse XML.

    Build standard article documents.

    Returns
    -------
    list[dict]
    """

    logger.info("=" * 70)
    logger.info(f"Collecting Articles : {source_name}")
    logger.info("=" * 70)

    soup = download_xml(
        xml_url
    )

    urls = soup.find_all("url")

    logger.info(
        f"URLs Found : {len(urls)}"
    )

    articles = []

    skipped = 0

    duplicate_urls = set()

    started = time.perf_counter()

    # =================================================
    # Parse Sitemap
    # =================================================

    for url in urls:

        try:

            # ---------------------------------------------
            # Article URL
            # ---------------------------------------------

            loc = url.find("loc")

            if loc is None:

                skipped += 1

                continue

            article_url = loc.text.strip()

            if not article_url:

                skipped += 1

                continue

            # ---------------------------------------------
            # Duplicate URL
            # ---------------------------------------------

            if article_url in duplicate_urls:

                skipped += 1

                continue

            duplicate_urls.add(
                article_url
            )

            # ---------------------------------------------
            # Published Date
            # ---------------------------------------------

            published = ""

            # Try multiple XML tag names used across news sitemaps & RSS
            date_tag = (
                url.find("news:publication_date")
                or url.find("publication_date")
                or url.find("lastmod")
                or url.find("pubdate")
                or url.find("pubDate")
                or url.find("dc:date")
            )

            if date_tag and date_tag.text:
                published = date_tag.text.strip()

            # ---------------------------------------------
            # Build Article
            # ---------------------------------------------

            article = build_article(

                article_url,

                published,

                source_name

            )

            # ---------------------------------------------
            # Basic Validation
            # ---------------------------------------------

            if not article["link"]:

                skipped += 1

                continue

            if not article["article_id"]:

                skipped += 1

                continue

            if not article["source"]["name"]:

                skipped += 1

                continue

            articles.append(
                article
            )

        except Exception as e:

            skipped += 1

            logger.exception(
                f"Failed : {e}"
            )

    # =================================================
    # Summary
    # =================================================

    duration = round(

        time.perf_counter() - started,

        3

    )

    logger.info("=" * 70)

    logger.info("Collection Summary")

    logger.info("=" * 70)

    logger.info(
        f"Source              : {source_name}"
    )

    logger.info(
        f"URLs Found          : {len(urls)}"
    )

    logger.info(
        f"Collected           : {len(articles)}"
    )

    logger.info(
        f"Skipped             : {skipped}"
    )

    logger.info(
        f"Duplicate URLs      : {len(duplicate_urls)}"
    )

    logger.info(
        f"Collection Time     : {duration:.2f} sec"
    )

    logger.info("=" * 70)

    return articles


# =====================================================
# Filter Articles By Date
# =====================================================

def filter_articles_by_date(
    articles,
    start_date,
    end_date
):
    """
    Filter articles within the bootstrap
    date range.
    """

    filtered_articles = []

    for article in articles:

        published = article.get(
            "published_datetime"
        )

        if published is None:
            continue

        if published.tzinfo is not None:

            published = published.replace(
                tzinfo=None
            )

        if start_date.tzinfo is not None:

            start_date = start_date.replace(
                tzinfo=None
            )

        if end_date.tzinfo is not None:

            end_date = end_date.replace(
                tzinfo=None
            )

        if (
            start_date
            <= published
            <= end_date
        ):

            filtered_articles.append(
                article
            )

    return filtered_articles

# =====================================================
# Print Summary
# =====================================================

def print_summary(
    source_name,
    processed,
    failed
):
    """
    Print collector summary.
    """

    logger.info("=" * 70)

    logger.info(
        f"{source_name} Summary"
    )

    logger.info("=" * 70)

    logger.info(
        f"Collected : {processed}"
    )

    logger.info(
        f"Failed    : {failed}"
    )

    logger.info("=" * 70)
# =====================================================
# Validate Article Schema
# =====================================================

def validate_article(article):
    """
    Validate the minimum schema before
    sending to Kafka.

    Returns
    -------
    bool
    """

    if not isinstance(article, dict):
        return False

    required_fields = [

        "article_id",

        "link",

        "source",

        "processing",

        "status",

        "schema_version",

        "pipeline_version",

        "collector_version"

    ]

    for field in required_fields:

        if field not in article:

            logger.error(
                f"Missing Field : {field}"
            )

            return False

    if not article["link"]:

        logger.error("Empty Link")

        return False

    if not article["article_id"]:

        logger.error("Empty Article ID")

        return False

    if not article["source"]["name"]:

        logger.error("Empty Source")

        return False

    return True


# =====================================================
# Remove Duplicate Articles
# =====================================================

def remove_duplicate_articles(
    articles
):
    """
    Remove duplicate articles using article_id.

    Returns
    -------
    list
    """

    unique = {}

    for article in articles:

        unique[
            article["article_id"]
        ] = article

    logger.info(

        f"Removed Duplicate Articles : "

        f"{len(articles) - len(unique)}"

    )

    return list(

        unique.values()

    )


# =====================================================
# Sort Articles
# =====================================================

def sort_articles(
    articles
):
    """
    Sort by published datetime.

    Oldest first.
    """

    return sorted(

        articles,

        key=lambda x: (

            x.get(

                "published_datetime"

            )

            or datetime.min.replace(

                tzinfo=UTC

            )

        )

    )


# =====================================================
# Collection Statistics
# =====================================================

def collection_statistics(
    articles
):
    """
    Print statistics.

    Useful before publishing
    to Kafka.
    """

    logger.info("=" * 70)

    logger.info("Collection Statistics")

    logger.info("=" * 70)

    logger.info(

        f"Articles : {len(articles)}"

    )

    sources = {}

    for article in articles:

        source = article["source"]["name"]

        sources[source] = (

            sources.get(source, 0) + 1

        )

    logger.info("-" * 70)

    for source, count in sources.items():

        logger.info(

            f"{source:<25} : {count}"

        )

    logger.info("=" * 70)


# =====================================================
# Close Resources
# =====================================================

def close_resources():
    """
    Close HTTP session
    and MongoDB client.
    """

    try:

        session.close()

    except Exception:

        pass

    try:

        client.close()

    except Exception:

        pass

    logger.info(

        "Resources Closed."

    )