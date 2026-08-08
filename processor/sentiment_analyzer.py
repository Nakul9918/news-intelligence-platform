

# """
# Sentiment Analyzer

# MongoDB
#     ↓
# Find Cleaned Articles
#     ↓
# Validate Content
#     ↓
# Analyze Sentiment
#     ↓
# Update MongoDB
# """

# from datetime import datetime, UTC

# from pymongo import MongoClient
# from transformers import pipeline

# from config import (
#     MONGO_URI,
#     DATABASE_NAME,
#     REALTIME_COLLECTION_NAME,
# )

# # =====================================================
# # MongoDB
# # =====================================================

# client = MongoClient(

#     MONGO_URI,

#     maxPoolSize=20,

#     serverSelectionTimeoutMS=5000

# )

# db = client[DATABASE_NAME]

# collection = db[REALTIME_COLLECTION_NAME]

# # =====================================================
# # Load Sentiment Model
# # =====================================================

# MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# print("=" * 70)
# print("Loading Sentiment Model...")
# print("=" * 70)

# sentiment_pipeline = pipeline(

#     "sentiment-analysis",

#     model=MODEL_NAME

# )

# print("Sentiment Model Loaded Successfully")
# print("=" * 70)


# # =====================================================
# # Get Pending Article
# # =====================================================

# def get_pending_article():

#     return collection.find_one(

#         {
#             "status.content_cleaned": True,
#             "status.sentiment_done": False,
#             "status.sentiment_failed": False
#         },

#         {
#             "_id": 1,
#             "title": 1,
#             "link": 1,
#             "clean_content": 1,
#             "processing": 1,
#             "fetched_at": 1
#         },

#         sort=[
#             ("fetched_at", 1)
#         ]

#     )


# # =====================================================
# # Validate Content
# # =====================================================

# def validate_content(text):

#     if text is None:
#         return False

#     text = text.strip()

#     if len(text) < MIN_CONTENT_LENGTH:
#         return False

#     return True


# # =====================================================
# # Split Long Text
# # =====================================================

# def split_text(text):

#     words = text.split()

#     chunks = []

#     current_chunk = []

#     current_length = 0

#     for word in words:

#         if current_length + len(word) + 1 <= MAX_CHUNK_LENGTH:

#             current_chunk.append(word)

#             current_length += len(word) + 1

#         else:

#             chunks.append(
#                 " ".join(current_chunk)
#             )

#             current_chunk = [word]

#             current_length = len(word)

#     if current_chunk:

#         chunks.append(
#             " ".join(current_chunk)
#         )

#     return chunks


# # =====================================================
# # Analyze Sentiment
# # =====================================================

# def analyze_sentiment(text):

#     chunks = split_text(text)

#     if len(chunks) == 0:

#         return {

#             "label": "Neutral",

#             "score": 0.0,

#             "model": MODEL_NAME,

#             "chunks": 0

#         }

#     positive = 0.0

#     neutral = 0.0

#     negative = 0.0

#     chunk_scores = []

#     # ----------------------------------------
#     # Analyze Every Chunk
#     # ----------------------------------------

#     for chunk in chunks:

#         result = sentiment_pipeline(chunk)[0]

#         label = result["label"].lower()

#         score = float(result["score"])

#         chunk_scores.append(score)

#         if label == "positive":

#             positive += score

#         elif label == "neutral":

#             neutral += score

#         elif label == "negative":

#             negative += score

#     # ----------------------------------------
#     # Final Label
#     # ----------------------------------------

#     scores = {

#         "Positive": positive,

#         "Neutral": neutral,

#         "Negative": negative

#     }

#     final_label = max(
#         scores,
#         key=scores.get
#     )

#     average_score = round(

#         sum(chunk_scores) / len(chunk_scores),

#         4

#     )

#     return {

#         "label": final_label,

#         "score": average_score,

#         "model": MODEL_NAME,

#         "chunks": len(chunks)

#     }
# # =====================================================
# # Configuration
# # =====================================================

