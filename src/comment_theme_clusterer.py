from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import hdbscan

from src.llm.azure_openai_client import embed_texts
from src.utils.logging import get_logger


logger = get_logger(__name__)


def _parse_themes_cell(cell: Any) -> List[str]:
    """Parse a cell value into a clean list of theme strings.

    Accepts JSON array strings, Python lists, or delimited strings; returns trimmed non-empty items.
    """
    if cell is None:
        return []
    if isinstance(cell, list):
        return [str(x).strip() for x in cell if str(x).strip()]
    s = str(cell).strip()
    if not s:
        return []
    try:
        data = json.loads(s)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        pass
    # Fallback: treat as semicolon/comma separated
    parts = [p.strip() for p in re.split(r"[;,]", s)]  # type: ignore[name-defined]
    return [p for p in parts if p]


def _summarize_clusters(themes: List[str], labels: np.ndarray, X: np.ndarray) -> pd.DataFrame:
    """Build a compact summary dataframe for clusters with exemplar labels and counts."""
    df = pd.DataFrame({"theme": themes, "cluster_id": labels})
    rows = []
    for cid in sorted(set(labels)):
        if cid == -1:
            # treat noise as its own bucket
            mask = labels == -1
            count = int(mask.sum())
            if count == 0:
                continue
            sample = df[df.cluster_id == -1].theme.head(5).tolist()
            rows.append({
                "cluster_id": int(cid),
                "cluster_label": "noise",
                "count": count,
                "example_themes": json.dumps(sample, ensure_ascii=False),
                "algorithm": "HDBSCAN",
            })
            continue
        mask = labels == cid
        idxs = np.where(mask)[0]
        if len(idxs) == 0:
            continue
        centroid = X[idxs].mean(axis=0, keepdims=True)
        dists = np.linalg.norm(X[idxs] - centroid, axis=1)
        medoid_idx = idxs[int(np.argmin(dists))]
        exemplar = themes[medoid_idx]
        sample = [themes[i] for i in idxs[:5]]
        rows.append({
            "cluster_id": int(cid),
            "cluster_label": exemplar,
            "count": int(mask.sum()),
            "example_themes": json.dumps(sample, ensure_ascii=False),
            "algorithm": "HDBSCAN",
        })
    return pd.DataFrame(rows).sort_values(by=["cluster_id"]).reset_index(drop=True)


def cluster_themes(
    input_path: str,
    output_path: str,
    themes_column: str = "themes",
    min_cluster_size: int = 5,
) -> Tuple[int, str]:
    """Cluster themes from a results spreadsheet and write a cluster summary Excel.

    Returns the number of clusters (rows) written and the output path.
    """
    df = pd.read_excel(input_path)
    if themes_column not in df.columns:
        raise ValueError(f"Missing themes column: {themes_column}")

    # Explode into a single list of themes
    all_themes: List[str] = []
    for cell in df[themes_column].tolist():
        all_themes.extend(_parse_themes_cell(cell))

    # Deduplicate while preserving counts
    # For clustering, use unique themes; for counts we use occurrences via labels mapping later
    unique_themes = sorted(set(t for t in all_themes if t))
    if len(unique_themes) == 0:
        # Nothing to cluster
        empty = pd.DataFrame(columns=["cluster_id", "cluster_label", "count", "example_themes", "algorithm"])
        empty.to_excel(output_path, index=False)
        return 0, output_path

    X = embed_texts(unique_themes)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    # Try HDBSCAN first
    hdb = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    labels_unique = hdb.fit_predict(Xs)

    # If poor clustering (all noise or single cluster), fallback to KMeans with silhouette selection
    valid_labels = set(int(l) for l in labels_unique if l != -1)
    if len(valid_labels) <= 1 and len(unique_themes) >= 2:
        max_k = min(50, max(2, len(unique_themes)))
        best_k = None
        best_score = -1.0
        best_labels = None
        for k in range(2, max_k + 1):
            km = KMeans(n_clusters=k, n_init=10, random_state=42)
            klabels = km.fit_predict(Xs)
            try:
                score = silhouette_score(Xs, klabels)
            except Exception:
                continue
            if score > best_score:
                best_score = score
                best_k = k
                best_labels = klabels
        if best_labels is not None:
            labels_unique = best_labels  # type: ignore[assignment]

    # Build mapping from unique_themes to labels
    theme_to_label = {t: int(l) for t, l in zip(unique_themes, labels_unique)}

    # Expand counts per cluster using original occurrences
    labels_for_all = np.array([theme_to_label.get(t, -1) for t in all_themes], dtype=int)

    # Summarize clusters using embeddings of unique themes
    summary = _summarize_clusters(unique_themes, np.array(list(theme_to_label.values())), Xs)

    # Recompute counts from all occurrences
    counts = pd.Series(labels_for_all).value_counts().to_dict()
    summary["count"] = summary["cluster_id"].map(lambda cid: int(counts.get(int(cid), 0)))

    summary.to_excel(output_path, index=False)
    return len(summary), output_path
