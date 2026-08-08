"""
Run Economic Times Bootstrap
"""

from bootstrap.collectors.et_collector import collect_et_articles
from bootstrap.bootstrap_producer import publish_articles


def main():

    print("=" * 70)
    print("Economic Times Bootstrap")
    print("=" * 70)

    articles = collect_et_articles()

    print(f"\nCollected Articles : {len(articles)}")

    published, failed = publish_articles(articles)

    print("\n" + "=" * 70)
    print("Bootstrap Summary")
    print("=" * 70)
    print(f"Collected : {len(articles)}")
    print(f"Published : {published}")
    print(f"Failed    : {failed}")


if __name__ == "__main__":
    main()