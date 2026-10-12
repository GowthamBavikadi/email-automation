<div align="center">

# 📬 Unique Content Email Automation

### *A fault-tolerant Python dispatch engine that distributes given content(images, text, links)  to candidates, interviewees, and participants over SMTP.*

[![CI Pipeline](https://github.com/gowthambavikadi/email-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/gowthambavikadi/email-automation/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?style=flat-square)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen.svg?style=flat-square)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-black%2Fruff-000000.svg?style=flat-square)](https://github.com/astral-sh/ruff)

<br/>

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │  $ python send.py --dry-run                                            │
  │  [INFO] [emailer.main]: MODE: *** DRY RUN ***                          │
  │  [INFO] [emailer.loader]: Loaded 5 recipient(s), 10 unique statement(s)│
  │  [INFO] [emailer.main]: [1/5] Would send 'stmt-003' -> alice@corp.com  │
  │  [INFO] [emailer.main]: [2/5] Would send 'stmt-007' -> bob@corp.com    │
  │  [INFO] [emailer.main]: EXECUTION SUMMARY: 5 Processed | 0 Duplicates  │
  └────────────────────────────────────────────────────────────────────────┘
```

</div>

---

##  Highlights

- **Zero Duplicates Ever**: Atomic JSON tracker (`sent_tracker.json`) guarantees a participant never receives the same assignment across multiple runs.
- **Batch-Level Diversity**: Within any single delivery batch, participants receive distinct items from the pool.
- **Safe Dry-Run Mode**: Simulate allocations and preview generated content without sending network requests or modifying saved state.
- **Resilient SMTP Delivery**: Handles network drops and throttling with automatic exponential backoff retries.
- **Dual-Format Templating**: Produces clean plaintext and responsive GitHub-styled HTML emails via Jinja2.
- **Production-Ready CLI**: Flags for `--dry-run`, `--limit N`, `--resume`, and custom `--config`.

---

##  Tech Stack

- **Language**: Python 3.10+
- **Data Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Email Templating**: [Jinja2](https://palletsprojects.com/p/jinja/)
- **Configuration**: YAML (`pyyaml`) with environment variable interpolation (`python-dotenv`)
- **Testing**: [pytest](https://docs.pytest.org/) & `pytest-mock`
- **CI/CD**: GitHub Actions (testing across Python 3.10 – 3.13)

---

##  Project Structure

```text
email_automation/
├── .github/
│   ├── workflows/ci.yml              # GitHub Actions CI (Python 3.10–3.13)
│   └── ISSUE_TEMPLATE/               # Bug report & feature request forms
├── emailer/
│   ├── config.py                     # Pydantic v2 settings & ${ENV} expansion
│   ├── loader.py                     # CSV and JSON/TXT file ingestors
│   ├── models.py                     # Recipient and Statement schemas
│   ├── tracker.py                    # Atomic JSON state manager
│   ├── selector.py                   # Non-repeating random picker
│   ├── sender.py                     # SMTP engine with retry backoff
│   ├── renderer.py                   # Jinja2 template engine
│   └── cli.py                        # Argparse & rotating logging
├── templates/
│   ├── statement.txt                 # Plaintext Jinja2 template
│   └── statement.html                # GitHub-styled HTML email
├── tests/                            # pytest suite (18 unit tests)
├── .env.example                      # Safe credentials template
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile                          # make test / dry-run / run / clean
├── config.yaml                       # SMTP, paths, runtime settings
├── emails.csv                        # Your recipient list
├── send.py                           # CLI entrypoint
├── statements.json                   # Your statement bank
└── requirements.txt
```

---

##  Getting Started

Follow these exact steps to run the project on a clean machine:

### 1. Clone & Set Up

```bash
git clone https://github.com/gowthambavikadi/email-automation.git
cd email-automation

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure SMTP Credentials

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Add your SMTP credentials:

```ini
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_16_digit_app_password
SMTP_FROM=your_email@gmail.com
```

> **Gmail Users**: Generate an [App Password](https://myaccount.google.com/apppasswords) under Google Account Security. Any spaces in the 16-character code are sanitized automatically.

### 3. Provide Your Recipients & Statements

- **`emails.csv`** (Columns: `email`, `name` optional):
  ```csv
  email,name
  candidate1@example.com,Alice
  candidate2@example.com,Bob
  ```

- **`statements.json`** (JSON array or one per line in `statements.txt`):
  ```json
  [
    { "id": "q-1", "text": "Design an in-memory distributed cache." },
    { "id": "q-2", "text": "Implement a rate limiter using token bucket." }
  ]
  ```

---

##  Usage Examples

### 1. Dry Run Simulation (Safe Preview)
```bash
python send.py --dry-run
```
*Simulates all allocations, verifies templates, and logs outputs without transmitting emails or updating state.*

### 2. Send to a Test Batch
```bash
python send.py --limit 2
```

### 3. Resume an Interrupted Run
```bash
python send.py --resume
```
*Skips anyone who has already received an email and continues with the rest.*

### 4. Full Live Dispatch
```bash
python send.py
```

### CLI Options

| Flag | Type | Description |
| :--- | :--- | :--- |
| `--dry-run` | Flag | Simulates execution, logs assigned items, modifies **no** records. |
| `--limit N` | Integer | Slices processing to the first $N$ recipients. |
| `--resume` | Flag | Automatically skips recipients already logged in `sent_tracker.json`. |
| `--config PATH` | String | Path to custom YAML configuration (defaults to `config.yaml`). |
| `-v, --verbose` | Flag | Enables detailed `DEBUG` console logging. |

---

##  Testing

The test suite runs 18 unit tests covering mocked SMTP transport, retry logic, state persistence, and parsing edge cases:

```bash
make test
# or
pytest -v
```

```text
tests/test_loader.py .....                                               [ 27%]
tests/test_selector.py ....                                              [ 50%]
tests/test_sender.py ....                                                [ 72%]
tests/test_tracker.py .....                                              [100%]

============================== 18 passed in 0.08s ==============================
```

---

##  Roadmap & Future Work

- [x] Non-repeating random selection with persistent atomic state tracking
- [x] Gmail App Password auto-sanitization & STARTTLS/SSL support
- [x] Jinja2 responsive HTML & plaintext templates
- [x] GitHub Actions automated multi-version CI pipeline
- [ ] SQLite/PostgreSQL storage backend option for massive contact lists (>100k)
- [ ] Open/Click tracking via webhooks & lightweight tracking pixel
- [ ] Interactive terminal progress bar using `rich` / `tqdm`
- [ ] Attachment support for personalized problem description PDFs

---

##  Repository Information & About Box

When publishing this repository to GitHub, use these suggested settings:

- **Description**: `Automated, fault-tolerant Python dispatch engine delivering unique, non-repeating problem statements over SMTP with persistent state tracking.`
- **Topics / Tags**: `python`, `email-automation`, `smtp`, `hackathon`, `jinja2`, `cli`, `automation`, `pydantic`
- **License**: [MIT License](LICENSE)

---

##  Author & Contact

- **Author**: Gowtham Bavikadi
- **GitHub**: [@gowthambavikadi](https://github.com/gowthambavikadi)
- **Feedback & Issues**: [Open an Issue](https://github.com/gowthambavikadi/email-automation/issues)
