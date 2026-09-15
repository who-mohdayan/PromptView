import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load .env if it exists (won't exist on Vercel - env vars set there directly)
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)


def get_gemini_api_key() -> str:
    """Dynamically read the Gemini API key from .env or environment."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key


def get_gemini_model() -> str:
    """Dynamically read the configured Gemini model."""
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()


def is_api_key_configured() -> bool:
    """Check if a Gemini API key is configured and not a placeholder."""
    key = get_gemini_api_key()
    return bool(key) and key != "your_gemini_api_key_here"