# MAX_CHUNK_LENGTH = 450

# SENTIMENT_MAP = {

#     "positive": "Positive",

#     "negative": "Negative",

#     "neutral": "Neutral",

# }

# # =====================================================
# # Get Pending Article
# # =====================================================

# def get_pending_article():

#     return collection.find_one(

#         {

#             "status.content_cleaned": True,

#             "status.sentiment_done": False

#         }

#     )

# # =====================================================
# # Validate Content
# # =====================================================

# def validate_content(text):

#     if not text:

#         return False

#     if len(text.strip()) < 100:

#         return False

#     return True
# # =====================================================
# # Split Text into Chunks
# # =====================================================

# def split_text(text):

#     chunks = []

#     # ----------------------------------------
#     # Split by Paragraph
#     # ----------------------------------------

#     paragraphs = [

#         paragraph.strip()

#         for paragraph in text.split("\n")

#         if paragraph.strip()

#     ]

#     # ----------------------------------------
#     # Process Each Paragraph
#     # ----------------------------------------

#     for paragraph in paragraphs:

#         # Small paragraph

#         if len(paragraph) <= MAX_CHUNK_LENGTH:

#             chunks.append(

#                 paragraph

#             )

#             continue

#         # Large paragraph

#         words = paragraph.split()

#         current_chunk = ""

#         for word in words:

#             if len(current_chunk) + len(word) + 1 <= MAX_CHUNK_LENGTH:

#                 current_chunk += " " + word

#             else:

#                 chunks.append(

#                     current_chunk.strip()

#                 )

#                 current_chunk = word

#         if current_chunk:

#             chunks.append(

#                 current_chunk.strip()

#             )

#     return chunks
# # =====================================================
# # Analyze Sentiment
# # =====================================================

# def analyze_sentiment(text):

#     chunks = split_text(text)

#     if not chunks:

#         return {

#             "label": "Unknown",

#             "score": 0.0

#         }

#     sentiment_scores = {

#         "Positive": [],

#         "Negative": [],

#         "Neutral": []

#     }

#     # ----------------------------------------
#     # Analyze Each Chunk
#     # ----------------------------------------

#     for chunk in chunks:

#         result = sentiment_pipeline(

#             chunk

#         )[0]

#         label = SENTIMENT_MAP.get(

#             result["label"].lower(),

#             result["label"].capitalize()

#         )

#         score = float(

#             result["score"]

#         )

#         sentiment_scores[

#             label

#         ].append(

#             score

#         )

#     # ----------------------------------------
#     # Average Scores
#     # ----------------------------------------

#     average_scores = {}

#     for label, values in sentiment_scores.items():

#         if values:

#             average_scores[label] = sum(values) / len(values)

#         else:

#             average_scores[label] = 0.0

#     # ----------------------------------------
#     # Final Label
#     # ----------------------------------------

#     final_label = max(

#         average_scores,

#         key=average_scores.get

#     )

#     final_score = round(

#         average_scores[final_label],

#         4

#     )

#     return {

#         "label": final_label,

#         "score": final_score

#     }

# # =====================================================
# # Update MongoDB
# # =====================================================

# def update_article(

#     article_id,

#     sentiment,

#     processing_time

# ):

#     result = collection.update_one(

#         {

#             "_id": article_id

#         },

#         {

#             "$set": {

#                 "sentiment": sentiment["label"],

#                 "sentiment_score": sentiment["score"],

#                 "sentiment_model": MODEL_NAME,

#                 "status.sentiment_done": True,

#                 "processing.sentiment_time": round(

#                     processing_time,

#                     3

#                 ),

#                 "updated_at": datetime.now(UTC),

#                 "error": None

#             }

#         }

#     )

#     print()

#     print("=" * 70)

#     print("MongoDB Updated")

#     print("=" * 70)

#     print(f"Matched  : {result.matched_count}")

#     print(f"Modified : {result.modified_count}")

#     print("=" * 70)

