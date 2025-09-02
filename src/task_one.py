from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from src.llm.azure_openai_client import chat_json
from src.utils.logging import get_logger


logger = get_logger(__name__)


def _load_prompt() -> str:
    """Load the Task One system prompt from `src/prompts/task_one_prompt.txt`."""
    prompt_path = Path(__file__).resolve().parent / "prompts" / "task_one_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def _coerce_result(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize LLM JSON into stable booleans-as-strings and string lists.

    Returns keys: `pii_ver`, `pii_txt`, `third_pty_info_ver`, `third_pty_info_txt`,
    `ssa_employee_ver`, `ssa_employee_txt`, `offensive_lang_ver`, `offensive_lang_txt`.
    """
    def as_bool_str(v: Any) -> str:
        if isinstance(v, bool):
            return "True" if v else "False"
        s = str(v).strip().lower()
        return "True" if s in {"true", "1", "yes"} else "False"

    def as_list(v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v.strip() else []
        if isinstance(v, list):
            return [str(x) for x in v if str(x).strip()]
        return []

    # Only new keys
    keys = [
        ("pii_ver", "pii_txt"),
        ("third_pty_info_ver", "third_pty_info_txt"),
        ("ssa_employee_ver", "ssa_employee_txt"),
        ("offensive_lang_ver", "offensive_lang_txt"),
    ]
    out: Dict[str, Any] = {}
    for v_key, t_key in keys:
        out[v_key] = as_bool_str(obj.get(v_key, "False"))
        out[t_key] = as_list(obj.get(t_key, []))
    return out


def review_comment_for_redactions(comment: str) -> Dict[str, Any]:
    """Run Task One against a single comment and return normalized redaction fields."""
    system = _load_prompt()
    messages = [
        {"role": "user", "content": f"Comment:\n{comment}\n\nReturn ONLY the JSON as specified."}
    ]
    raw = chat_json(messages, system=system)
    result = _coerce_result(raw or {})
    logger.debug("Task One result: %s", json.dumps(result))
    return result
