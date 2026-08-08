from pprint import pprint

from nlp.summarizer import (

    generate_summary,

    warmup_model,

    health_check,

)

article = """
Apple introduced a new AI-powered MacBook during its annual event.
The company highlighted improved performance, AI-powered tools,
and better battery life. Tim Cook said the new lineup is designed
to accelerate AI adoption for developers and everyday users.
"""

print("=" * 60)
print("WARMUP")
print("=" * 60)

warmup_model()

print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(
    generate_summary(article)
)

print()

print("=" * 60)
print("HEALTH")
print("=" * 60)

pprint(
    health_check()
)