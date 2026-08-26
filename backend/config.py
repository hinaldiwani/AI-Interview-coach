import os
from dotenv import load_dotenv

load_dotenv()

# Database Config (MySQL)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3305))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "hinal")
DB_NAME = os.getenv("DB_NAME", "ai_interview_coach")

# Auth Config
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_ai_interview_coach_key_2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

# AI API Key
AI_API_KEY = os.getenv("AI_API_KEY", os.getenv("GEMINI_API_KEY", "")).strip()

# Server Config
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