# # =====================================================
# # Main
# # =====================================================

# def main():

#     started = datetime.now(UTC)

#     article = get_pending_article()

#     if article is None:

#         print("=" * 70)

#         print("No Pending Articles")

#         print("=" * 70)

#         return

#     print("=" * 70)

#     print("Analyzing Sentiment")

#     print(article["link"])

#     print("=" * 70)

#     try:

#         # ----------------------------------------
#         # Validate Content
#         # ----------------------------------------

#         if not validate_content(

#             article["clean_content"]

#         ):

#             print("Invalid Clean Content")

#             return

#         # ----------------------------------------
#         # Analyze Sentiment
#         # ----------------------------------------

#         sentiment = analyze_sentiment(

#             article["clean_content"]

#         )

#         duration = (

#             datetime.now(UTC) - started

#         ).total_seconds()

#         # ----------------------------------------
#         # Update MongoDB
#         # ----------------------------------------

#         update_article(

#             article["_id"],

#             sentiment,

#             duration

#         )

#         # ----------------------------------------
#         # Summary
#         # ----------------------------------------

#         print()

#         print("=" * 70)

#         print("Sentiment Summary")

#         print("=" * 70)

#         print(

#             f"Label           : {sentiment['label']}"

#         )

#         print(

#             f"Confidence      : {sentiment['score']}"

#         )

#         print(

#             f"Processing Time : {duration:.2f} sec"

#         )

#         print("=" * 70)

#     except Exception as e:

#         print()

#         print("=" * 70)

#         print("Sentiment Analysis Failed")

#         print("=" * 70)

#         print(f"Article : {article['link']}")

#         print(f"Reason  : {e}")

#         print("=" * 70)

#         collection.update_one(

#             {

#                 "_id": article["_id"]

#             },

#             {

#                 "$set": {

#                     "error": str(e),

#                     "updated_at": datetime.now(UTC)

#                 }

#             }

#         )

# # =====================================================
# # Main
# # =====================================================

# if __name__ == "__main__":

#     main()

# # =====================================================
# # Split Text into Chunks
# # =====================================================

# def split_text(text):

#     chunks = []

#     # ----------------------------------------
#     # Split by Paragraph
#     # ----------------------------------------

#     paragraphs = [

#         paragraph.strip()

#         for paragraph in text.split("\n")

#         if paragraph.strip()

#     ]

#     # ----------------------------------------
#     # Build Chunks
#     # ----------------------------------------

#     current_chunk = ""

#     for paragraph in paragraphs:

#         # Small paragraph
#         if len(paragraph) <= MAX_CHUNK_LENGTH:

#             if len(current_chunk) + len(paragraph) <= MAX_CHUNK_LENGTH:

#                 current_chunk += "\n" + paragraph

#             else:

#                 if current_chunk:

#                     chunks.append(

#                         current_chunk.strip()

#                     )

#                 current_chunk = paragraph

#             continue

#         # ----------------------------------------
#         # Large Paragraph
#         # ----------------------------------------

#         words = paragraph.split()

#         for word in words:

#             if len(current_chunk) + len(word) + 1 <= MAX_CHUNK_LENGTH:

#                 current_chunk += " " + word

#             else:

#                 chunks.append(

#                     current_chunk.strip()

#                 )

#                 current_chunk = word

#     if current_chunk:

#         chunks.append(

#             current_chunk.strip()

#         )

#     return chunks


# # =====================================================
# # Analyze Sentiment
# # =====================================================

# def analyze_sentiment(text):

#     chunks = split_text(

#         text

#     )

#     if not chunks:

#         return {

#             "label": "Unknown",

#             "score": 0.0,

#             "model": MODEL_NAME,

#             "chunks": 0

#         }

#     # ----------------------------------------
#     # Store Scores
#     # ----------------------------------------

#     sentiment_scores = {

#         "Positive": [],

#         "Negative": [],

#         "Neutral": []

#     }

