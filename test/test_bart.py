from transformers import AutoModel

print("Loading...")

model = AutoModel.from_pretrained(
    "bert-base-uncased"
)

print("Loaded")