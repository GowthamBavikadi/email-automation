# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- SQLite/PostgreSQL backend for large-scale deployments (>100k contacts)
- Open/click tracking via lightweight webhook pixel
- Interactive terminal progress bar (`rich` / `tqdm`)
- Attachment support for personalized PDF problem statements

---

## [1.0.0] - 2026-10-12

### Added
- **Core CLI Dispatch Engine** (`send.py`): Assigns and delivers unique statements over SMTP with flags `--dry-run`, `--limit N`, `--resume`, `--config`, and `--verbose`.
- **Persistent State Tracker** (`emailer/tracker.py`): `SentTracker` using atomic JSON writes (`sent_tracker.json`) guaranteeing non-repeating assignments per recipient across sessions.
- **Batch Uniqueness**: Preference logic ensuring all recipients within a single run receive distinct statements.
- **Robust SMTP Sender** (`emailer/sender.py`): STARTTLS & SSL support, auto-sanitization of Google App Passwords (strips spaces from 16-char codes), exponential backoff retries.
- **Jinja2 Templating** (`emailer/renderer.py`): Plaintext (`templates/statement.txt`) and GitHub-styled responsive HTML (`templates/statement.html`) with `{{ name }}` and `{{ statement }}` variables.
- **Flexible Data Loaders** (`emailer/loader.py`): Reads recipient CSV files and statement JSON or newline-separated TXT banks. Case-insensitive email normalization. Auto-detects CSV delimiter.
- **Pydantic v2 Configuration** (`emailer/config.py`): Full `${ENV_VAR}` and `${VAR:-default}` expansion from `.env` and `config.yaml`.
- **Comprehensive Test Suite**: 18 unit tests covering mocked SMTP delivery, retry backoff, tracker persistence, and loader edge cases.
- **GitHub Actions CI** (`.github/workflows/ci.yml`): Matrix testing across Python 3.10, 3.11, 3.12, and 3.13.
- **Community Files**: `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE` (MIT), issue templates (bug, feature), and PR template.
- **Developer Tooling**: `Makefile` shortcuts (`test`, `dry-run`, `run`, `resume`, `clean`) and `pyproject.toml` with packaging metadata.
