import json

DATA_FILE = "backend/sample_data/sample_news.json"


def load_news():
    with open(DATA_FILE, "r") as file:
        return json.load(file)