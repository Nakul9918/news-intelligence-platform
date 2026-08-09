

"""
=========================================================
Realtime NLP Pipeline

Processes one article from MongoDB.

Supports

1. Realtime Articles
2. Historical Articles

Workflow

MongoDB
    ↓
Get Article Content
    ↓
Validate Content
    ↓
Clean Content
    ↓
Validate Cleaned Content
    ↓
Summary
    ↓
Sentiment
    ↓
Category
    ↓
Keywords
    ↓
NER
    ↓
Embedding
    ↓
Update MongoDB

Version : 5.0
=========================================================
"""

from datetime import datetime, UTC
from time import perf_counter

from bson import ObjectId
from pymongo import MongoClient

# =====================================================
# Article Extractor
# =====================================================

from historical_crawlers.extractor import extract_article

# =====================================================
# NLP Modules
# =====================================================

from nlp.content_cleaner import clean_content

try:
    from nlp.summarizer import generate_summary
except Exception:
    generate_summary = None

try:
    from nlp.sentiment import analyze_sentiment
except Exception:
    analyze_sentiment = None

try:
    from nlp.category_classifier import classify_article
except Exception:
    classify_article = None

try:
    from nlp.keyword_extractor import extract_keywords
except Exception:
    extract_keywords = None

try:
    from nlp.ner import extract_entities
except Exception:
    extract_entities = None

try:
    from nlp.embeddings import generate_embedding
except Exception:
    generate_embedding = None

# =====================================================
# MongoDB Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "news_db"

COLLECTION_NAME = "realtime_articles"

# =====================================================
# Validation Configuration
# =====================================================

MIN_ARTICLE_LENGTH = 300

MIN_CONTENT_LENGTH = 200

MAX_RETRY = 3

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]

# =====================================================
# Processing Status
# =====================================================

STATUS_PENDING = "PENDING"

STATUS_PROCESSING = "PROCESSING"

STATUS_COMPLETED = "COMPLETED"

STATUS_FAILED = "FAILED"

# =====================================================
# Load Article
# =====================================================
# =====================================================
# Load Article
# =====================================================

def load_article(article_id, collection):

    print_section("STEP 1 - LOAD ARTICLE")

    print(f"Collection : {collection.name}")
    print(f"Article ID : {article_id}")

    try:
        query = {"_id": ObjectId(article_id)} if (isinstance(article_id, str) and len(article_id) == 24 and ObjectId.is_valid(article_id)) else ({"_id": article_id} if isinstance(article_id, ObjectId) else {"article_id": article_id})

        article = collection.find_one(query)

        if article is None and "_id" not in query:
            article = collection.find_one({"link": article_id})

        if article is None:

            print("\n❌ Article NOT FOUND in MongoDB")
            return None

        print("\n✅ Article Found")

        print(f"MongoDB ID : {article['_id']}")

        print("\nAvailable Fields:")

        for key in sorted(article.keys()):
            print(f"  • {key}")

        print("\nField Check")
        print("-" * 50)

        print(f"Title Exists      : {'title' in article}")
        print(f"Content Exists    : {'content' in article}")
        print(f"Authors Exists    : {'authors' in article}")
        print(f"Link Exists       : {'link' in article}")
        print(f"Source Exists     : {'source' in article}")

        title = article.get("title")
        content = article.get("content")

        print(f"\nTitle             : {title}")

        print(
            f"Content Length    : {len(content) if isinstance(content, str) else 0}"
        )

        return article

    except Exception as e:

        print(f"\n❌ load_article() ERROR")

        print(type(e).__name__)

        print(e)

        return None

# =====================================================
# Logging
# =====================================================

def print_section(title):

    print("\n" + "=" * 70)

    print(title)

    print("=" * 70)


# =====================================================
# Pipeline Metrics
# =====================================================

def print_pipeline_metrics(start_time):

    elapsed = perf_counter() - start_time

    print_section("Pipeline Metrics")

    print(f"Execution Time : {elapsed:.2f} seconds")


