from nlp.gemini_processor import process_article

sample_article = """
India defeated Australia by 5 wickets in the ICC Champions Trophy final.
Virat Kohli scored 92 runs while KL Rahul remained unbeaten.
The match was played in Dubai on Sunday.
"""

result = process_article(sample_article)

print("=" * 60)
print("CLEAN CONTENT")
print("=" * 60)
print(result["clean_content"])

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(result["summary"])

print("\n" + "=" * 60)
print("CATEGORY")
print("=" * 60)
print(result["category"])