from __future__ import annotations

import json
import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Dict, Optional, Tuple, List

import pandas as pd
from tqdm import tqdm

from src.task_one import review_comment_for_redactions
from src.task_two import extract_themes
from src.utils.logging import get_logger


logger = get_logger(__name__)


def _process_single(comment: str) -> Dict[str, Any]:
    """Run Task One and Task Two on a single comment and merge the dictionaries."""
    t1 = review_comment_for_redactions(comment)
    t2 = extract_themes(comment)
    return {**t1, **t2}


def _serialize_list(val: Any) -> str:
    """Serialize a value as a JSON list string, coercing non-lists to sane defaults."""
    try:
        return json.dumps(val, ensure_ascii=False)
    except Exception:
        return "[]" if not val else json.dumps([str(val)], ensure_ascii=False)


def process_file(
    input_path: str,
    output_path: str,
    text_column: str,
    uid_column: Optional[str] = None,
    name_column: Optional[str] = None,
    date_column: Optional[str] = None,
    processes: Optional[int] = None,
) -> Tuple[int, str]:
    """Process an Excel file of comments and write Task One & Two outputs.

    Args:
        input_path: Path to input Excel containing comments.
        output_path: Path to write results Excel.
        text_column: Column name containing the comment text.
        uid_column, name_column, date_column: Reserved for future use.
        processes: Max worker processes for parallelism.

    Returns:
        (row_count, output_path)
    """
    df = pd.read_excel(input_path)
    if text_column not in df.columns:
        raise ValueError(f"Missing required text column: {text_column}")

    comments = df[text_column].fillna("").astype(str).tolist()

    results: List[Optional[Dict[str, Any]]] = [None] * len(comments)
    with ProcessPoolExecutor(max_workers=processes) as ex:
        futures = {ex.submit(_process_single, c): idx for idx, c in enumerate(comments)}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Processing comments"):
            idx = futures[fut]
            try:
                results[idx] = fut.result()
            except Exception as e:
                logger.error("Row %s failed: %s", idx, e)
                results[idx] = {
                    "pii_ver": "False",
                    "pii_txt": [],
                    "third_pty_info_ver": "False",
                    "third_pty_info_txt": [],
                    "ssa_employee_ver": "False",
                    "ssa_employee_txt": [],
                    "offensive_lang_ver": "False",
                    "offensive_lang_txt": [],
                    "overall_opinion": "unknown",
                    "themes": [],
                }

    # Merge results
    out_df = df.copy()

    def get_col(col: str) -> List[Any]:
        return [r.get(col) if r else None for r in results]

    for col in [
        "pii_ver",
        "third_pty_info_ver",
        "ssa_employee_ver",
        "offensive_lang_ver",
        "overall_opinion",
    ]:
        out_df[col] = get_col(col)

    for col in [
        "pii_txt",
        "third_pty_info_txt",
        "ssa_employee_txt",
        "offensive_lang_txt",
        "themes",
    ]:
        out_df[col] = [
            _serialize_list(vals) if isinstance(vals, (list, tuple)) else _serialize_list([])
            for vals in get_col(col)
        ]

    # Insert a readable datetime stamp before the extension to ensure unique filenames
    # Example format: 01302025_0352PM
    ts = datetime.now().strftime("%m%d%Y_%I%M%p")
    base, ext = os.path.splitext(output_path)
    stamped_output_path = f"{base}_{ts}{ext or '.xlsx'}"

    out_df.to_excel(stamped_output_path, index=False)
    return len(out_df), stamped_output_path
