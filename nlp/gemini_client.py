import os

from dotenv import load_dotenv
from google import genai

# Load .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Gemini Client
client = genai.Client(api_key=API_KEY)

# Model Name
MODEL = "gemini-2.5-flash"