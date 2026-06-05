"""
LLM Provider abstraction.
Selects the correct provider based on ENVIRONMENT and available API keys.

Development:  Gemini (primary) → xAI Grok (fallback)
Production:   Anthropic Claude (primary) → OpenAI (fallback)
"""

from openai import AsyncOpenAI
from .config import settings


def _get_primary_client() -> tuple[AsyncOpenAI, str]:
    """Returns (client, model_name) for the primary LLM provider."""
    if settings.environment == "development":
        if settings.gemini_api_key:
            client = AsyncOpenAI(
                api_key=settings.gemini_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            return client, settings.gemini_model
        if settings.xai_api_key:
            client = AsyncOpenAI(
                api_key=settings.xai_api_key,
                base_url="https://api.x.ai/v1",
            )
            return client, settings.xai_model
    else:
        # staging/production — prefer Anthropic but fall through to OpenAI-compatible
        if settings.anthropic_api_key:
            # Anthropic has its own SDK — handled separately in call_llm
            return None, settings.anthropic_model  # type: ignore
        if settings.openai_api_key:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            return client, settings.openai_llm_model

    raise RuntimeError("No LLM API key configured. Set GEMINI_API_KEY (dev) or ANTHROPIC_API_KEY (prod).")


def _get_fallback_client() -> tuple[AsyncOpenAI, str] | tuple[None, None]:
    """Returns (client, model_name) for the fallback LLM provider, or (None, None)."""
    if settings.environment == "development":
        if settings.xai_api_key:
            client = AsyncOpenAI(
                api_key=settings.xai_api_key,
                base_url="https://api.x.ai/v1",
            )
            return client, settings.xai_model
    else:
        if settings.openai_api_key:
            return AsyncOpenAI(api_key=settings.openai_api_key), settings.openai_llm_model
    return None, None


async def call_llm(
    messages: list[dict],
    system_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """
    Call the primary LLM with automatic fallback.
    Uses Anthropic SDK directly when ANTHROPIC_API_KEY is set in production.
    Falls back to OpenAI-compatible clients otherwise.
    """
    # Production path with Anthropic SDK (supports prompt caching)
    if settings.environment != "development" and settings.anthropic_api_key:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        try:
            response = await client.messages.create(
                model=settings.anthropic_model,
                max_tokens=max_tokens,
                system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
                messages=messages,
                temperature=temperature,
            )
            return response.content[0].text  # type: ignore
        except Exception as e:
            # Fall through to OpenAI fallback
            pass

    # OpenAI-compatible path (Gemini, xAI, or OpenAI)
    primary_client, primary_model = _get_primary_client()
    all_messages = [{"role": "system", "content": system_prompt}] + messages

    try:
        if primary_client is not None:
            response = await primary_client.chat.completions.create(
                model=primary_model,
                messages=all_messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
    except Exception:
        pass

    # Fallback
    fallback_client, fallback_model = _get_fallback_client()
    if fallback_client and fallback_model:
        response = await fallback_client.chat.completions.create(
            model=fallback_model,
            messages=all_messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    raise RuntimeError("All LLM providers failed.")


async def get_embedding(text: str) -> list[float]:
    """Get text embedding using HuggingFace (dev) or OpenAI (prod)."""
    if settings.environment == "development" and settings.huggingface_api_key:
        client = AsyncOpenAI(
            api_key=settings.huggingface_api_key,
            base_url="https://api-inference.huggingface.co/v1",
        )
        response = await client.embeddings.create(
            model=settings.huggingface_embedding_model,
            input=text,
        )
        return response.data[0].embedding

    if settings.openai_api_key:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding

    raise RuntimeError("No embedding provider configured.")
