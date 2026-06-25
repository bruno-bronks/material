from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config import get_settings


@lru_cache
def get_llm(temperature: float = 0.2) -> ChatOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada. Defina-a em backend/.env (veja .env.example)."
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=temperature,
        max_tokens=4096,
        timeout=60,
        max_retries=2,
    )