# =====================================================
# Update Processing Status
# =====================================================

def update_processing_status(
    article_id,
    collection,
    status,
    stage="pipeline",
    error=None,
    retry=False
):

    query = {"_id": ObjectId(article_id)} if (isinstance(article_id, str) and len(article_id) == 24 and ObjectId.is_valid(article_id)) else ({"_id": article_id} if isinstance(article_id, ObjectId) else {"article_id": article_id})

    article = collection.find_one(
        query,
        {
            "processing": 1
        }
    )

    processing = article.get("processing", {}) if article else {}

    retry_count = processing.get("retry_count", 0)

    if retry:
        retry_count += 1

    retryable = (
        status == STATUS_FAILED
        and retry_count < MAX_RETRY
    )

    now = datetime.now(UTC)

    update_data = {

        "processing.status": status,

        "processing.stage": stage,

        "processing.completed": status == STATUS_COMPLETED,

        "processing.retry_count": retry_count,

        "processing.max_retry": MAX_RETRY,

        "processing.retryable": retryable,

        "processing.processed_at": now,

        "updated_at": now

    }

    if status == STATUS_PROCESSING:

        update_data["processing.started_at"] = now

    if status == STATUS_COMPLETED:

        update_data["processing.completed_at"] = now

        update_data["processing.error"] = None

        update_data["processing.retryable"] = False

    if status == STATUS_FAILED:

        update_data["processing.error"] = {

            "stage": stage,

            "message": str(error)

        }

    collection.update_one(

        get_mongo_query(article_id),

        {
            "$set": update_data
        }

    )


# =====================================================
# Save Results
# =====================================================

def save_results(article_id, data, collection):

    print("\nSAVE_RESULTS CALLED")

    print("Collection :", collection.name)

    print("Fields :", list(data.keys()))

    collection.update_one(

        get_mongo_query(article_id),

        {
            "$set": data
        }

    )


# =====================================================
# Pipeline Statistics
# =====================================================

def print_statistics(
    content,
    cleaned_content,
    summary,
    keywords,
    entities,
    embedding
):

    print_section("NLP Statistics")

    print(f"Original Length : {len(content)}")

    print(f"Cleaned Length  : {len(cleaned_content)}")

    print(f"Compression     : {len(cleaned_content)/len(content):.2f}")

    print(f"Summary Length  : {len(summary)}")

    print(f"Keywords        : {len(keywords)}")

    print(f"Entities        : {len(entities)}")

    print(f"Embedding Size  : {len(embedding)}")


# =====================================================
# NEW
def get_mongo_query(article_id):
    if isinstance(article_id, ObjectId):
        return {"_id": article_id}
    if isinstance(article_id, str) and len(article_id) == 24 and ObjectId.is_valid(article_id):
        return {"$or": [{"_id": ObjectId(article_id)}, {"article_id": article_id}]}
    return {"$or": [{"article_id": article_id}, {"link": article_id}]}

