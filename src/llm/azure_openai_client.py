from __future__ import annotations

import json
import re
import os
from typing import Any, Dict, List, Optional

import numpy as np
from tenacity import retry, stop_after_attempt, wait_random_exponential

from openai import AzureOpenAI

from src.utils.logging import get_logger
from dotenv import load_dotenv


logger = get_logger(__name__)


_client: Optional[AzureOpenAI] = None


def get_client() -> AzureOpenAI:
    """Initialize and cache the Azure OpenAI client using environment variables.

    Expected env vars (see .env.example):
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_KEY
    - AZURE_OPENAI_API_VERSION (optional, defaults to '2024-02-01')
    """
    global _client
    if _client is None:
        load_dotenv(override=False)
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01").strip()
        if not endpoint or not api_key:
            raise RuntimeError(
                "Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY. Configure your .env."
            )
        _client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        logger.info("Initialized AzureOpenAI client")
    return _client


def _coerce_json(text: str) -> Any:
    """Parse JSON from model output, stripping code fences and extra text when present."""
    # Remove code fences if present
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
    # Find first JSON object/array
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
    if match:
        cleaned = match.group(1)
    return json.loads(cleaned)


@retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(6))
def chat_json(messages: List[Dict[str, str]], system: Optional[str] = None, temperature: float = 0.0, max_tokens: int = 700) -> Dict[str, Any]:
    """Call Azure OpenAI chat completion enforcing a JSON object response.

    Returns a parsed JSON dict (empty dict on failure).
    """
    client = get_client()
    msg_payload: List[Dict[str, str]] = []
    if system:
        msg_payload.append({"role": "system", "content": system})
    msg_payload.extend(messages)

    # Required chat deployment name from env
    chat_model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()
    if not chat_model:
        raise RuntimeError("Missing AZURE_OPENAI_CHAT_DEPLOYMENT in environment.")

    resp = client.chat.completions.create(
        model=chat_model,
        messages=msg_payload,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    try:
        return _coerce_json(content)
    except Exception as e:
        logger.warning("Falling back to best-effort JSON parsing: %s", e)
        return json.loads("{}")


@retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(6))
def embed_texts(texts: List[str], batch_size: int = 100) -> np.ndarray:
    """Generate embeddings for a list of texts using the embedding deployment from env."""
    client = get_client()
    model = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "").strip()
    if not model:
        raise RuntimeError("Missing AZURE_OPENAI_EMBEDDING_DEPLOYMENT in environment.")
    all_vecs: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        resp = client.embeddings.create(model=model, input=batch)
        vecs = [d.embedding for d in resp.data]
        all_vecs.extend(vecs)
    return np.array(all_vecs, dtype=np.float32)
