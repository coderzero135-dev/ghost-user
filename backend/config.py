import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "offline")
GEMINI_API_KEY = GEMINI_API_KEY.strip()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nipx.db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-to-a-random-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 72
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
SCREENSHOTS_DIR = os.path.join(UPLOAD_DIR, "screenshots")
VIDEOS_DIR = os.path.join(UPLOAD_DIR, "videos")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
