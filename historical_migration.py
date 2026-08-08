"""
=========================================================
Historical Migration Pipeline v2

Migrates historical articles to the latest schema using
the Realtime NLP Pipeline.

Workflow

Historical Collection
        ↓
Find nlp_completed != True
        ↓
Use stored MongoDB content
        ↓
process_article()
        ↓
Update same document

Supports
---------
✓ Resume processing
✓ Progress
✓ ETA
✓ Success / Failure count
✓ All historical collections

=========================================================
"""

# =====================================================
# Imports
# =====================================================

from datetime import timedelta
from time import perf_counter
import traceback

from pymongo import MongoClient

from realtime_pipeline.realtime_nlp_pipeline import process_article

# =====================================================
# MongoDB Configuration
# =====================================================

MONGO_URI = "mongodb://localhost:27017"

DATABASE_NAME = "news_db"

COLLECTIONS = [

    # "historical_urls_et",

    # "historical_urls_hindustantimes",

    # "historical_urls_indianexpress",

    "historical_urls_thehindu"

]

# =====================================================
# MongoDB Connection
# =====================================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

# =====================================================
# Helper Functions
# =====================================================

def print_section(title):

    print()

    print("=" * 80)

    print(title)

    print("=" * 80)


def format_time(seconds):

    return str(
        timedelta(
            seconds=int(seconds)
        )
    )


def print_progress(
    processed,
    total,
    success,
    failed,
    elapsed,
    eta
):

    print()

    print("-" * 80)

    print(f"Progress        : {processed}/{total}")

    print(f"Successful      : {success}")

    print(f"Failed          : {failed}")

    print(f"Elapsed Time    : {format_time(elapsed)}")

    print(f"Remaining ETA   : {format_time(eta)}")

    print("-" * 80)


# =====================================================
# Collection Statistics
# =====================================================

def collection_summary(collection):

    query = {

        "nlp_completed": {

            "$ne": True

        }

    }

    remaining = collection.count_documents(query)

    total = collection.count_documents({})

    completed = total - remaining

    return {

        "total": total,

        "completed": completed,

        "remaining": remaining

    }
# =====================================================
# Process One Collection
# =====================================================

def process_collection(collection_name):

    collection = db[collection_name]

    stats = collection_summary(collection)

    print_section(f"Collection : {collection_name}")

    print(f"Total Articles     : {stats['total']:,}")
    print(f"Already Processed  : {stats['completed']:,}")
    print(f"Remaining          : {stats['remaining']:,}")

    if stats["remaining"] == 0:

        print("\n✅ Collection already migrated.")

        return

    query = {

        "nlp_completed": {

            "$ne": True

        }

    }

    processed = 0
    success = 0
    failed = 0

    collection_start = perf_counter()

    cursor = collection.find(

        query,

        no_cursor_timeout=True

    )

    try:

        for article in cursor:

            processed += 1

            article_start = perf_counter()

            print()

            print("=" * 80)

            print("=" * 80)
            print(f"[{processed}/{stats['remaining']}]")
            print(f"ID    : {article['_id']}")
            print(f"Title : {article.get('title', '')}")
            print("=" * 80)

            print("=" * 80)

            try:

                ok = process_article(

                    str(article["_id"]),

                    collection

                )

                if ok:

                    success += 1

                else:

                    failed += 1

            except Exception as e:

                failed += 1

                print(f"\n❌ ERROR : {e}")
                traceback.print_exc()

            article_time = perf_counter() - article_start

            elapsed = perf_counter() - collection_start

            average = elapsed / processed

            remaining = stats["remaining"] - processed

            eta = remaining * average

            print_progress(

                processed,

                stats["remaining"],

                success,

                failed,

                elapsed,

                eta

            )

            print(

                f"Last Article Time : "

                f"{article_time:.2f} sec"

            )

    finally:

        cursor.close()

    print_section(

        f"{collection_name} Completed"

    )

    print(f"Processed : {processed}")

    print(f"Success   : {success}")

    print(f"Failed    : {failed}")

    print(

        f"Execution Time : "

        f"{format_time(perf_counter() - collection_start)}"

    )
# =====================================================
# Main
# =====================================================

def main():

    overall_start = perf_counter()

    print_section("Historical Schema Migration")

    print("\nCollections Summary\n")

    grand_total = 0
    grand_completed = 0
    grand_remaining = 0

    for collection_name in COLLECTIONS:

        collection = db[collection_name]

        stats = collection_summary(collection)

        grand_total += stats["total"]
        grand_completed += stats["completed"]
        grand_remaining += stats["remaining"]

        print(f"{collection_name}")

        print(f"   Total      : {stats['total']:,}")

        print(f"   Completed  : {stats['completed']:,}")

        print(f"   Remaining  : {stats['remaining']:,}")

        print()

    print("=" * 80)

    print(f"Grand Total      : {grand_total:,}")

    print(f"Already Complete : {grand_completed:,}")

    print(f"To Process       : {grand_remaining:,}")

    print("=" * 80)

    if grand_remaining == 0:

        print("\n✅ Everything is already migrated.")

        return

    input("\nPress ENTER to start migration...")

    for collection_name in COLLECTIONS:

        process_collection(collection_name)

    total_time = perf_counter() - overall_start

    print_section("Migration Completed Successfully")

    print(f"Total Execution Time : {format_time(total_time)}")

    print("\nMongoDB Connection Closed.")


# =====================================================
# Entry Point
# =====================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print("\n\nMigration stopped by user.")

    except Exception as e:

        print(f"\nUnexpected Error : {e}")

    finally:

        client.close()