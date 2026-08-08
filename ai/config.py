import os
import sys
import site

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.2"))
AI_MAX_CONTEXT_ARTICLES = int(os.getenv("AI_MAX_CONTEXT_ARTICLES", "8"))
