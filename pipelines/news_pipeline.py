


"""
=========================================================
Realtime NLP Pipeline

Processes one realtime article from MongoDB.

Workflow

MongoDB
    ↓
Extract Content
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

Version : 4.0
=========================================================
"""

from datetime import datetime, UTC
from time import perf_counter

from bson import ObjectId
from pymongo import MongoClient

# =====================================================
# Historical Extractor
# =====================================================

from historical_crawlers.extractor import extract_article

# =====================================================
# NLP Modules
# =====================================================

from nlp.content_cleaner import clean_content
from nlp.summarizer import generate_summary
from nlp.sentiment import analyze_sentiment
from nlp.category_classifier import classify_category
from nlp.keyword_extractor import extract_keywords
from nlp.ner import extract_entities
from nlp.embeddings import generate_embedding

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

def load_article(article_id,collection):
    """
    Load article from MongoDB.
    """

    return collection.find_one(
        {
            "_id": ObjectId(article_id)
        }
    )

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
    """
    Updates processing information.
    Supports retries and detailed error tracking.
    """

    article = collection.find_one(
        {
            "_id": ObjectId(article_id)
        },
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

        "processing.completed":
            status == STATUS_COMPLETED,

        "processing.retry_count":
            retry_count,

        "processing.max_retry":
            MAX_RETRY,

        "processing.retryable":
            retryable,

        "processing.processed_at":
            now,

        "updated_at":
            now

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

        {

            "_id": ObjectId(article_id)

        },

        {

            "$set": update_data

        }

    )

# =====================================================
# Save NLP Results
# =====================================================

def save_results(article_id, data,collection):
    """
    Save NLP output into MongoDB.
    """

    collection.update_one(

        {
            "_id": ObjectId(article_id)
        },

        {
            "$set": data
        }

    )
# =====================================================
# Logging Helpers
# =====================================================

def print_section(title):

    print("\n" + "=" * 70)

    print(title)

    print("=" * 70)


def print_statistics(
    content,
    cleaned_content,
    summary,
    keywords,
    entities,
    embedding
):

    print_section("NLP Statistics")

    print(f"Original Content Length : {len(content)}")

    print(f"Cleaned Content Length  : {len(cleaned_content)}")

    print(f"Compression Ratio       : {len(cleaned_content)/len(content):.2f}")

    print(f"Summary Length          : {len(summary)}")

    print(f"Keywords                : {len(keywords)}")

    print(f"Entities                : {len(entities)}")

    print(f"Embedding Dimension     : {len(embedding)}")
# =====================================================
# Main Pipeline
# =====================================================


# =====================================================
# Pipeline Metrics
# =====================================================

def print_pipeline_metrics(start_time):

    elapsed = perf_counter() - start_time

    print_section("Pipeline Metrics")

    print(f"Execution Time : {elapsed:.2f} seconds")


def process_article(article_id,collection):

    print_section("Realtime NLP Pipeline")
    start_time = perf_counter()

    article = load_article(article_id,collection)

    if not article:

        print("❌ Article not found.")
        return False

    print(f"Title : {article.get('title')}")

    try:

        # =====================================================
        # Processing Started
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="pipeline_started"
        )

        # =====================================================
        # Extract Full Article
        # =====================================================

        print_section("Extracting Full Article")

        result = extract_article(article["link"])

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

        # =====================================================
        # Extracted Data
        # =====================================================

        title = result.get("title") or article.get("title", "")

        authors = result.get("authors", ["Unknown"])

        content = result.get("content", "")

        extraction_method = result.get("method", "Unknown")

        print("✅ Content extracted successfully")
        print(f"Content Length : {len(content)}")

        # =====================================================
        # Validate Extracted Content
        # =====================================================

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
                f"❌ Article content too short "
                f"({len(content)} characters)"
            )

            return False

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

        cleaned_content = clean_content(

            content,

            article.get("source", "")

        )

        print("✅ Content cleaned successfully")

        # =====================================================
        # Cleaned Content Preview
        # =====================================================

        print_section("Cleaned Content Preview")

        print(cleaned_content[:1000])

        print(f"\nOriginal Length : {len(content)}")

        print(f"Cleaned Length : {len(cleaned_content)}")

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
        # Generate Summary
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="summary_generation"
        )
        # =====================================================
        # Summary Generation
        # =====================================================

        print_section("Generating Summary")

        summary = generate_summary(cleaned_content)

        print("✅ Summary generated")

        print("\nSummary Preview\n")

        print(summary)

        # =====================================================
        # Sentiment Analysis
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="sentiment_analysis"
        )

        print_section("Sentiment Analysis")

        sentiment = analyze_sentiment(cleaned_content)

        print("✅ Sentiment completed")

        print(sentiment)

        # =====================================================
        # Category Classification
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="category_classification"
        )

        print_section("Category Classification")

        category = classify_category(

            title=title,

            content=cleaned_content

        )

        print("✅ Category predicted")

        print(category)

        # =====================================================
        # Keyword Extraction
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="keyword_extraction"
        )

        print_section("Keyword Extraction")

        keywords = extract_keywords(cleaned_content)

        print("✅ Keywords extracted")

        print(keywords)

        # =====================================================
        # Named Entity Recognition
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="named_entity_recognition"
        )

        print_section("Named Entity Recognition")

        entities = extract_entities(cleaned_content)

        print("✅ Entities extracted")

        print(entities)

        # =====================================================
        # Embedding Generation
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="embedding_generation"
        )

        print_section("Embedding Generation")

        embedding = generate_embedding(cleaned_content)

        print("✅ Embedding generated")

        # =====================================================
        # Statistics
        # =====================================================

        print_statistics(

            content,

            cleaned_content,

            summary,

            keywords,

            entities,

            embedding

        )

       
        # =====================================================
        # Saving Results To MongoDB
        # =====================================================

        update_processing_status(
            article_id=article_id,
            collection=collection,
            status=STATUS_PROCESSING,
            stage="saving_results"
        )

        print_section("Saving Results To MongoDB")

        save_results(

            article_id,

            {

                "title": title,

                "authors": authors,

                "content": content,

                "content_length": len(content),

                "cleaned_content": cleaned_content,

                "cleaned_content_length": len(cleaned_content),

                "summary": summary,

                "summary_length": len(summary),

                "sentiment": sentiment,

                "category": category,

                "keywords": keywords,

                "keyword_count": len(keywords),

                "entities": entities,

                "entity_count": len(entities),

                "embedding": embedding,

                "embedding_dimension": len(embedding),

                "extraction_method": extraction_method,

                "content_extracted": True,

                "nlp_completed": True,

                "processing_notes": "Realtime NLP pipeline completed successfully",
                "pipeline_version": "4.0",

                "processed_by": "Realtime NLP Pipeline",

                "processing_timestamp": datetime.now(UTC),

                "nlp_version": "1.0",

                "updated_at": datetime.now(UTC)

            },
            collection

        )

        # =====================================================
        # Processing Completed
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

        # =====================================================
        # Find Latest Pending Article
        # =====================================================

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

            print(f"Retry     : {article.get('processing', {}).get('retry_count', 0)}")

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

            print("No pending or retryable realtime articles found.")

    except KeyboardInterrupt:

        print("\nPipeline interrupted by user.")

    except Exception as e:

        print_section("UNEXPECTED ERROR")

        print(f"❌ {e}")

    finally:

        client.close()

        print("\nMongoDB Connection Closed.")
