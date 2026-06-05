from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # Required — always needed
    ai_service_api_key: str
    supabase_url: str
    supabase_secret_key: str
    environment: Literal["development", "staging", "production"] = "development"

    # Free tier LLM — primary for development
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    # Free tier LLM — fallback for development
    xai_api_key: str | None = None
    xai_model: str = "grok-3-mini"

    # Free tier embeddings — development
    huggingface_api_key: str | None = None
    huggingface_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Paid providers — staging/production only
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5"
    openai_api_key: str | None = None
    openai_llm_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Market data — optional
    eodhd_api_key: str | None = None
    alpha_vantage_api_key: str | None = None

    class Config:
        env_file = "../../.env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()


def get_active_llm_provider() -> str:
    """Returns the name of the active primary LLM provider based on environment and available keys."""
    if settings.environment == "development":
        if settings.gemini_api_key:
            return f"Gemini {settings.gemini_model} (FREE)"
        if settings.xai_api_key:
            return f"xAI Grok {settings.xai_model} (FREE)"
    else:
        if settings.anthropic_api_key:
            return f"Anthropic {settings.anthropic_model}"
        if settings.openai_api_key:
            return f"OpenAI {settings.openai_llm_model}"
    return "NONE — no LLM key configured!"


def get_active_fallback_provider() -> str:
    if settings.environment == "development":
        if settings.xai_api_key:
            return f"xAI Grok {settings.xai_model} (FREE)"
    else:
        if settings.openai_api_key:
            return f"OpenAI {settings.openai_llm_model}"
    return "None"


def get_active_embedding_provider() -> str:
    if settings.environment == "development":
        if settings.huggingface_api_key:
            return f"HuggingFace {settings.huggingface_embedding_model} (FREE)"
    if settings.openai_api_key:
        return f"OpenAI {settings.openai_embedding_model}"
    return "None"


def get_active_market_data_provider() -> str:
    if settings.eodhd_api_key:
        return "EODHD"
    return "yfinance (FREE)"
