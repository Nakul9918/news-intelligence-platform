

# # """
# # Category Classification Service

# # MongoDB
# #     ↓
# # Find Cleaned Articles
# #     ↓
# # Classify Category
# #     ↓
# # Update MongoDB
# # """

# # from datetime import datetime, UTC

# # from pymongo import MongoClient
# # from transformers import pipeline

# # from config import (
# #     MONGO_URI,
# #     DATABASE_NAME,
# #     REALTIME_COLLECTION_NAME,
# # )

# # # =====================================================
# # # MongoDB
# # # =====================================================

# # client = MongoClient(

# #     MONGO_URI,

# #     maxPoolSize=20,

# #     serverSelectionTimeoutMS=5000

# # )

# # db = client[DATABASE_NAME]

# # collection = db[REALTIME_COLLECTION_NAME]

# # # =====================================================
# # # Model Configuration
# # # =====================================================

# # MODEL_NAME = "facebook/bart-large-mnli"

# # MAX_CHUNK_LENGTH = 450

# # MAX_CLASSIFICATION_CHUNKS = 10

# # CATEGORIES = [

# #     "Politics",

# #     "Business",

# #     "Technology",

# #     "Sports",

# #     "Health",

# #     "Entertainment",

# #     "Science",

# #     "Education",

# #     "World",

# #     "Crime"

# # ]
# # # =====================================================
# # # Load Zero-Shot Model
# # # =====================================================

# # print("=" * 70)
# # print("Loading Category Classification Model...")
# # print("=" * 70)

# # classifier = pipeline(

# #     "zero-shot-classification",

# #     model="facebook/bart-large-mnli"

# # )

# # print("Category Model Loaded Successfully")

# # # =====================================================
# # # Get Pending Article
# # # =====================================================

# # def get_pending_article():

# #     return collection.find_one(

# #         {

# #             "status.content_cleaned": True,

# #             "status.category_done": False

# #         }

# #     )

# # # =====================================================
# # # Update MongoDB
# # # =====================================================

# # def update_article(article_id, category):

# #     result = collection.update_one(

# #         {

# #             "_id": article_id

# #         },

# #         {

# #             "$set": {

# #                 "category": category["label"],

# #                 "category_score": category["score"],

# #                 "status.category_done": True,

# #                 "updated_at": datetime.now(UTC),

# #                 "error": None

# #             }

# #         }

# #     )

# #     print()
# #     print("=" * 70)
# #     print("MongoDB Updated")
# #     print("=" * 70)

# #     print(f"Matched  : {result.matched_count}")
# #     print(f"Modified : {result.modified_count}")

# # # =====================================================
# # # Main
# # # =====================================================

# # def main():

# #     article = get_pending_article()

# #     if article is None:

# #         print("=" * 70)
# #         print("No Pending Articles")
# #         print("=" * 70)

# #         return

# #     print("=" * 70)
# #     print("Classifying Category")
# #     print(article["link"])
# #     print("=" * 70)

# #     try:

# #         category = classify_category(

# #             article["clean_content"]

# #         )

# #         update_article(

# #             article["_id"],

# #             category

# #         )

# #         print()

# #         print("=" * 70)
# #         print("Category Result")
# #         print("=" * 70)

# #         print(f"Category : {category['label']}")
# #         print(f"Score    : {category['score']}")

# #         print("=" * 70)

# #     except Exception as e:

# #         print()

# #         print("=" * 70)
# #         print("Category Classification Failed")
# #         print("=" * 70)

# #         print(e)

# #         collection.update_one(

# #             {

# #                 "_id": article["_id"]

# #             },

# #             {

# #                 "$set": {

# #                     "error": str(e),

# #                     "updated_at": datetime.now(UTC)

# #                 }

# #             }

# #         )


# # # =====================================================
# # # Split Text into Chunks
# # # =====================================================

# # def split_text(text):

# #     chunks = []

# #     # ----------------------------------------
# #     # Split by Paragraph
# #     # ----------------------------------------

# #     paragraphs = [

# #         paragraph.strip()

# #         for paragraph in text.split("\n")

# #         if paragraph.strip()

# #     ]

# #     # ----------------------------------------
# #     # Process Each Paragraph
# #     # ----------------------------------------

# #     for paragraph in paragraphs:

# #         if len(paragraph) <= MAX_CHUNK_LENGTH:

# #             chunks.append(

# #                 paragraph

# #             )

# #             continue

# #         words = paragraph.split()

# #         current_chunk = ""

# #         for word in words:

# #             if len(current_chunk) + len(word) + 1 <= MAX_CHUNK_LENGTH:

# #                 current_chunk += " " + word

# #             else:

