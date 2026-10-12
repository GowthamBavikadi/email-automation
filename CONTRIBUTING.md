# Contributing Guidelines

Thank you for your interest in contributing to **Unique Statement Email Automation**! We welcome bug reports, feature suggestions, and pull requests.

> Found a bug? [Open a bug report](https://github.com/gowthambavikadi/email-automation/issues/new?template=bug_report.yml)  
> Have an idea? [Open a feature request](https://github.com/gowthambavikadi/email-automation/issues/new?template=feature_request.yml)

---

## 🛠️ Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/<your-username>/email-automation.git
   cd email-automation
   ```

2. **Create Virtual Environment & Install**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Copy credentials template**:
   ```bash
   cp .env.example .env
   # Fill in your SMTP_USER, SMTP_PASS, SMTP_FROM
   ```

4. **Verify everything works**:
   ```bash
   make test       # 18 unit tests should pass
   make dry-run    # Preview allocations with no emails sent
   ```

---

## 🌿 Git & Branch Workflow

Even as the only contributor, working through branches and PRs keeps your git history clean:

1. Create a branch for your change:
   ```bash
   git checkout -b feat/add-sqlite-backend
   ```
2. Make your changes with focused commits using [Conventional Commits](https://www.conventionalcommits.org/) format:
   ```
   feat(tracker): add SQLite backend as alternative to JSON
   fix(sender): handle SMTPRecipientsRefused exception
   docs(readme): update getting started section
   test(selector): add edge case for empty statement pool
   ```
3. Ensure all tests pass:
   ```bash
   pytest -v
   ```
4. Push and open a Pull Request against `main`.

---

## 📜 Code Standards

| Concern | Standard |
|---|---|
| **Formatting** | PEP 8 · max line length: 100 characters |
| **Type Annotations** | Required on all public functions and class methods |
| **Docstrings** | All public functions must have a clear docstring |
| **Tests** | New behavior must have corresponding pytest tests |
| **Secrets** | Never commit real credentials. Always use `.env` and `.env.example` |

---

## 🔁 CI Checks

Every push runs the GitHub Actions CI pipeline across Python 3.10, 3.11, 3.12, and 3.13. PRs will not be merged unless CI passes.
