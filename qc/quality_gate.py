"""
=====================================================
Data Quality Gate & Quarantine Layer
News Intelligence Platform
=====================================================
"""

import re
from datetime import datetime, timezone
import urllib.parse
from config import (
    MIN_TITLE_LENGTH,
    MIN_CONTENT_LENGTH,
    MIN_CLEAN_CONTENT_LENGTH,
    QUALITY_SCORE_THRESHOLD,
    SUPPORTED_SOURCES,
)

def is_valid_url(url: str) -> bool:
    """Validate HTTP/HTTPS URL structure."""
    if not isinstance(url, str) or not url.strip():
        return False
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def parse_date_safely(dt_val) -> tuple[datetime | None, str | None]:
    """Parse date into UTC datetime object and return warning if invalid."""
    if not dt_val:
        return None, "Missing publication date"
    if isinstance(dt_val, datetime):
        return dt_val, None
    s = str(dt_val).strip()
    try:
        # ISO format
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt, None
    except Exception:
        pass
    
    # Common RFC 822 formats
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt, None
        except Exception:
            continue
    return None, f"Unrecognized date format: '{s[:30]}'"

def evaluate_article_quality(article: dict) -> dict:
    """
    Perform comprehensive Data Quality (DQ) evaluation.
    Returns dictionary with quality_score, status, warnings, and errors.
    """
    score = 100.0
    warnings = []
    errors = []

    # 1. Article ID Check
    article_id = article.get("article_id") or str(article.get("_id", ""))
    if not article_id or article_id == "None":
        score -= 40.0
        errors.append("Missing or null article_id")

    # 2. URL / Link Check
    link = article.get("link") or article.get("url") or ""
    if not is_valid_url(link):
        score -= 30.0
        errors.append(f"Invalid or missing article URL: '{link}'")

    # 3. Source Name Check
    src = article.get("source")
    source_name = src if isinstance(src, str) else (src.get("name") if isinstance(src, dict) else None)
    if not source_name:
        score -= 20.0
        errors.append("Missing source publisher name")

    # 4. Title Validation
    title = str(article.get("title") or "").strip()
    if not title:
        score -= 40.0
        errors.append("Empty article title")
    elif len(title) < MIN_TITLE_LENGTH:
        score -= 15.0
        warnings.append(f"Short title length ({len(title)} < {MIN_TITLE_LENGTH} chars)")

    # 5. Date Validation
    pub_date = article.get("published_date") or article.get("created_at")
    dt_obj, date_err = parse_date_safely(pub_date)
    if date_err:
        score -= 10.0
        warnings.append(date_err)
    elif dt_obj:
        now_utc = datetime.now(timezone.utc)
        if dt_obj.tzinfo is not None:
            delta = (dt_obj - now_utc).total_seconds()
        else:
            delta = (dt_obj - datetime.now()).total_seconds()
        if delta > 172800:
            score -= 20.0
            warnings.append(f"Future published date detected: {dt_obj}")

    # 6. Body Content Validation
    content = str(article.get("content") or "").strip()
    clean_content = str(article.get("clean_content") or "").strip()
    stage = article.get("processing", {}).get("stage") or article.get("processing", {}).get("status")

    if stage in ("extracted", "enriched", "completed"):
        if not content and not clean_content:
            score -= 35.0
            errors.append("Post-extraction content is completely empty")
        elif len(clean_content) < MIN_CLEAN_CONTENT_LENGTH and len(content) < MIN_CONTENT_LENGTH:
            score -= 15.0
            warnings.append(f"Content length below minimum threshold ({len(clean_content)} chars)")

    # 7. Embedding Vector Dimension Check (if enriched)
    embedding = article.get("embedding")
    if embedding is not None:
        if not isinstance(embedding, list) or len(embedding) != 384:
            score -= 30.0
            errors.append(f"Invalid embedding vector dimension (expected 384, got {len(embedding) if isinstance(embedding, list) else type(embedding)})")

    # Clamp score between 0 and 100
    final_score = max(0.0, min(100.0, score))
    is_quarantined = len(errors) > 0 or final_score < QUALITY_SCORE_THRESHOLD

    return {
        "quality_score": round(final_score, 2),
        "quality_status": "QUARANTINED" if is_quarantined else "PASSED",
        "warnings": warnings,
        "errors": errors,
        "evaluated_at": datetime.now().isoformat()
    }
