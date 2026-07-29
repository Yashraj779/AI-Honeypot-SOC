import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application Configuration"""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-this"
    )

    MONGO_URI = os.getenv("MONGO_URI")

    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI environment variable not found."
        )

    DATABASE_NAME = "ai_honeypot"

    LOG_COLLECTION = "logs"

    DEBUG = True