def get_article_content(article, collection):

    """
    Historical / Stored
    -------------------
    Uses existing MongoDB content if valid and >= MIN_ARTICLE_LENGTH.

    Realtime Extraction
    -------------------
    Downloads article using 3-stage fallback extractor if content is missing or short.
    """

    print_section("Getting Article Content")

    content = article.get("content", "").strip()
    title = article.get("title", "").strip()

    # ------------------------------------------
    # Stored Content (Idempotent Reuse)
    # ------------------------------------------

    if content and len(content) >= MIN_ARTICLE_LENGTH and title:

        print("✅ Using stored MongoDB content")

        print(f"Content Length : {len(content)}")

        return {

            "title": title,

            "authors": article.get("authors", ["Unknown"]),

            "content": content,

            "method": article.get(
                "extraction_method",
                "MongoDB"
            )

        }

    # ------------------------------------------
    # Realtime Extraction Fallback
    # ------------------------------------------

    print("⚠️ Valid stored content not found")

    print("Extracting article from URL:", article.get("link"))

    link = article.get("link")
    if not link:
        return None

    result = extract_article(link)

    if result is None or not result.get("content") or len(result.get("content").strip()) < MIN_ARTICLE_LENGTH:
        desc = article.get("description", "") or article.get("summary", "") or ""
        fallback_text = (title + ". " + str(desc)).strip()
        if len(fallback_text) >= 10:
            print("✅ Using Title & Description fallback for NLP enrichment")
            return {
                "title": title or "Untitled Article",
                "authors": article.get("authors", ["Unknown"]),
                "content": fallback_text,
                "method": "TitleDescriptionFallback"
            }
        return None

    extracted_content = result.get("content").strip()
    extracted_title = result.get("title") or title

    collection.update_one(
        get_mongo_query(article["_id"]),
        {
            "$set": {

                "title": extracted_title,

                "authors": result.get("authors", ["Unknown"]),

                "content": extracted_content,

                "content_length": len(extracted_content),

                "content_extracted": True,

                "extraction_method": result.get("method"),

                "last_pipeline_stage": "extraction"

            }

        }

    )

    print("✅ Article extracted successfully")

    print(f"Content Length : {len(extracted_content)}")

    return result

# =====================================================
# Phase 7 & 8 Standalone Worker: Extraction + Cleaning
# =====================================================

def extract_and_clean_article(article_id, collection):
    """
    Executes Phase 7 (Extraction) & Phase 8 (Cleaning) without heavy NLP models.
    """
    start_time = perf_counter()
    article = load_article(article_id, collection)
    if not article:
        return {"success": False, "error": "Article not found"}

    source_obj = article.get("source")
    src_name = source_obj if isinstance(source_obj, str) else (source_obj.get("name", "") if isinstance(source_obj, dict) else "")

    # Phase 7: Extract
    ext_start = perf_counter()
    res = get_article_content(article, collection)
    ext_time = perf_counter() - ext_start

    if not res:
        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_FAILED,
            stage="content_extraction",
            error="Content extraction failed or too short (< 300 chars)",
            retry=True
        )
        return {"success": False, "error": "Extraction failed", "extraction_time": ext_time, "cleaning_time": 0}

    raw_content = res.get("content", "")
    title = res.get("title", article.get("title", ""))
    method = res.get("method", "Unknown")

    # Phase 8: Clean
    clean_start = perf_counter()
    cleaned = clean_content(raw_content, src_name)
    clean_time = perf_counter() - clean_start

    if not cleaned or len(cleaned.strip()) < MIN_CONTENT_LENGTH:
        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_FAILED,
            stage="content_cleaning",
            error=f"Cleaned content too short ({len(cleaned)} chars)",
            retry=True
        )
        return {"success": False, "error": "Cleaning failed (< 200 chars)", "extraction_time": ext_time, "cleaning_time": clean_time}

    # Save Cleaned Content & Update Status
    now = datetime.now(UTC)
    collection.update_one(
        get_mongo_query(article_id),
        {
            "$set": {
                "title": title,
                "content": raw_content,
                "clean_content": cleaned,
                "clean_content_length": len(cleaned),
                "extraction_method": method,
                "last_pipeline_stage": "cleaning",
                "status.content_extracted": True,
                "status.content_cleaned": True,
                "updated_at": now
            }
        }
    )

    update_processing_status(
        article_id=article_id,
        collection=collection,
        status="CLEANED",
        stage="cleaning"
    )

    total_time = perf_counter() - start_time
    return {
        "success": True,
        "title": title,
        "content_length": len(raw_content),
        "clean_content_length": len(cleaned),
        "method": method,
        "extraction_time": ext_time,
        "cleaning_time": clean_time,
        "total_time": total_time
    }
# =====================================================
# Main Pipeline
# =====================================================

