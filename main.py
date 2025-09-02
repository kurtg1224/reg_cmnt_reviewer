from __future__ import annotations

import argparse
import os

from src.utils.logging import get_logger
from src.orchestrator import process_file


logger = get_logger(__name__)


def cmd_process(args: argparse.Namespace) -> None:
    """Run Task One & Two over the input Excel and write results to output Excel."""
    n, out = process_file(
        input_path=args.input,
        output_path=args.output,
        text_column=args.text_column,
        uid_column=args.uid_column,
        name_column=args.name_column,
        date_column=args.date_column,
        processes=args.processes,
    )
    logger.info("Processed %s rows -> %s", n, out)


def cmd_cluster(args: argparse.Namespace) -> None:
    """Cluster themes from a processed results spreadsheet into labeled groups."""
    # Lazy import to avoid importing clustering when disabled
    from src.comment_theme_clusterer import cluster_themes
    n, out = cluster_themes(
        input_path=args.input,
        output_path=args.output,
        themes_column=args.themes_column,
        min_cluster_size=args.min_cluster_size,
    )
    logger.info("Produced %s clusters -> %s", n, out)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser with 'process' (default) and optional 'cluster' subcommands."""
    p = argparse.ArgumentParser(description="SSA Regulation Comment Reviewer")
    sub = p.add_subparsers(dest="command", required=True)

    p_proc = sub.add_parser("process", help="Process comments (Task One & Two)")
    p_proc.add_argument("--input", required=True, help="Path to input Excel file")
    p_proc.add_argument("--output", required=True, help="Path to output Excel file")
    p_proc.add_argument("--text-column", default="comment", help="Name of the text column in input Excel")
    p_proc.add_argument("--uid-column", default=None)
    p_proc.add_argument("--name-column", default=None)
    p_proc.add_argument("--date-column", default=None)
    p_proc.add_argument("--processes", type=int, default=None, help="Max worker processes")
    p_proc.set_defaults(func=cmd_process)

    # Clustering subcommand disabled by default. Set DISABLE_CLUSTER=0 to enable.
    disable_cluster = os.getenv("DISABLE_CLUSTER", "1").lower() in ("1", "true", "yes")
    if not disable_cluster:
        p_clu = sub.add_parser("cluster", help="Cluster themes from processed results")
        p_clu.add_argument("--input", required=True, help="Path to processed results Excel file")
        p_clu.add_argument("--output", required=True, help="Path to theme clusters Excel file")
        p_clu.add_argument("--themes-column", default="themes", help="Name of the themes column in results Excel")
        p_clu.add_argument("--min-cluster-size", type=int, default=5)
        p_clu.set_defaults(func=cmd_cluster)

    return p


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
