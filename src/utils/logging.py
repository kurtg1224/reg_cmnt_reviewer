import logging
import os
from typing import Optional


_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _configure_root_logger() -> None:
    """Configure the root logger once using LOG_LEVEL env (default INFO)."""
    if getattr(_configure_root_logger, "_configured", False):
        return
    logging.basicConfig(
        level=getattr(logging, _LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    _configure_root_logger._configured = True  # type: ignore[attr-defined]


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module logger after ensuring root logger is configured."""
    _configure_root_logger()
    return logging.getLogger(name or __name__)
