"""State tracker for persisting statements sent to each email address."""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class SentTracker:
    """Tracks and persists which problem statements each email has received."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        # Store internal mapping: normalized_email -> list of statement IDs
        self._data: Dict[str, List[str]] = {}
        self.load()

    def _normalize_email(self, email: str) -> str:
        return email.strip().lower()

    def load(self) -> None:
        """Load tracking data from disk. Initializes empty if file doesn't exist."""
        if not self.path.exists():
            logger.info("Sent tracker file not found at %s. Starting fresh.", self.path)
            self._data = {}
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                if isinstance(raw, dict):
                    # Ensure all values are lists of strings
                    self._data = {
                        self._normalize_email(k): [str(x) for x in v] if isinstance(v, list) else []
                        for k, v in raw.items()
                    }
                else:
                    logger.warning("Tracker file %s had non-dict root. Resetting.", self.path)
                    self._data = {}
        except Exception as e:
            logger.error("Failed to load tracker file %s: %s. Starting with empty data.", self.path, e)
            self._data = {}

    def get_used(self, email: str) -> Set[str]:
        """Return the set of statement IDs already sent to the given email."""
        norm = self._normalize_email(email)
        return set(self._data.get(norm, []))

    def has_received(self, email: str, stmt_id: str) -> bool:
        """Check if an email has already received a particular statement."""
        return str(stmt_id) in self.get_used(email)

    def mark_sent(self, email: str, stmt_id: str) -> None:
        """Record that a statement ID was sent to the given email."""
        norm = self._normalize_email(email)
        stmt_str = str(stmt_id)
        if norm not in self._data:
            self._data[norm] = []
        if stmt_str not in self._data[norm]:
            self._data[norm].append(stmt_str)

    def save(self) -> None:
        """Persist tracking data atomically to avoid file corruption."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        dir_name = self.path.parent

        # Atomic write pattern: write to temporary file then replace
        try:
            with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
                json.dump(self._data, tf, indent=2, ensure_ascii=False)
                temp_path = tf.name

            os.replace(temp_path, self.path)
            logger.debug("Tracker successfully saved to %s", self.path)
        except Exception as e:
            logger.error("Failed to save tracker to %s: %s", self.path, e)
            raise

    def get_all_tracked_emails(self) -> Set[str]:
        """Return all emails currently recorded in the tracker."""
        return set(self._data.keys())

    def get_stats(self) -> Dict[str, int]:
        """Return summary statistics of tracked deliveries."""
        total_emails = len(self._data)
        total_sent = sum(len(v) for v in self._data.values())
        return {
            "total_recipients_tracked": total_emails,
            "total_statements_delivered": total_sent,
        }