#     # ----------------------------------------
#     # Analyze Every Chunk
#     # ----------------------------------------

#     for chunk in chunks:

#         result = sentiment_pipeline(

#             chunk

#         )[0]

#         label = SENTIMENT_MAP.get(

#             result["label"].lower(),

#             result["label"].capitalize()

#         )

#         score = float(

#             result["score"]

#         )

#         sentiment_scores[label].append(

#             score

#         )

#     # ----------------------------------------
#     # Average Scores
#     # ----------------------------------------

#     average_scores = {}

#     for label, values in sentiment_scores.items():

#         if values:

#             average_scores[label] = round(

#                 sum(values) / len(values),

#                 4

#             )

#         else:

#             average_scores[label] = 0.0

#     # ----------------------------------------
#     # Final Sentiment
#     # ----------------------------------------

#     final_label = max(

#         average_scores,

#         key=average_scores.get

#     )

#     return {

#         "label": final_label,

#         "score": average_scores[final_label],

#         "model": MODEL_NAME,

#         "chunks": len(chunks)

#     }
# # =====================================================
# # Split Text into Chunks
# # =====================================================

# def split_text(text):

#     chunks = []

#     # ----------------------------------------
#     # Split by Paragraph
#     # ----------------------------------------

#     paragraphs = [

#         paragraph.strip()

#         for paragraph in text.split("\n")

#         if paragraph.strip()

#     ]

#     # ----------------------------------------
#     # Build Chunks
#     # ----------------------------------------

#     current_chunk = ""

#     for paragraph in paragraphs:

#         # Small paragraph
#         if len(paragraph) <= MAX_CHUNK_LENGTH:

#             if len(current_chunk) + len(paragraph) <= MAX_CHUNK_LENGTH:

#                 current_chunk += "\n" + paragraph

#             else:

#                 if current_chunk:

#                     chunks.append(

#                         current_chunk.strip()

#                     )

#                 current_chunk = paragraph

#             continue

#         # ----------------------------------------
#         # Large Paragraph
#         # ----------------------------------------

#         words = paragraph.split()

#         for word in words:

#             if len(current_chunk) + len(word) + 1 <= MAX_CHUNK_LENGTH:

#                 current_chunk += " " + word

#             else:

#                 chunks.append(

#                     current_chunk.strip()

#                 )

#                 current_chunk = word

#     if current_chunk:

#         chunks.append(

#             current_chunk.strip()

#         )

#     return chunks


# # =====================================================
# # Analyze Sentiment
# # =====================================================

# def analyze_sentiment(text):

#     chunks = split_text(

#         text

#     )

#     if not chunks:

#         return {

#             "label": "Unknown",

#             "score": 0.0,

#             "model": MODEL_NAME,

#             "chunks": 0

#         }

#     # ----------------------------------------
#     # Store Scores
#     # ----------------------------------------

#     sentiment_scores = {

#         "Positive": [],

#         "Negative": [],

#         "Neutral": []

#     }

#     # ----------------------------------------
#     # Analyze Every Chunk
#     # ----------------------------------------

#     for chunk in chunks:

#         result = sentiment_pipeline(

#             chunk

#         )[0]

#         label = SENTIMENT_MAP.get(

#             result["label"].lower(),

#             result["label"].capitalize()

#         )

#         score = float(

#             result["score"]

#         )

#         sentiment_scores[label].append(

#             score

#         )

#     # ----------------------------------------
#     # Average Scores
#     # ----------------------------------------

#     average_scores = {}

#     for label, values in sentiment_scores.items():

#         if values:

#             average_scores[label] = round(

#                 sum(values) / len(values),

#                 4

#             )

#         else:

#             average_scores[label] = 0.0

#     # ----------------------------------------
#     # Final Sentiment
#     # ----------------------------------------

#     final_label = max(

#         average_scores,

#         key=average_scores.get

#     )

#     return {

#         "label": final_label,

#         "score": average_scores[final_label],

#         "model": MODEL_NAME,

