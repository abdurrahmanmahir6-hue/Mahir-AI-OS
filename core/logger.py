"""
core/logger.py

Responsible for:
    - Central, consistent logging across the entire system.
    - Supporting DEBUG / INFO / WARNING / ERROR levels.
    - Providing one place to later add file logging and audit logging
      (MAFS Ch.10 — Audit Trail) without touching call sites elsewhere.
"""

from __future__ import annotations

import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

_CONFIGURED = False
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class JsonFormatter(logging.Formatter):
    """
    Minimal structured (JSON) log formatter.

    Extension point for MAFS Ch.10 (Audit Trail): a downstream log
    shipper or audit pipeline can consume one JSON object per line
    instead of parsing free-text log lines.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, _DATE_FORMAT),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
) -> None:
    """
    Configure the root logger once for the whole application.

    Args:
        level: Minimum level to emit ("DEBUG", "INFO", "WARNING", "ERROR").
        log_file: Optional path to also write logs to a file. The file
            handler rotates automatically (see max_bytes/backup_count)
            so a long-running process can't fill the disk with one
            unbounded log file.
        json_format: If True, emit structured JSON lines instead of
            the human-readable format. Useful once logs are shipped to
            an external audit/log-aggregation system (MAFS Ch.10).
        max_bytes: Rotate the log file after it reaches this size.
        backup_count: Number of rotated log files to keep.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())

    formatter: logging.Formatter
    formatter = (
        JsonFormatter()
        if json_format
        else logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    )

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger, configuring root logging with defaults first
    if configure_logging() hasn't been called yet (safe for early
    imports and unit tests that import a module in isolation).

    Args:
        name: Usually __name__ of the calling module.

    Returns:
        A standard library logging.Logger instance.
    """
    if not _CONFIGURED:
        configure_logging()
    return logging.getLogger(name)
