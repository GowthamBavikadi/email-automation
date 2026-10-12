"""Tests for statement selection and non-repeating logic."""

from pathlib import Path
from emailer.models import Statement
from emailer.selector import pick_unused, get_unused_count
from emailer.tracker import SentTracker


def test_pick_unused_picks_from_available(tmp_path: Path):
    tracker = SentTracker(tmp_path / "tracker.json")
    statements = [
        Statement(id="stmt-1", text="Problem 1"),
        Statement(id="stmt-2", text="Problem 2"),
    ]

    selected = pick_unused("user@example.com", statements, tracker)
    assert selected is not None
    assert selected.id in {"stmt-1", "stmt-2"}


def test_pick_unused_never_repeats(tmp_path: Path):
    tracker = SentTracker(tmp_path / "tracker.json")
    statements = [
        Statement(id="stmt-1", text="Problem 1"),
        Statement(id="stmt-2", text="Problem 2"),
        Statement(id="stmt-3", text="Problem 3"),
    ]

    # Pre-mark stmt-1 and stmt-3 as sent
    tracker.mark_sent("user@example.com", "stmt-1")
    tracker.mark_sent("user@example.com", "stmt-3")

    # Only stmt-2 remains
    selected = pick_unused("user@example.com", statements, tracker)
    assert selected is not None
    assert selected.id == "stmt-2"


def test_pick_unused_returns_none_when_exhausted(tmp_path: Path):
    tracker = SentTracker(tmp_path / "tracker.json")
    statements = [
        Statement(id="stmt-1", text="Problem 1"),
        Statement(id="stmt-2", text="Problem 2"),
    ]

    tracker.mark_sent("user@example.com", "stmt-1")
    tracker.mark_sent("user@example.com", "stmt-2")

    # Both exhausted
    assert get_unused_count("user@example.com", statements, tracker) == 0
    selected = pick_unused("user@example.com", statements, tracker)
    assert selected is None


def test_pick_unused_independent_per_email(tmp_path: Path):
    tracker = SentTracker(tmp_path / "tracker.json")
    statements = [
        Statement(id="stmt-1", text="Problem 1"),
    ]

    # Email 1 has received stmt-1
    tracker.mark_sent("user1@example.com", "stmt-1")

    # Email 1 gets None (exhausted)
    assert pick_unused("user1@example.com", statements, tracker) is None

    # Email 2 has not received stmt-1 yet, should get it
    selected2 = pick_unused("user2@example.com", statements, tracker)
    assert selected2 is not None
    assert selected2.id == "stmt-1"
