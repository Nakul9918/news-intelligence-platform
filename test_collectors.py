"""
Phase 3 — Unified News Collectors Verification Test

Verifies all four news source collectors:
- Economic Times
- The Hindu
- Indian Express
- Hindustan Times
"""

import sys
import io
from pathlib import Path
from urllib.parse import urlparse

# Set stdout encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from bootstrap.realtime_bootstrap.et_loader import collect_august_articles as collect_et
from bootstrap.realtime_bootstrap.thehindu_loader import collect_august_articles as collect_thehindu
from bootstrap.realtime_bootstrap.indianexpress_loader import collect_august_articles as collect_indianexpress
from bootstrap.realtime_bootstrap.hindustantimes_loader import collect_august_articles as collect_hindustantimes
from crawler.rss_crawler import fetch_news as fetch_rss_news

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], result.netloc])
    except Exception:
        return False

def verify_collector(source_name, collector_func):
    try:
        articles = collector_func()
        if not isinstance(articles, list):
            return {"count": 0, "dup_ids": 0, "dup_links": 0, "status": "FAIL (Not a list)"}
        
        seen_ids = set()
        seen_links = set()
        dup_ids = 0
        dup_links = 0
        
        for art in articles:
            article_id = art.get("article_id")
            link = art.get("link")
            source = art.get("source", {})
            src_name = source.get("name") if isinstance(source, dict) else str(source)
            
            if not article_id:
                return {"count": len(articles), "dup_ids": dup_ids, "dup_links": dup_links, "status": "FAIL (Missing article_id)"}
            if not link or not is_valid_url(link):
                return {"count": len(articles), "dup_ids": dup_ids, "dup_links": dup_links, "status": "FAIL (Invalid URL link)"}
            if not src_name or src_name != source_name:
                return {"count": len(articles), "dup_ids": dup_ids, "dup_links": dup_links, "status": f"FAIL (Invalid source name: {src_name})"}
            
            if article_id in seen_ids:
                dup_ids += 1
            else:
                seen_ids.add(article_id)
                
            if link in seen_links:
                dup_links += 1
            else:
                seen_links.add(link)
                
        status = "PASS" if len(articles) > 0 else "WARNING (0 articles)"
        return {"count": len(articles), "dup_ids": dup_ids, "dup_links": dup_links, "status": status}

    except Exception as e:
        return {"count": 0, "dup_ids": 0, "dup_links": 0, "status": f"FAIL ({type(e).__name__})"}

def main():
    print("=" * 80)
    print("RUNNING UNIFIED COLLECTORS VERIFICATION TEST (PHASE 3)")
    print("=" * 80)
    
    collectors = [
        ("Economic Times", collect_et),
        ("The Hindu", collect_thehindu),
        ("Indian Express", collect_indianexpress),
        ("Hindustan Times", collect_hindustantimes),
    ]
    
    results = {}
    all_passed = True
    
    for name, func in collectors:
        print(f"\n--- Testing Collector: {name} ---")
        res = verify_collector(name, func)
        results[name] = res
        if "FAIL" in res["status"]:
            all_passed = False
            
    print("\n--- Testing RSS Fallback Feeds ---")
    try:
        rss_articles = fetch_rss_news()
        print(f"Total RSS Articles Fetched: {len(rss_articles)}")
    except Exception as e:
        print(f"RSS Fetch Error: {e}")

    print("\n" + "=" * 80)
    print(f"{'SOURCE':<20} {'COUNT':<10} {'DUPLICATE_IDS':<16} {'DUPLICATE_LINKS':<18} {'STATUS':<15}")
    print("=" * 80)
    
    for name, res in results.items():
        print(f"{name:<20} {res['count']:<10} {res['dup_ids']:<16} {res['dup_links']:<18} {res['status']:<15}")
        
    print("=" * 80)
    if all_passed:
        print("ALL FOUR COLLECTORS PASSED SUCCESSFULLY!")
    else:
        print("SOME COLLECTORS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
