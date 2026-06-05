from fastapi import FastAPI, Security, HTTPException
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import logging

from .config import (
    settings,
    get_active_llm_provider,
    get_active_fallback_provider,
    get_active_embedding_provider,
    get_active_market_data_provider,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    if api_key != settings.ai_service_api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: validate at least one LLM key is available
    primary = get_active_llm_provider()
    if "NONE" in primary:
        logger.error("[AI Service] FATAL: No LLM provider configured. Set GEMINI_API_KEY or ANTHROPIC_API_KEY.")
        raise RuntimeError("No LLM provider configured")

    logger.info("\n[AI Service] Active providers:")
    logger.info(f"  LLM primary  : {primary}")
    logger.info(f"  LLM fallback : {get_active_fallback_provider()}")
    logger.info(f"  Embeddings   : {get_active_embedding_provider()}")
    logger.info(f"  Market data  : {get_active_market_data_provider()}")
    logger.info(f"  Environment  : {settings.environment}\n")

    yield


app = FastAPI(
    title="Investom AI Service",
    version="0.1.0",
    description="Internal AI microservice — not public",
    lifespan=lifespan,
)


@app.get("/health", dependencies=[Security(verify_api_key)])
async def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "providers": {
            "llm_primary": get_active_llm_provider(),
            "llm_fallback": get_active_fallback_provider(),
            "embeddings": get_active_embedding_provider(),
            "market_data": get_active_market_data_provider(),
        },
    }


# Routers — registered here, implemented in later prompts
# from .routers import chat, screener, overview
# app.include_router(chat.router, prefix="/ai/chat", tags=["chat"])
# app.include_router(screener.router, prefix="/ai/screener", tags=["screener"])
# app.include_router(overview.router, prefix="/ai/stock", tags=["overview"])
