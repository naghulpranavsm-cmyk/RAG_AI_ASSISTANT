from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import Settings


PLACEHOLDER_KEY_PARTS = {
    "your_google_api_key_here",
    "your_api_key_here",
    "paste",
    "replace",
}


def _looks_like_placeholder(api_key: str | None) -> bool:
    if not api_key:
        return True
    normalized = api_key.strip().lower()
    return any(part in normalized for part in PLACEHOLDER_KEY_PARTS)


def build_llm(settings: Settings) -> BaseChatModel:
    if settings.llm_provider == "gemini":
        if _looks_like_placeholder(settings.google_api_key):
            raise RuntimeError(
                "A valid Gemini API key is required. Set GEMINI_API_KEY or "
                "GOOGLE_API_KEY in your .env file, then restart Streamlit. "
                "If both are set, GOOGLE_API_KEY takes precedence."
            )
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
        )

    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=settings.temperature,
        )

    raise RuntimeError("LLM_PROVIDER must be either 'gemini' or 'openai'.")