#         "chunks": len(chunks)

#     }
# # =====================================================
# # Main
# # =====================================================

# def main():

#     processed = 0

#     failed = 0

#     while True:

#         started = datetime.now(UTC)

#         article = get_pending_article()

#         if article is None:

#             print("=" * 70)
#             print("No Pending Articles")
#             print("=" * 70)
#             print()

#             print("=" * 70)
#             print("Sentiment Analysis Summary")
#             print("=" * 70)
#             print(f"Processed : {processed}")
#             print(f"Failed    : {failed}")
#             print(f"Success   : {processed}")
#             print("=" * 70)

#             break

#         print("=" * 70)
#         print("Sentiment Analysis")
#         print(f"Title : {article.get('title', '')}")
#         print(f"URL   : {article['link']}")
#         print("=" * 70)

#         try:

#             # ----------------------------------------
#             # Validate Content
#             # ----------------------------------------

#             text = article.get(

#                 "clean_content",

#                 ""

#             )

#             if not validate_content(text):

#                 failed += 1

#                 print("Invalid Clean Content")

#                 mark_sentiment_failed(

#                     article["_id"],

#                     "Invalid clean content"

#                 )

#                 continue

#             # ----------------------------------------
#             # Analyze Sentiment
#             # ----------------------------------------

#             sentiment = analyze_sentiment(

#                 text

#             )

#             # ----------------------------------------
#             # Processing Time
#             # ----------------------------------------

#             duration = (

#                 datetime.now(UTC)

#                 - started

#             ).total_seconds()

#             # ----------------------------------------
#             # Update MongoDB
#             # ----------------------------------------

#             update_article(

#                 article,

#                 sentiment,

#                 duration

#             )

#             processed += 1

#             # ----------------------------------------
#             # Summary
#             # ----------------------------------------

#             print()

#             print("=" * 70)
#             print("Sentiment Result")
#             print("=" * 70)

#             print(

#                 f"Sentiment       : {sentiment['label']}"

#             )

#             print(

#                 f"Confidence      : {sentiment['score']:.4f}"

#             )

#             print(

#                 f"Model           : {sentiment['model']}"

#             )

#             print(

#                 f"Chunks          : {sentiment['chunks']}"

#             )

#             print(

#                 f"Processing Time : {duration:.2f} sec"

#             )

#             print("=" * 70)

#         except Exception as e:

#             traceback.print_exc()

#             failed += 1

#             print()

#             print("=" * 70)
#             print("Sentiment Analysis Failed")
#             print("=" * 70)

#             print(e)

#             mark_sentiment_failed(

#                 article["_id"],

#                 str(e)

#             )

#             continue


# # =====================================================
# # Main
# # =====================================================

# if __name__ == "__main__":

#     main()


"""
Sentiment Analysis Service

MongoDB
    ↓
Find Cleaned Articles
    ↓
Validate Content
    ↓
Split Long Articles
    ↓
Analyze Sentiment
    ↓
Update MongoDB
"""

import traceback
from datetime import datetime, UTC

from pymongo import MongoClient
from transformers import pipeline

from config import (
    MONGO_URI,
    DATABASE_NAME,
    REALTIME_COLLECTION_NAME,
)

# =====================================================
# MongoDB
# =====================================================

client = MongoClient(

    MONGO_URI,

    maxPoolSize=20,

    serverSelectionTimeoutMS=5000

)

db = client[DATABASE_NAME]

collection = db[REALTIME_COLLECTION_NAME]

# =====================================================
# MongoDB Indexes
# =====================================================

collection.create_index(
    "status.content_cleaned"
)

collection.create_index(
    "status.sentiment_done"
)

collection.create_index(
    "status.sentiment_failed"
)

collection.create_index(
    "processing.sentiment_time"
)

# =====================================================
# Configuration
# =====================================================

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

SENTIMENT_VERSION = "1.0.0"

MIN_CONTENT_LENGTH = 100

MAX_CHUNK_LENGTH = 450