def process_article(article_id, collection):

    print_section("Realtime NLP Pipeline")

    start_time = perf_counter()

    article = load_article(article_id, collection)

    # =====================================================
    # Debug Information
    # =====================================================

    print("\n" + "=" * 70)
    print("DEBUG INFORMATION")
    print("=" * 70)
    print(f"Collection Name : {collection.name}")
    print(f"Article ID      : {article_id}")

    if article:

        print(f"MongoDB _id     : {article['_id']}")
        print(f"Title           : {article.get('title')}")

    print("=" * 70)

    if not article:

        print("❌ Article not found.")

        return False

    print(f"Title : {article.get('title')}")

    try:

        # =====================================================
        # Pipeline Started
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="pipeline_started"
        )

        # =====================================================
        # Get Article Content
        # =====================================================

        result = get_article_content(article, collection)

        if result is None:

            update_processing_status(
                article_id=article_id,
                collection=collection,
                status=STATUS_FAILED,
                stage="content_extraction",
                error="Content extraction failed",
                retry=True
            )

            print("❌ Content extraction failed.")

            return False

        title = result.get("title") or article.get("title", "")

        authors = result.get("authors", ["Unknown"])

        content = result.get("content", "")

        extraction_method = result.get("method", "Unknown")

        # =====================================================
        # Validate Content
        # =====================================================

        print_section("Validating Content")

        if not content.strip():

            update_processing_status(
                article_id=article_id,
                collection=collection,
                status=STATUS_FAILED,
                stage="content_validation",
                error="Article content is empty",
                retry=True
            )

            print("❌ Article content is empty.")

            return False

        if len(content.strip()) < MIN_ARTICLE_LENGTH:

            update_processing_status(
                article_id=article_id,
                collection=collection,
                status=STATUS_FAILED,
                stage="content_validation",
                error=f"Article content too short ({len(content)} characters)",
                retry=True
            )

            print(
                f"❌ Article content too short ({len(content)} characters)"
            )

            return False

        print("✅ Content validation passed")
        # =====================================================
        # Content Cleaning
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="content_cleaning"
        )

        print_section("Cleaning Content")

        source_val = article.get("source")
        src_name = source_val.get("name") if isinstance(source_val, dict) else str(source_val or "")

        cleaned_content = clean_content(
            content,
            src_name
        )

        print("✅ Content cleaned successfully")

        # =====================================================
        # Cleaned Content Preview
        # =====================================================

        print_section("Cleaned Content Preview")

        print(repr(cleaned_content[:1000]))

        print(f"\nOriginal Length : {len(content)}")

        print(f"Cleaned Length  : {len(cleaned_content)}")

        # =====================================================
        # Validate Cleaned Content
        # =====================================================

        if not cleaned_content.strip():

            update_processing_status(
                article_id=article_id,
                collection=collection,
                status=STATUS_FAILED,
                stage="clean_content_validation",
                error="Cleaned content is empty after preprocessing",
                retry=True
            )

            print("\n❌ Cleaned content is empty.")

            print("Skipping NLP pipeline.")

            return False

        if len(cleaned_content.strip()) < MIN_CONTENT_LENGTH:

            update_processing_status(
                article_id=article_id,
                collection=collection,
                status=STATUS_FAILED,
                stage="clean_content_validation",
                error=f"Cleaned content too short ({len(cleaned_content)} characters)",
                retry=True
            )

            print(
                f"\n❌ Cleaned content too short "
                f"({len(cleaned_content)} characters)"
            )

            print("Skipping NLP pipeline.")

            return False

        print("✅ Cleaned content validation passed")
        # =====================================================
        # Summary Generation
        # =====================================================
        t_sum = perf_counter()
        existing_summary = article.get("summary")
        if isinstance(existing_summary, dict) and existing_summary.get("text"):
            summary = existing_summary.get("text")
        elif isinstance(existing_summary, str) and existing_summary:
            summary = existing_summary
        elif generate_summary:
            try:
                update_processing_status(article_id=article_id, collection=collection, status=STATUS_PROCESSING, stage="summary_generation")
                print_section("Generating Summary")
                summary = generate_summary(cleaned_content)
                print("✅ Summary generated")
            except Exception as e:
                logger.error(f"Summary generation error: {e}")
                summary = ""
        else:
            summary = ""
        summary_time = round(perf_counter() - t_sum, 4)

        # =====================================================
        # Sentiment Analysis
        # =====================================================
        t_sent = perf_counter()
        existing_sentiment = article.get("sentiment")
        if isinstance(existing_sentiment, dict) and existing_sentiment.get("label"):
            sentiment = existing_sentiment
        elif analyze_sentiment:
            try:
                update_processing_status(article_id=article_id, collection=collection, status=STATUS_PROCESSING, stage="sentiment_analysis")
                print_section("Sentiment Analysis")
                sentiment = analyze_sentiment(cleaned_content)
                print("✅ Sentiment completed:", sentiment)
            except Exception as e:
                logger.error(f"Sentiment analysis error: {e}")
                sentiment = {"label": "Neutral", "score": 0.0, "model": "fallback"}
        else:
            sentiment = {"label": "Neutral", "score": 0.0, "model": "fallback"}
        sentiment_time = round(perf_counter() - t_sent, 4)

        # =====================================================
        # Category Classification
        # =====================================================
        t_cat = perf_counter()
        existing_category = article.get("category")
        if isinstance(existing_category, dict) and existing_category.get("label"):
            category = existing_category
        elif classify_article:
            try:
                update_processing_status(article_id=article_id, collection=collection, status=STATUS_PROCESSING, stage="category_classification")
                print_section("Category Classification")
                classification_text = f"{title}\n\n{cleaned_content}"
                category = classify_article(text=classification_text)
                print("✅ Category predicted:", category)
            except Exception as e:
                logger.error(f"Category classification error: {e}")
                category = {"label": "General", "score": 0.0, "model": "fallback"}
        else:
            category = {"label": "General", "score": 0.0, "model": "fallback"}
        category_time = round(perf_counter() - t_cat, 4)

        # =====================================================
        # Keyword Extraction
        # =====================================================
        t_key = perf_counter()
        existing_keywords = article.get("keywords")
        if isinstance(existing_keywords, list) and len(existing_keywords) > 0:
            keywords = existing_keywords
        elif extract_keywords:
            try:
                update_processing_status(article_id=article_id, collection=collection, status=STATUS_PROCESSING, stage="keyword_extraction")
                print_section("Keyword Extraction")
                keywords = extract_keywords(cleaned_content)
                print("✅ Keywords extracted:", len(keywords))
            except Exception as e:
                logger.error(f"Keyword extraction error: {e}")
                keywords = []
        else:
            keywords = []
        keyword_time = round(perf_counter() - t_key, 4)

        # =====================================================
        # Named Entity Recognition
        # =====================================================
        t_ner = perf_counter()
        existing_entities = article.get("entities")
        if isinstance(existing_entities, list) and len(existing_entities) > 0:
            entities = existing_entities
        elif extract_entities:
            try:
                update_processing_status(article_id=article_id, collection=collection, status=STATUS_PROCESSING, stage="named_entity_recognition")
                print_section("Named Entity Recognition")
                entities = extract_entities(cleaned_content)
                print("✅ Entities extracted:", len(entities))
            except Exception as e:
                logger.error(f"NER error: {e}")
                entities = []
        else:
            entities = []
        ner_time = round(perf_counter() - t_ner, 4)

        # =====================================================
        # Embedding Generation
        # =====================================================
        t_emb = perf_counter()
        existing_emb = article.get("embedding")
        if isinstance(existing_emb, list) and len(existing_emb) > 0:
            embedding = existing_emb
        elif isinstance(existing_emb, dict) and isinstance(existing_emb.get("vector"), list) and len(existing_emb.get("vector")) > 0:
            embedding = existing_emb.get("vector")
        elif generate_embedding:
            try:
                update_processing_status(article_id=article_id, collection=collection, status=STATUS_PROCESSING, stage="embedding_generation")
                print_section("Embedding Generation")
                embedding = generate_embedding(cleaned_content)
                print("✅ Embedding generated:", len(embedding) if isinstance(embedding, list) else 0)
            except Exception as e:
                logger.error(f"Embedding generation error: {e}")
                embedding = []
        else:
            embedding = []
        embedding_time = round(perf_counter() - t_emb, 4)

        total_time = round(perf_counter() - start_time, 4)

        # =====================================================
        # Pipeline Statistics & Saving Results
        # =====================================================
        print_statistics(
            content,
            cleaned_content,
            summary if isinstance(summary, str) else str(summary),
            keywords,
            entities,
            embedding if isinstance(embedding, list) else []
        )

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="saving_results"
        )

        print_section("Saving Results")

        save_results(
            article_id,
            {
                "title": title,
                "authors": authors,
                "content": content,
                "content_length": len(content),
                "clean_content": cleaned_content,
                "cleaned_content": cleaned_content,
                "cleaned_content_length": len(cleaned_content),
                "summary": summary,
                "summary_length": len(summary) if isinstance(summary, str) else 0,
                "sentiment": sentiment,
                "category": category,
                "keywords": keywords,
                "keyword_count": len(keywords),
                "entities": entities,
                "entity_count": len(entities),
                "embedding": embedding,
                "embedding_dimension": len(embedding) if isinstance(embedding, list) else 0,
                "extraction_method": extraction_method,
                "content_extracted": True,
                "nlp_completed": True,
                "status.nlp_completed": True,
                "processing.summary_time": summary_time,
                "processing.sentiment_time": sentiment_time,
                "processing.category_time": category_time,
                "processing.keyword_time": keyword_time,
                "processing.ner_time": ner_time,
                "processing.embedding_time": embedding_time,
                "processing.total_time": total_time,
                "pipeline_version": "5.0",
                "processed_by": "Realtime NLP Pipeline",
                "processing_notes": "Pipeline completed successfully",
                "processing_timestamp": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            },
            collection
        )

        # =====================================================
        # Pipeline Completed
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_COMPLETED,
            stage="completed"
        )

        print_pipeline_metrics(start_time)

        print_section("Pipeline Completed Successfully")

        print("✅ Article processed successfully.")

        return True

    except Exception as e:

        print_section("Pipeline Error")

        print(f"❌ {e}")

        print_pipeline_metrics(start_time)

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_FAILED,
            stage="pipeline_exception",
            error=str(e),
            retry=True
        )

        return False
