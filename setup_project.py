"""
==========================================
News Intelligence Platform
Project Setup
Version : 1.0
==========================================
"""

from __future__ import annotations

import importlib
import platform
import sys

from pymongo import MongoClient
import spacy
from sentence_transformers import SentenceTransformer
from gliner import GLiNER


# =====================================================
# Required Packages
# =====================================================

PACKAGES = [
    "pymongo",
    "numpy",
    "pandas",
    "torch",
    "transformers",
    "sentence_transformers",
    "spacy",
    "yake",
    "gliner",
    "newspaper",
    "trafilatura",
    "feedparser",
    "bs4",
    "sklearn",
]


# =====================================================
# Python
# =====================================================

def check_python():

    return {

        "python": sys.version,

        "platform": platform.system(),

        "release": platform.release(),

    }


# =====================================================
# Packages
# =====================================================

def check_packages():

    print("\nChecking Packages...\n")

    missing = []

    for package in PACKAGES:

        try:

            importlib.import_module(package)

            print(f"✓ {package}")

        except ModuleNotFoundError:

            print(f"✗ {package}")

            missing.append(package)

    return missing


# =====================================================
# MongoDB
# =====================================================

def check_mongodb():

    print("\nChecking MongoDB...\n")

    try:

        client = MongoClient(

            "mongodb://localhost:27017",

            serverSelectionTimeoutMS=3000,

        )

        client.admin.command("ping")

        print("✓ MongoDB Connected")

        return True

    except Exception as e:

        print(f"✗ MongoDB : {e}")

        return False


# =====================================================
# spaCy
# =====================================================

def check_spacy():

    print("\nChecking spaCy model...\n")

    try:

        spacy.load("en_core_web_sm")

        print("✓ en_core_web_sm")

        return True

    except Exception:

        print("✗ en_core_web_sm not installed")

        print("Run:")
        print("python -m spacy download en_core_web_sm")

        return False


# =====================================================
# GLiNER
# =====================================================

def check_gliner():

    print("\nChecking GLiNER model...\n")

    try:

        GLiNER.from_pretrained(

            "urchade/gliner_small-v2.1"

        )

        print("✓ GLiNER Ready")

        return True

    except Exception as e:

        print(f"✗ GLiNER : {e}")

        return False


# =====================================================
# Embedding Model
# =====================================================

def check_embedding_model():

    print("\nChecking Embedding model...\n")

    try:

        SentenceTransformer(

            "all-MiniLM-L6-v2"

        )

        print("✓ all-MiniLM-L6-v2 Ready")

        return True

    except Exception as e:

        print(f"✗ Embedding Model : {e}")

        return False


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":

    print("=" * 60)

    print("News Intelligence Platform Setup")

    print("=" * 60)

    print(check_python())

    missing = check_packages()

    check_mongodb()

    check_spacy()

    check_gliner()

    check_embedding_model()

    print("\n" + "=" * 60)

    if missing:

        print("Missing Packages:\n")

        for package in missing:

            print(f" - {package}")

    else:

        print("✓ All Packages Installed")

    print("=" * 60)

    print("Setup Completed")

    print("=" * 60)