"""Selector module to pick a random, non-repeating problem statement for an email."""

import logging
import random
from typing import List, Optional
from emailer.models import Statement
from emailer.tracker import SentTracker

logger = logging.getLogger(__name__)


def pick_unused(
    email: str,
    statements: List[Statement],
    tracker: SentTracker,
    batch_assigned_ids: Optional[set[str]] = None,
) -> Optional[Statement]:
    """Pick a random unused problem statement for the given email address.

    Args:
        email: The recipient's email address.
        statements: The complete list of available statements in the bank.
        tracker: The persistent tracker tracking already delivered statement IDs.
        batch_assigned_ids: Optional set of statement IDs already assigned in current run.

    Returns:
        A randomly chosen Statement if an unused one exists, or None if the pool is exhausted.
    """
    if not statements:
        logger.warning("Statement pool is completely empty.")
        return None

    used_ids = tracker.get_used(email)
    unused_pool = [stmt for stmt in statements if stmt.id not in used_ids]

    if not unused_pool:
        logger.warning(
            "Statement pool exhausted for recipient %s (already received %d of %d statements).",
            email,
            len(used_ids),
            len(statements),
        )
        return None

    # Prefer statements that have not already been assigned in the current batch
    if batch_assigned_ids:
        fresh_in_batch = [s for s in unused_pool if s.id not in batch_assigned_ids]
        if fresh_in_batch:
            unused_pool = fresh_in_batch

    selected = random.choice(unused_pool)
    logger.debug(
        "Selected unused statement '%s' for %s (remaining unused: %d)",
        selected.id,
        email,
        len(unused_pool) - 1,
    )
    return selected


def get_unused_count(email: str, statements: List[Statement], tracker: SentTracker) -> int:
    """Return the number of statements available for the recipient."""
    used_ids = tracker.get_used(email)
    return sum(1 for s in statements if s.id not in used_ids)
