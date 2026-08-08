"""
=====================================================
Elasticsearch Indexer & Search Module
Version : 8.0 (ES 8.17.2 Production Compatible)
=====================================================
"""

import logging
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch, helpers
from config import ELASTICSEARCH_HOST, ELASTICSEARCH_INDEX, MONGO_URI, DATABASE_NAME, REALTIME_COLLECTION_NAME

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 384

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "article_id": {"type": "keyword"},
            "link": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text", "analyzer": "standard"},
            "content": {"type": "text", "analyzer": "standard"},
            "clean_content": {"type": "text", "analyzer": "standard"},
            "source": {
                "properties": {
                    "name": {"type": "keyword"},
                    "country": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "type": {"type": "keyword"}
                }
            },
            "published_date": {"type": "date"},
            "ingestion_type": {"type": "keyword"},
            "category": {
                "properties": {
                    "label": {"type": "keyword"},
                    "score": {"type": "float"}
                }
            },
            "sentiment": {
                "properties": {
                    "label": {"type": "keyword"},
                    "score": {"type": "float"}
                }
            },
            "keywords": {"type": "keyword"},
            "summary": {
                "properties": {
                    "text": {"type": "text", "analyzer": "standard"}
                }
            },
            "entities": {
                "type": "nested",
                "properties": {
                    "entity": {"type": "keyword"},
                    "label": {"type": "keyword"},
                    "confidence": {"type": "float"}
                }
            },
            "embedding": {
                "type": "dense_vector",
                "dims": EMBEDDING_DIMENSION,
                "index": True,
                "similarity": "cosine"
            },
            "processing": {
                "properties": {
                    "status": {"type": "keyword"},
                    "stage": {"type": "keyword"}
                }
            },
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"}
        }
    }
}

def get_es_client(host: str = ELASTICSEARCH_HOST) -> Elasticsearch:
    """Connect to Elasticsearch cluster."""
    return Elasticsearch(host, request_timeout=30)

def create_index_if_not_exists(es: Optional[Elasticsearch] = None, index_name: str = ELASTICSEARCH_INDEX) -> bool:
    """Verify or create Elasticsearch index with mapping."""
    if es is None:
        es = get_es_client()
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=INDEX_MAPPING)
        logger.info(f"Created index '{index_name}' with dense_vector (dims={EMBEDDING_DIMENSION}).")
        return True
    return False

from datetime import datetime
from dateutil import parser as date_parser

def parse_iso_date(val: Any) -> Optional[str]:
    """Parse string/datetime into ISO-8601 string suitable for Elasticsearch date fields."""
    if not val:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, str):
        try:
            dt = date_parser.parse(val)
            return dt.isoformat()
        except Exception:
            return None
    return None

def prepare_document_for_es(article: Dict[str, Any]) -> Dict[str, Any]:
    """Formats MongoDB article document into clean Elasticsearch document schema."""
    pub_date = parse_iso_date(article.get("published_date"))
    created_at = parse_iso_date(article.get("created_at"))
    updated_at = parse_iso_date(article.get("updated_at"))

    doc = {
        "article_id": article.get("article_id") or str(article.get("_id")),
        "link": article.get("link", ""),
        "title": article.get("title", ""),
        "description": article.get("description", ""),
        "content": article.get("content", ""),
        "clean_content": article.get("clean_content") or article.get("cleaned_content", ""),
        "source": article.get("source") if isinstance(article.get("source"), dict) else {"name": str(article.get("source", ""))},
        "published_date": pub_date,
        "created_at": created_at,
        "updated_at": updated_at,
        "ingestion_type": article.get("ingestion_type", "realtime"),
        "keywords": article.get("keywords", []) if isinstance(article.get("keywords"), list) else [],
    }

    # Summary
    summary = article.get("summary")
    if isinstance(summary, str):
        doc["summary"] = {"text": summary}
    elif isinstance(summary, dict):
        doc["summary"] = summary
    else:
        doc["summary"] = {"text": ""}

    # Category
    category = article.get("category")
    if isinstance(category, dict):
        doc["category"] = category
    elif isinstance(category, str):
        doc["category"] = {"label": category, "score": 1.0}
    else:
        doc["category"] = {"label": "General", "score": 0.0}

    # Sentiment
    sentiment = article.get("sentiment")
    if isinstance(sentiment, dict):
        doc["sentiment"] = sentiment
    elif isinstance(sentiment, str):
        doc["sentiment"] = {"label": sentiment, "score": 1.0}
    else:
        doc["sentiment"] = {"label": "Neutral", "score": 0.0}

    # Entities
    entities = article.get("entities", [])
    if isinstance(entities, list):
        doc["entities"] = [e for e in entities if isinstance(e, dict)]

    # Embedding
    emb = article.get("embedding")
    if isinstance(emb, list) and len(emb) == EMBEDDING_DIMENSION:
        doc["embedding"] = emb
    elif isinstance(emb, dict) and isinstance(emb.get("vector"), list) and len(emb.get("vector")) == EMBEDDING_DIMENSION:
        doc["embedding"] = emb.get("vector")

    return doc