# =====================================================
# Test Pipeline
# =====================================================

if __name__ == "__main__":

    print_section("Realtime NLP Pipeline Test")

    try:

        article = collection.find_one(

            {

                "$or": [

                    {

                        "processing.status": STATUS_PENDING

                    },

                    {

                        "processing.status": STATUS_FAILED,

                        "processing.retryable": True

                    }

                ]

            },

            sort=[("created_at", -1)]

        )

        if article:

            print("\nArticle Selected")

            print("-" * 60)

            print(f"ID        : {article['_id']}")

            print(f"Title     : {article.get('title')}")

            print(f"Source    : {article.get('source')}")

            print(
                f"Retry     : "
                f"{article.get('processing', {}).get('retry_count', 0)}"
            )

            print("-" * 60)

            success = process_article(

                str(article["_id"]),

                collection

            )

            print_section("TEST RESULT")

            if success:

                print("✅ Pipeline executed successfully.")

            else:

                print("❌ Pipeline execution failed.")

        else:

            print_section("NO ARTICLES FOUND")

            print("No pending or retryable articles found.")

    except KeyboardInterrupt:

        print("\nPipeline interrupted by user.")

    except Exception as e:

        print_section("UNEXPECTED ERROR")

        print(f"❌ {e}")

    finally:

        client.close()

        print("\nMongoDB Connection Closed.")