# #                 chunks.append(

# #                     current_chunk.strip()

# #                 )

# #                 current_chunk = word

# #         if current_chunk:

# #             chunks.append(

# #                 current_chunk.strip()

# #             )

# #     return chunks

# # # =====================================================
# # # Classify Category
# # # =====================================================

# # def classify_category(text):

# #     chunks = split_text(text)

# #     if not chunks:

# #         return {

# #             "label": "Unknown",

# #             "score": 0.0

# #         }

# #     # ----------------------------------------
# #     # Limit Maximum Chunks
# #     # ----------------------------------------
# #     MAX_CLASSIFICATION_CHUNKS = 10
# #     chunks = chunks[:MAX_CLASSIFICATION_CHUNKS]
    

# #     # ----------------------------------------
# #     # Score Accumulator
# #     # ----------------------------------------

# #     category_scores = {

# #         category: 0.0

# #         for category in CATEGORIES

# #     }

# #     # ----------------------------------------
# #     # Classify Each Chunk
# #     # ----------------------------------------

# #     for chunk in chunks:

# #         result = classifier(

# #             chunk,

# #             candidate_labels=CATEGORIES,

# #             multi_label=False

# #         )

# #         for label, score in zip(

# #             result["labels"],

# #             result["scores"]

# #         ):

# #             category_scores[label] += float(score)

# #     # ----------------------------------------
# #     # Average Scores
# #     # ----------------------------------------

# #     total_chunks = len(chunks)

# #     for category in category_scores:

# #         category_scores[category] = round(

# #             category_scores[category] / total_chunks,

# #             4

# #         )

# #     # ----------------------------------------
# #     # Best Category
# #     # ----------------------------------------

# #     best_category = max(

# #         category_scores,

# #         key=category_scores.get

# #     )

# #     return {

# #         "label": best_category,

# #         "score": category_scores[best_category]

# #     }   
# #     # ----------------------------------------
# #     # Limit Maximum Chunks
# #     # ----------------------------------------

# #     chunks = chunks[:10]

# #     # ----------------------------------------
# #     # Score Accumulator
# #     # ----------------------------------------

# #     category_scores = {

# #         category: 0.0

# #         for category in CATEGORIES

# #     }

# #     # ----------------------------------------
# #     # Classify Each Chunk
# #     # ----------------------------------------

# #     for chunk in chunks:

# #         result = classifier(

# #             chunk,

# #             candidate_labels=CATEGORIES,

# #             multi_label=False

# #         )

# #         for label, score in zip(

# #             result["labels"],

# #             result["scores"]

# #         ):

# #             category_scores[label] += float(score)

# #     # ----------------------------------------
# #     # Average Scores
# #     # ----------------------------------------

# #     total_chunks = len(chunks)

# #     for category in category_scores:

# #         category_scores[category] = round(

# #             category_scores[category] / total_chunks,

# #             4

# #         )

# #     # ----------------------------------------
# #     # Best Category
# #     # ----------------------------------------

# #     best_category = max(

# #         category_scores,

# #         key=category_scores.get

# #     )

# #     return {

# #         "label": best_category,

# #         "score": category_scores[best_category]

# #     }
# #     # ----------------------------------------
# #     # Score Accumulator
# #     # ----------------------------------------

# #     category_scores = {

# #         category: 0.0

# #         for category in CATEGORIES

# #     }

# #     # ----------------------------------------
# #     # Classify Every Chunk
# #     # ----------------------------------------

# #     for chunk in chunks:

# #         result = classifier(

# #             chunk,

# #             candidate_labels=CATEGORIES,

# #             multi_label=False

# #         )

# #         for label, score in zip(

# #             result["labels"],

# #             result["scores"]

# #         ):

# #             category_scores[label] += float(score)

# #     # ----------------------------------------
# #     # Average Scores
# #     # ----------------------------------------

# #     total_chunks = len(chunks)

# #     for category in category_scores:

# #         category_scores[category] = round(

# #             category_scores[category] / total_chunks,

# #             4

# #         )

# #     # ----------------------------------------
# #     # Final Category
# #     # ----------------------------------------

# #     best_category = max(

# #         category_scores,

# #         key=category_scores.get

# #     )

# #     return {

# #         "label": best_category,

# #         "score": category_scores[best_category]

# #     }   



# """
# Category Classification Service

# MongoDB
#     ↓
# Find Cleaned Articles
#     ↓
# Validate Content
#     ↓
# Classify Category
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
# # Model Configuration
# # =====================================================

# MODEL_NAME = "facebook/bart-large-mnli"

# MAX_CHUNK_LENGTH = 450

# MAX_CLASSIFICATION_CHUNKS = 10

