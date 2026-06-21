from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chroma_db_dir: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    collection_name: str = os.getenv("COLLECTION_NAME", "rag_assistant")
    chunk_size: int = _get_int("CHUNK_SIZE", 1000)
    chunk_overlap: int = _get_int("CHUNK_OVERLAP", 150)
    retrieval_k: int = _get_int("RETRIEVAL_K", 4)
    temperature: float = _get_float("TEMPERATURE", 0.2)


def get_settings() -> Settings:
    return Settings()
