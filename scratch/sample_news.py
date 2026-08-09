import json

data = json.load(open('data/news.json', encoding='utf-8'))
print(f"Total read: {len(data)}")

for i, doc in enumerate(data[:12]):
    source = doc.get('source', {}).get('name', 'Unknown')
    title = doc.get('title', 'No Title')
    link = doc.get('link', '')
    pub_date = doc.get('published_date', '')
    print(f"{i+1}. [{source}] {title} ({pub_date[:22]})")
