import sys
sys.path.append(".")
import dashboard

query = "war"
hits = dashboard.mongo_fallback_search(query, limit=5)
print(f"=== UPGRADED SEARCH RESULTS FOR '{query}' ===")
print(f"Total Hits: {len(hits)}")
for h in hits:
    print(f"  [Score: {h['_score']:.1f}] {h['title']}")
