"""Tests for loader module (CSV recipients and JSON/TXT statements)."""

import json
from pathlib import Path
import pytest
from emailer.loader import load_recipients, load_statements


def test_load_recipients_csv_standard(tmp_path: Path):
    csv_file = tmp_path / "emails.csv"
    csv_file.write_text(
        "email,name\n"
        "Alice@EXAMPLE.com,Alice Smith\n"
        "bob@example.com,Bob Jones\n",
        encoding="utf-8",
    )

    recipients = load_recipients(csv_file)
    assert len(recipients) == 2
    assert recipients[0].email == "alice@example.com"  # normalized lowercase
    assert recipients[0].name == "Alice Smith"
    assert recipients[1].email == "bob@example.com"


def test_load_recipients_missing_column(tmp_path: Path):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("first_name,last_name\nJohn,Doe\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required 'email' column"):
        load_recipients(csv_file)


def test_load_statements_json_objects(tmp_path: Path):
    json_file = tmp_path / "statements.json"
    data = [
        {"id": "q1", "text": "Problem 1"},
        {"id": "q2", "text": "Problem 2"},
    ]
    json_file.write_text(json.dumps(data), encoding="utf-8")

    stmts = load_statements(json_file)
    assert len(stmts) == 2
    assert stmts[0].id == "q1"
    assert stmts[0].text == "Problem 1"


def test_load_statements_json_strings(tmp_path: Path):
    json_file = tmp_path / "questions.json"
    data = ["Question A", "Question B"]
    json_file.write_text(json.dumps(data), encoding="utf-8")

    stmts = load_statements(json_file)
    assert len(stmts) == 2
    assert stmts[0].id == "stmt-1"
    assert stmts[0].text == "Question A"


def test_load_statements_txt_lines(tmp_path: Path):
    txt_file = tmp_path / "questions.txt"
    txt_file.write_text(
        "# Comment line\n"
        "First problem statement\n"
        "\n"
        "Second problem statement\n",
        encoding="utf-8",
    )

    stmts = load_statements(txt_file)
    assert len(stmts) == 2
    assert stmts[0].text == "First problem statement"
    assert stmts[1].text == "Second problem statement"
