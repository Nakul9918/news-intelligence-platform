from nlp.keyword_extractor import (
    warmup_model,
    module_information,
)

print("=" * 60)
print("WARMUP")
print("=" * 60)

warmup_model()

print()

print(module_information())