"""Configuration management for QuestLearn: Shadows of the Machine."""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings:
    def __init__(self):
        load_dotenv(dotenv_path=env_path)

    @property
    def MONGO_URI(self) -> str:
        load_dotenv(dotenv_path=env_path, override=True)
        return os.getenv("MONGO_URI", "")

    @property
    def GEMMA_API_KEY(self) -> str:
        load_dotenv(dotenv_path=env_path, override=True)
        return (
            os.getenv("GEMMA_API_KEY")
            or os.getenv("GROQ_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or ""
        ).strip()

    @property
    def GEMMA_API_BASE(self) -> str:
        load_dotenv(dotenv_path=env_path, override=True)
        custom_base = os.getenv("GEMMA_API_BASE")
        if custom_base:
            return custom_base.strip()

        key = self.GEMMA_API_KEY
        if key.startswith("AIza"):
            # Google Gemini OpenAI-compatible endpoint
            return "https://generativelanguage.googleapis.com/v1beta/openai"
        # Default to Groq OpenAI-compatible endpoint
        return "https://api.groq.com/openai/v1"

    @property
    def GEMMA_MODEL(self) -> str:
        load_dotenv(dotenv_path=env_path, override=True)
        custom_model = os.getenv("GEMMA_MODEL")
        if custom_model:
            return custom_model.strip()

        key = self.GEMMA_API_KEY
        if key.startswith("AIza"):
            # Default fast model for Google Gemini
            return "gemini-2.5-flash"
        # Default model for Groq (open-weight Gemma 2 9B)
        return "gemma2-9b-it"

    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", 8000))

    @property
    def DEBUG(self) -> bool:
        return os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")


settings = Settings()
