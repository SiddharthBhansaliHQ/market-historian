#!/usr/bin/env bash
set -e

echo $'\nConfiguring virtual environment...'
python3 -m venv .venv > /dev/null
.venv/bin/python -m pip install --upgrade pip > /dev/null
.venv/bin/python -m pip install -r requirements-dev.txt > /dev/null

echo $'\nRunning linter, formatter, type checker, & tests...\n'
.venv/bin/python -m ruff check . --extend-select I --fix
.venv/bin/python -m ruff format .
.venv/bin/python -m pyrefly check --python-interpreter-path .venv/bin/python --preset all .
.venv/bin/python -m pytest tests/

echo $'\nStarting FastAPI...'
exec .venv/bin/python -m fastapi dev main.py
