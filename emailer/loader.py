"""Data loaders for recipient emails and problem statement banks."""

import csv
import json
import logging
import uuid
from pathlib import Path
from typing import List
from emailer.models import Recipient, Statement

logger = logging.getLogger(__name__)


def load_recipients(file_path: Path | str) -> List[Recipient]:
    """Load recipients from a CSV file.

    Expects columns: 'email' (required) and 'name' (optional).
    Column names are case-insensitive.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Recipient file not found: {path.resolve()}")

    recipients: List[Recipient] = []
    seen_in_file = set()

    with open(path, "r", encoding="utf-8-sig") as f:
        # Detect delimiter or default to comma
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        except Exception:
            dialect = csv.excel

        reader = csv.DictReader(f, dialect=dialect)
        if not reader.fieldnames:
            logger.warning("Empty CSV file: %s", path)
            return []

        # Find email and name column mappings
        field_map = {fn.strip().lower(): fn for fn in reader.fieldnames if fn}
        email_col = field_map.get("email") or field_map.get("email_address") or field_map.get("mail")
        name_col = field_map.get("name") or field_map.get("full_name") or field_map.get("username")

        if not email_col:
            raise ValueError(f"CSV file {path} missing required 'email' column. Found columns: {reader.fieldnames}")

        for line_num, row in enumerate(reader, start=2):
            raw_email = row.get(email_col, "")
            raw_name = row.get(name_col, "") if name_col else ""

            if not raw_email or not raw_email.strip():
                continue

            try:
                recipient = Recipient(email=raw_email, name=raw_name)
                # Avoid duplicate rows in the same input file
                if recipient.email in seen_in_file:
                    logger.debug("Skipping duplicate email in CSV line %d: %s", line_num, recipient.email)
                    continue
                seen_in_file.add(recipient.email)
                recipients.append(recipient)
            except Exception as e:
                logger.warning("Skipping invalid row %d in %s: %s", line_num, path, e)

    logger.info("Loaded %d valid recipient(s) from %s", len(recipients), path)
    return recipients


def load_statements(file_path: Path | str) -> List[Statement]:
    """Load problem statements from JSON or TXT file.

    JSON formats supported:
    - List of dicts: [{"id": "...", "text": "..."}] (or "statement" / "question")
    - List of strings: ["Problem 1", "Problem 2"]

    TXT format supported:
    - One statement per line.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Statement file not found: {path.resolve()}")

    statements: List[Statement] = []
    seen_ids = set()

    if path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError(f"JSON statements file {path} must contain a list/array of items")

        for idx, item in enumerate(raw_data):
            if isinstance(item, dict):
                stmt_id = str(item.get("id") or str(uuid.uuid4()))
                stmt_text = str(item.get("text") or item.get("statement") or item.get("question") or "").strip()
            elif isinstance(item, str):
                stmt_id = f"stmt-{idx + 1}"
                stmt_text = item.strip()
            else:
                logger.warning("Skipping unrecognized statement item at index %d", idx)
                continue

            if not stmt_text:
                continue

            if stmt_id in seen_ids:
                stmt_id = f"{stmt_id}-{uuid.uuid4().hex[:6]}"
            seen_ids.add(stmt_id)

            statements.append(Statement(id=stmt_id, text=stmt_text))

    elif path.suffix.lower() in (".txt", ".md"):
        with open(path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("#"):
                    continue
                stmt_id = f"stmt-{idx}"
                statements.append(Statement(id=stmt_id, text=clean_line))
    else:
        raise ValueError(f"Unsupported file format for statements: {path.suffix}. Use .json or .txt")

    logger.info("Loaded %d unique statement(s) from %s", len(statements), path)
    return statements
