#!/usr/bin/env bash
set -e

echo $'\nInstalling dependencies...'
python3 -m pip install -r requirements-dev.txt > /dev/null

echo $'\nRunning analysis...\n'
python3 -m ruff check . --extend-select I
python3 -m ruff format --check .
python3 -m pyrefly check --preset all .
