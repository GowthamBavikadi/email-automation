"""CLI argument parsing and logging initialization."""

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_path: Path | str = "logs/send.log", verbose: bool = False) -> logging.Logger:
    """Configure dual logging: console (stdout) and rotating file."""
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    level = logging.DEBUG if verbose else logging.INFO

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers on re-initialization
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating File Handler (5 MB per file, max 5 backups)
    file_handler = RotatingFileHandler(
        filename=str(path),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG in log files
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    return root_logger


def parse_args(args=None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="send.py",
        description="Automated email delivery of unique problem statements with state tracking.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without sending emails or modifying tracker.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Limit execution to the first N recipients.",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip recipients who have already received a statement in previous runs.",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        metavar="PATH",
        help="Path to YAML configuration file (default: config.yaml).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug output.",
    )

    return parser.parse_args(args)