SENTIMENT_MAP = {

    "positive": "Positive",

    "negative": "Negative",

    "neutral": "Neutral"

}

# =====================================================
# Load HuggingFace Model
# =====================================================

print("=" * 70)
print("Loading Sentiment Model...")
print("=" * 70)

sentiment_pipeline = pipeline(

    "sentiment-analysis",

    model=MODEL_NAME

)

print("Sentiment Model Loaded Successfully")
print("=" * 70)

# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one(

        {

            "status.content_cleaned": True,

            "status.sentiment_done": False,

            "status.sentiment_failed": False

        },

        {

            "_id": 1,

            "title": 1,

            "link": 1,

            "clean_content": 1,

            "processing": 1,

            "fetched_at": 1

        },

        sort=[

            ("fetched_at", 1)

        ]

    )

# =====================================================
# Validate Content
# =====================================================

def validate_content(text):

    if text is None:

        return False

    text = text.strip()

    if len(text) < MIN_CONTENT_LENGTH:

        return False

    return True

# =====================================================
# Split Text into Chunks
# =====================================================

def split_text(text):

    words = text.split()

    chunks = []

    current_chunk = []

    current_length = 0

    for word in words:

        word_length = len(word) + 1

        if current_length + word_length <= MAX_CHUNK_LENGTH:

            current_chunk.append(word)

            current_length += word_length

        else:

            chunks.append(

                " ".join(current_chunk)

            )

            current_chunk = [word]

            current_length = word_length

    if current_chunk:

        chunks.append(

            " ".join(current_chunk)

        )

    return chunks

# =====================================================
# Analyze Sentiment
# =====================================================

def analyze_sentiment(text):

    chunks = split_text(text)

    if len(chunks) == 0:

        return {

            "label": "Neutral",

            "score": 0.0,

            "model": MODEL_NAME,

            "chunks": 0

        }

    label_scores = {

        "Positive": [],

        "Negative": [],

        "Neutral": []

    }

    # ----------------------------------------
    # Analyze Every Chunk
    # ----------------------------------------

    for chunk in chunks:

        result = sentiment_pipeline(chunk)[0]

        label = SENTIMENT_MAP.get(

            result["label"].lower(),

            result["label"]

        )

        score = float(result["score"])

        label_scores[label].append(score)

    # ----------------------------------------
    # Calculate Average Score
    # ----------------------------------------

    average_scores = {}

    for label, scores in label_scores.items():

        if scores:

            average_scores[label] = round(

                sum(scores) / len(scores),

                4

            )

        else:

            average_scores[label] = 0.0

    # ----------------------------------------
    # Final Sentiment
    # ----------------------------------------

    final_label = max(

        average_scores,

        key=average_scores.get

    )

    return {

        "label": final_label,

        "score": average_scores[final_label],

        "model": MODEL_NAME,

        "chunks": len(chunks)

    }
# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one(

        {

            "status.content_cleaned": True,

            "status.sentiment_done": False,

            "status.sentiment_failed": False

        },

        {

            "_id": 1,

            "title": 1,

            "link": 1,

            "clean_content": 1,

            "processing": 1,

            "fetched_at": 1

        },

        sort=[

            ("fetched_at", 1)

        ]

    )

# =====================================================
# Validate Content
# =====================================================

def validate_content(text):

    if text is None:

        return False

    text = text.strip()

    if len(text) < MIN_CONTENT_LENGTH:

        return False

    return True

# =====================================================
# Split Text into Chunks
# =====================================================

def split_text(text):

    words = text.split()

    chunks = []

    current_chunk = []

    current_length = 0

    for word in words:

        word_length = len(word) + 1

        if current_length + word_length <= MAX_CHUNK_LENGTH:

            current_chunk.append(word)

            current_length += word_length

        else:

            chunks.append(

                " ".join(current_chunk)

            )

            current_chunk = [word]

            current_length = word_length

    if current_chunk:

        chunks.append(

            " ".join(current_chunk)

        )

    return chunks

