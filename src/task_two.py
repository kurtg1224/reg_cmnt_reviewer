from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from src.llm.azure_openai_client import chat_json
from src.utils.logging import get_logger


logger = get_logger(__name__)


def _load_prompt() -> str:
    """Load the Task Two system prompt from `src/prompts/task_two_prompt.txt`."""
    prompt_path = Path(__file__).resolve().parent / "prompts" / "task_two_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def _coerce_result(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize LLM JSON into stable fields: `themes` list and `overall_opinion`.

    Accepts either `themes` or legacy `themes` in the response.
    """
    # Accept either 'themes' (old) or 'themes' (new prompt) as input
    themes_raw = obj.get("themes", obj.get("themes", []))
    if isinstance(themes_raw, str):
        try:
            parsed = json.loads(themes_raw)
            if isinstance(parsed, list):
                themes = parsed
            else:
                themes = [themes_raw]
        except Exception:
            themes = [themes_raw]
    elif isinstance(themes_raw, list):
        themes = themes_raw
    else:
        themes = []
    clean: List[str] = []
    seen = set()
    for t in themes:
        s = str(t).strip()
        if s and s not in seen:
            seen.add(s)
            clean.append(s)
    # Normalize overall opinion
    op_raw = str(obj.get("overall_opinion", "")).strip().lower()
    if op_raw not in {"support", "oppose", "unknown"}:
        op_raw = "unknown"
    return {"themes": clean, "overall_opinion": op_raw}


def extract_themes(comment: str) -> Dict[str, Any]:
    """Run Task Two on a single comment and return `themes` plus `overall_opinion`."""
    system = _load_prompt()
    messages = [
        {"role": "user", "content": f"Comment:\n{comment}\n\nReturn ONLY the JSON as specified."}
    ]
    raw = chat_json(messages, system=system)
    result = _coerce_result(raw or {})
    logger.debug("Task Two result: %s", json.dumps(result))
    return result