def index_article(article: Dict[str, Any], es: Optional[Elasticsearch] = None, index_name: str = ELASTICSEARCH_INDEX) -> bool:
    """Index a single enriched article into ES using article_id as _id."""
    if es is None:
        es = get_es_client()
    create_index_if_not_exists(es, index_name)

    article_id = article.get("article_id") or str(article.get("_id"))
    if not article_id:
        logger.error("Cannot index document missing article_id")
        return False

    doc = prepare_document_for_es(article)
    res = es.index(index=index_name, id=article_id, document=doc)
    return res.get("result") in ["created", "updated"]

def index_articles_bulk(articles: List[Dict[str, Any]], es: Optional[Elasticsearch] = None, index_name: str = ELASTICSEARCH_INDEX) -> Dict[str, int]:
    """Bulk index articles into Elasticsearch idempotently."""
    if es is None:
        es = get_es_client()
    create_index_if_not_exists(es, index_name)

    actions = []
    for art in articles:
        article_id = art.get("article_id") or str(art.get("_id"))
        if not article_id:
            continue
        doc = prepare_document_for_es(art)
        actions.append({
            "_op_type": "index",
            "_index": index_name,
            "_id": article_id,
            "_source": doc
        })

    if not actions:
        return {"indexed": 0, "failed": 0}

    success, failed = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)
    failed_count = len(failed) if isinstance(failed, list) else 0
    return {"indexed": success, "failed": failed_count}

def search_articles(query: str, size: int = 10, category: Optional[str] = None, es: Optional[Elasticsearch] = None, index_name: str = ELASTICSEARCH_INDEX) -> List[Dict[str, Any]]:
    """BM25 full-text keyword search across title, content, summary, and keywords."""
    if es is None:
        es = get_es_client()

    must_clause = [
        {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "clean_content", "summary.text^2", "keywords^2"]
            }
        }
    ]
    filter_clause = []
    if category:
        filter_clause.append({"term": {"category.label": category}})

    body = {
        "size": size,
        "query": {
            "bool": {
                "must": must_clause,
                "filter": filter_clause
            }
        }
    }
    res = es.search(index=index_name, body=body)
    results = []
    for hit in res["hits"]["hits"]:
        item = hit["_source"]
        item["_score"] = hit["_score"]
        results.append(item)
    return results

def search_similar_articles(query_vector: List[float], k: int = 10, es: Optional[Elasticsearch] = None, index_name: str = ELASTICSEARCH_INDEX) -> List[Dict[str, Any]]:
    """KNN dense vector similarity search using cosine distance."""
    if es is None:
        es = get_es_client()

    if len(query_vector) != EMBEDDING_DIMENSION:
        raise ValueError(f"Query vector dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {len(query_vector)}")

    body = {
        "knn": {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 100
        }
    }
    res = es.search(index=index_name, body=body)
    results = []
    for hit in res["hits"]["hits"]:
        item = hit["_source"]
        item["_score"] = hit["_score"]
        results.append(item)
    return results

def hybrid_search(query_text: str, query_vector: Optional[List[float]] = None, k: int = 10, es: Optional[Elasticsearch] = None, index_name: str = ELASTICSEARCH_INDEX) -> List[Dict[str, Any]]:
    """Combines BM25 keyword query and KNN vector similarity search."""
    if es is None:
        es = get_es_client()

    body = {
        "size": k,
        "query": {
            "multi_match": {
                "query": query_text,
                "fields": ["title^3", "clean_content", "summary.text^2", "keywords^2"]
            }
        }
    }
    if query_vector:
        if len(query_vector) != EMBEDDING_DIMENSION:
            raise ValueError(f"Query vector dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {len(query_vector)}")
        body["knn"] = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": k,
            "num_candidates": 100
        }

    res = es.search(index=index_name, body=body)
    results = []
    for hit in res["hits"]["hits"]:
        item = hit["_source"]
        item["_score"] = hit["_score"]
        results.append(item)
    return results
