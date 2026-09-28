"""Load application settings from backend/.env."""

import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)

SWEDAVIA_API_KEY: str = os.getenv("SWEDAVIA_API_KEY", "")
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
