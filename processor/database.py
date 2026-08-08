"""
Database Operations

MongoDB
    ↓
Load Article
Save Results
"""

from bson import ObjectId


# =====================================================
# Load Article
# =====================================================

def load_article(

    article_id,

    collection,

    print_section

):

    print_section("STEP 1 - LOAD ARTICLE")

    print(f"Collection : {collection.name}")

    print(f"Article ID : {article_id}")

    try:

        article = collection.find_one(

            {

                "_id": ObjectId(article_id)

            }

        )

        if article is None:

            print("\n❌ Article NOT FOUND")

            return None

        print("\n✅ Article Found")

        print(f"MongoDB ID : {article['_id']}")

        print("\nAvailable Fields")

        for key in sorted(article.keys()):

            print(f" • {key}")

        title = article.get("title")

        content = article.get("content")

        print(f"\nTitle : {title}")

        print(

            f"Content Length : "

            f"{len(content) if isinstance(content,str) else 0}"

        )

        return article

    except Exception as e:

        print("\nload_article() ERROR")

        print(e)

        return None


# =====================================================
# Save Results
# =====================================================

def save_results(

    article_id,

    data,

    collection

):

    print("\nSAVE_RESULTS CALLED")

    print("Collection :", collection.name)

    print("Fields :", list(data.keys()))

    collection.update_one(

        {

            "_id": ObjectId(article_id)

        },

        {

            "$set": data

        }

    )