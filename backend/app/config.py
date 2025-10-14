import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "market_research.db")
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXPIRATION = 24
    LOG_FILE = "api_requests.log"
    MAPS_RADIUS = 3000