# CATEGORIES = [

#     "Politics",

#     "Business",

#     "Technology",

#     "Sports",

#     "Health",

#     "Entertainment",

#     "Science",

#     "Education",

#     "World",

#     "Crime"

# ]

# # =====================================================
# # Load Model
# # =====================================================

# print("=" * 70)
# print("Loading Category Classification Model...")
# print("=" * 70)

# classifier = pipeline(

#     "zero-shot-classification",

#     model=MODEL_NAME

# )

# print("Category Model Loaded Successfully")

# # =====================================================
# # Get Pending Article
# # =====================================================

# def get_pending_article():

#     return collection.find_one(

#         {

#             "status.content_cleaned": True,

#             "status.category_done": False

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

#         if len(paragraph) <= MAX_CHUNK_LENGTH:

#             chunks.append(

#                 paragraph

#             )

#             continue

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
# # Classify Category
# # =====================================================

# def classify_category(text):

#     chunks = split_text(text)

#     if not chunks:

#         return {

#             "label": "Unknown",

#             "score": 0.0

#         }

#     # ----------------------------------------
#     # Limit Maximum Chunks
#     # ----------------------------------------

#     chunks = chunks[:MAX_CLASSIFICATION_CHUNKS]

#     # ----------------------------------------
#     # Score Accumulator
#     # ----------------------------------------

#     category_scores = {

#         category: 0.0

#         for category in CATEGORIES

#     }

#     # ----------------------------------------
#     # Classify Every Chunk
#     # ----------------------------------------

#     for chunk in chunks:

#         result = classifier(

#             chunk,

#             candidate_labels=CATEGORIES,

#             multi_label=False

#         )

#         for label, score in zip(

#             result["labels"],

#             result["scores"]

#         ):

#             category_scores[label] += float(score)

#     # ----------------------------------------
#     # Average Scores
#     # ----------------------------------------

#     total_chunks = len(chunks)

#     for category in category_scores:

#         category_scores[category] = round(

#             category_scores[category] / total_chunks,

#             4

#         )

#     # ----------------------------------------
#     # Final Category
#     # ----------------------------------------

#     best_category = max(

#         category_scores,

#         key=category_scores.get

#     )

#     return {

#         "label": best_category,

#         "score": category_scores[best_category]

#     }

# # =====================================================
# # Update MongoDB
# # =====================================================

# def update_article(

#     article_id,

#     category,

#     processing_time

# ):

#     result = collection.update_one(

#         {

#             "_id": article_id

#         },

#         {

#             "$set": {

#                 "category": category["label"],

#                 "category_score": category["score"],

#                 "category_model": MODEL_NAME,

#                 "status.category_done": True,

#                 "processing.category_time": round(

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

#     print("Classifying Category")

#     print(article["link"])

#     print("=" * 70)

#     try:

#         # ----------------------------------------
#         # Validate Content
#         # ----------------------------------------

#         if not validate_content(

#             article["clean_content"]

#         ):

#             raise ValueError(

#                 "Invalid Clean Content"

#             )

#         # ----------------------------------------
#         # Classify Category
#         # ----------------------------------------

#         category = classify_category(

#             article["clean_content"]

#         )

#         # ----------------------------------------
#         # Processing Time
#         # ----------------------------------------

#         duration = (

#             datetime.now(UTC) - started

#         ).total_seconds()

#         # ----------------------------------------
#         # Update MongoDB
#         # ----------------------------------------

#         update_article(

#             article["_id"],

#             category,

#             duration

#         )

#         # ----------------------------------------
#         # Summary
#         # ----------------------------------------

#         print()

#         print("=" * 70)

#         print("Category Classification Summary")

#         print("=" * 70)

#         print(

#             f"Category        : {category['label']}"

#         )

#         print(

#             f"Confidence      : {category['score']}"

#         )

#         print(

#             f"Model           : {MODEL_NAME}"

#         )

#         print(

#             f"Processing Time : {duration:.2f} sec"

#         )

#         print("=" * 70)

#     except Exception as e:

#         print()

#         print("=" * 70)

#         print("Category Classification Failed")

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


