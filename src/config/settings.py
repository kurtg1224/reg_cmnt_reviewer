from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_chat_deployment: str
    azure_openai_embedding_deployment: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Load .env when present
    load_dotenv(override=False)

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01").strip()
    chat_dep = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()
    embed_dep = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "").strip()

    if not endpoint or not api_key or not chat_dep or not embed_dep:
        missing = [
            name for name, val in [
                ("AZURE_OPENAI_ENDPOINT", endpoint),
                ("AZURE_OPENAI_API_KEY", api_key),
                ("AZURE_OPENAI_CHAT_DEPLOYMENT", chat_dep),
                ("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", embed_dep),
            ]
            if not val
        ]
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Create a .env from .env.example or set env vars."
        )

    return Settings(
        azure_openai_endpoint=endpoint,
        azure_openai_api_key=api_key,
        azure_openai_api_version=api_version,
        azure_openai_chat_deployment=chat_dep,
        azure_openai_embedding_deployment=embed_dep,
    )
