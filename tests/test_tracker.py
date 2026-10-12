"""Tests for SentTracker persistence and querying."""

import json
from pathlib import Path
from emailer.tracker import SentTracker


def test_tracker_initializes_empty_file(tmp_path: Path):
    tracker_file = tmp_path / "sent_tracker.json"
    tracker = SentTracker(tracker_file)

    assert tracker.get_used("test@example.com") == set()
    assert tracker.get_stats()["total_recipients_tracked"] == 0


def test_tracker_mark_and_retrieve(tmp_path: Path):
    tracker_file = tmp_path / "sent_tracker.json"
    tracker = SentTracker(tracker_file)

    tracker.mark_sent("user@example.com", "stmt-1")
    tracker.mark_sent("user@example.com", "stmt-2")
    # Duplicate mark should not duplicate in list
    tracker.mark_sent("user@example.com", "stmt-1")

    assert tracker.get_used("user@example.com") == {"stmt-1", "stmt-2"}
    assert tracker.has_received("user@example.com", "stmt-1") is True
    assert tracker.has_received("user@example.com", "stmt-3") is False


def test_tracker_email_case_insensitivity(tmp_path: Path):
    tracker_file = tmp_path / "sent_tracker.json"
    tracker = SentTracker(tracker_file)

    tracker.mark_sent("Alice.Smith@Example.COM", "stmt-42")

    assert tracker.has_received("alice.smith@example.com", "stmt-42") is True
    assert tracker.get_used("ALICE.SMITH@EXAMPLE.COM") == {"stmt-42"}


def test_tracker_persistence_across_instances(tmp_path: Path):
    tracker_file = tmp_path / "sent_tracker.json"
    tracker1 = SentTracker(tracker_file)
    tracker1.mark_sent("bob@example.com", "stmt-a")
    tracker1.mark_sent("alice@example.com", "stmt-b")
    tracker1.save()

    # Verify JSON structure on disk
    with open(tracker_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {
        "bob@example.com": ["stmt-a"],
        "alice@example.com": ["stmt-b"],
    }

    # Verify new instance loads the saved data
    tracker2 = SentTracker(tracker_file)
    assert tracker2.get_used("bob@example.com") == {"stmt-a"}
    assert tracker2.get_used("alice@example.com") == {"stmt-b"}
    assert tracker2.get_stats()["total_recipients_tracked"] == 2
    assert tracker2.get_stats()["total_statements_delivered"] == 2


def test_tracker_handles_corrupt_file(tmp_path: Path):
    tracker_file = tmp_path / "corrupt_tracker.json"
    tracker_file.write_text("invalid json content!!!", encoding="utf-8")

    # Should not raise exception, logs error and initializes empty
    tracker = SentTracker(tracker_file)
    assert tracker.get_used("anyone@example.com") == set()