"""
Category Classification Service

MongoDB
    ↓
Find Sentiment Processed Articles
    ↓
Validate Content
    ↓
Classify Category
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
    "status.sentiment_done"
)

collection.create_index(
    "status.category_done"
)

collection.create_index(
    "status.category_failed"
)

collection.create_index(
    "processing.category_time"
)

collection.create_index(
    "category.label"
)

# =====================================================
# Category Configuration
# =====================================================

CATEGORY_VERSION = "1.0.0"

MODEL_NAME = "facebook/bart-large-mnli"

MIN_CONTENT_LENGTH = 100

# =====================================================
# Candidate Labels
# =====================================================

CANDIDATE_LABELS = [

    "Politics",

    "Business",

    "Technology",

    "Sports",

    "Health",

    "Science",

    "Entertainment",

    "Education",

    "Crime",

    "World",

    "Environment"

]

# =====================================================
# Load Zero-Shot Model
# =====================================================

print("=" * 70)
print("Loading Category Classifier")
print("=" * 70)

classifier = pipeline(

    "zero-shot-classification",

    model=MODEL_NAME

)

print("Category Model Loaded")

print("=" * 70)

# =====================================================
# Get Pending Article
# =====================================================

def get_pending_article():

    return collection.find_one(

        {

            "status.sentiment_done": True,

            "status.category_done": False,

            "status.category_failed": False

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
# Classify Category
# =====================================================

def classify_category(text):

    result = classifier(

        text,

        candidate_labels=CANDIDATE_LABELS,

        multi_label=False

    )

    label = result["labels"][0]

    score = float(result["scores"][0])

    return {

        "label": label,

        "score": round(

            score,

            4

        ),

        "model": MODEL_NAME

    }
# =====================================================
# Update MongoDB
# =====================================================

def update_article(
    article,
    category,
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
                # Category
                # ------------------------------------

                "category": {

                    "label": category["label"],

                    "score": round(
                        category["score"],
                        4
                    ),

                    "model": MODEL_NAME,

                    "version": CATEGORY_VERSION,

                    "status": "success",

                    "completed_at": datetime.now(UTC)

                },

                # ------------------------------------
                # Status
                # ------------------------------------

                "status.category_done": True,

                "status.category_failed": False,

                # ------------------------------------
                # Processing
                # ------------------------------------

                "processing.category_time": round(
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

    print(f"Category         : {category['label']}")
    print(f"Confidence       : {category['score']:.4f}")
    print(f"Processing Time  : {processing_time:.2f} sec")

    print("=" * 70)


# =====================================================
# Mark Category Failed
# =====================================================

def mark_category_failed(
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

                "status.category_done": False,

                "status.category_failed": True,

                # ------------------------------------
                # Category
                # ------------------------------------

                "category": {

                    "label": "",

                    "score": 0.0,

                    "model": MODEL_NAME,

                    "version": CATEGORY_VERSION,

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
    print("Category Classification Failed")
    print("=" * 70)

    print(error_message)

    print("=" * 70)
# =====================================================
# Main
# =====================================================

def main():

    processed = 0

    failed = 0

    while True:

        started = datetime.now(UTC)

        article = get_pending_article()

        if article is None:

            print("=" * 70)
            print("No Pending Articles")
            print("=" * 70)

            print()

            print("=" * 70)
            print("Category Classification Summary")
            print("=" * 70)
            print(f"Processed : {processed}")
            print(f"Failed    : {failed}")
            print(f"Success   : {processed}")
            print("=" * 70)

            break

        print("=" * 70)
        print("Category Classification")
        print("=" * 70)
        print(f"Title : {article.get('title', '')}")
        print(f"URL   : {article.get('link', '')}")
        print("=" * 70)

        try:

            # ----------------------------------------
            # Validate Content
            # ----------------------------------------

            text = article.get(
                "clean_content",
                ""
            )

            if not validate_content(text):

                failed += 1

                print("Invalid Clean Content")

                mark_category_failed(
                    article["_id"],
                    "Invalid clean content"
                )

                continue

            # ----------------------------------------
            # Classify Category
            # ----------------------------------------

            category = classify_category(text)

            # ----------------------------------------
            # Processing Time
            # ----------------------------------------

            duration = (
                datetime.now(UTC) - started
            ).total_seconds()

            # ----------------------------------------
            # Update MongoDB
            # ----------------------------------------

            update_article(
                article,
                category,
                duration
            )

            processed += 1

            # ----------------------------------------
            # Summary
            # ----------------------------------------

            print()

            print("=" * 70)
            print("Category Summary")
            print("=" * 70)

            print(f"Category        : {category['label']}")
            print(f"Confidence      : {category['score']:.4f}")
            print(f"Model           : {category['model']}")
            print(f"Processing Time : {duration:.2f} sec")

            print("=" * 70)

        except Exception as e:

            traceback.print_exc()

            failed += 1

            print()

            print("=" * 70)
            print("Category Classification Failed")
            print("=" * 70)

            print(f"Article : {article.get('link', '')}")
            print(f"Reason  : {e}")

            print("=" * 70)

            mark_category_failed(
                article["_id"],
                str(e)
            )

            continue


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    main()
    