# =====================================================
# Analyze Sentiment
# =====================================================

def analyze_sentiment(text):

    chunks = split_text(text)

    if len(chunks) == 0:

        return {

            "label": "Neutral",

            "score": 0.0,

            "model": MODEL_NAME,

            "chunks": 0

        }

    label_scores = {

        "Positive": [],

        "Negative": [],

        "Neutral": []

    }

    # ----------------------------------------
    # Analyze Every Chunk
    # ----------------------------------------

    for chunk in chunks:

        result = sentiment_pipeline(chunk)[0]

        label = SENTIMENT_MAP.get(

            result["label"].lower(),

            result["label"]

        )

        score = float(result["score"])

        label_scores[label].append(score)

    # ----------------------------------------
    # Calculate Average Score
    # ----------------------------------------

    average_scores = {}

    for label, scores in label_scores.items():

        if scores:

            average_scores[label] = round(

                sum(scores) / len(scores),

                4

            )

        else:

            average_scores[label] = 0.0

    # ----------------------------------------
    # Final Sentiment
    # ----------------------------------------

    final_label = max(

        average_scores,

        key=average_scores.get

    )

    return {

        "label": final_label,

        "score": average_scores[final_label],

        "model": MODEL_NAME,

        "chunks": len(chunks)

    }
# =====================================================
# Update MongoDB
# =====================================================

def update_article(
    article,
    sentiment,
    processing_time
):

    # ----------------------------------------
    # Total Processing Time
    # ----------------------------------------

    total_time = (
        article.get("processing", {})
        .get("total_time", 0)
        + processing_time
    )

    result = collection.update_one(

        {
            "_id": article["_id"]
        },

        {
            "$set": {

                # ------------------------------------
                # Sentiment Result
                # ------------------------------------

                "sentiment": {

                    "label": sentiment["label"],

                    "score": round(
                        sentiment["score"],
                        4
                    ),

                    "model": MODEL_NAME,

                    "version": SENTIMENT_VERSION,

                    "chunks": sentiment["chunks"],

                    "status": "success",

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Status
                # ------------------------------------

                "status.sentiment_done": True,

                "status.sentiment_failed": False,

                # ------------------------------------
                # Processing
                # ------------------------------------

                "processing.sentiment_time": round(
                    processing_time,
                    3
                ),

                "processing.total_time": round(
                    total_time,
                    3
                ),

                # ------------------------------------
                # Metadata
                # ------------------------------------

                "updated_at": datetime.now(UTC),

                "error": None

            }

        }

    )

    print()

    print("=" * 70)
    print("MongoDB Updated")
    print("=" * 70)

    print(f"Matched          : {result.matched_count}")
    print(f"Modified         : {result.modified_count}")

    print(f"Sentiment        : {sentiment['label']}")
    print(f"Confidence       : {sentiment['score']:.4f}")
    print(f"Chunks Processed : {sentiment['chunks']}")
    print(f"Processing Time  : {processing_time:.2f} sec")

    print("=" * 70)


# =====================================================
# Mark Sentiment Failed
# =====================================================

def mark_sentiment_failed(
    article_id,
    error_message
):

    collection.update_one(

        {
            "_id": article_id
        },

        {
            "$set": {

                # ------------------------------------
                # Status
                # ------------------------------------

                "status.sentiment_done": False,

                "status.sentiment_failed": True,

                # ------------------------------------
                # Sentiment
                # ------------------------------------

                "sentiment": {

                    "label": "",

                    "score": 0.0,

                    "model": MODEL_NAME,

                    "version": SENTIMENT_VERSION,

                    "chunks": 0,

                    "status": "failed",

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Metadata
                # ------------------------------------

                "updated_at": datetime.now(UTC),

                "error": error_message

            }

        }

    )

    print()

    print("=" * 70)
    print("Sentiment Failed")
    print("=" * 70)

    print(error_message)

    print("=" * 70)
