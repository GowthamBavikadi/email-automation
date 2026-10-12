.PHONY: help install test dry-run run resume clean

PYTHON := ./.venv/bin/python
PYTEST := ./.venv/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make install  - Install requirements into virtualenv"
	@echo "  make test     - Run pytest test suite"
	@echo "  make dry-run  - Simulate delivery run without sending emails"
	@echo "  make run      - Run live email delivery"
	@echo "  make resume   - Resume delivery (skip already contacted recipients)"
	@echo "  make clean    - Remove cache and temporary test files"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTEST) -v

dry-run:
	$(PYTHON) send.py --dry-run

run:
	$(PYTHON) send.py

resume:
	$(PYTHON) send.py --resume

clean:
	rm -rf __pycache__ emailer/__pycache__ tests/__pycache__ .pytest_cache
