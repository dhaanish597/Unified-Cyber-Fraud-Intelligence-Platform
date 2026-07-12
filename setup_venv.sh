#!/usr/bin/env bash
# Python virtual environment setup (bash / Git Bash / macOS / Linux)
# Usage: ./setup_venv.sh
set -euo pipefail

python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Done. Activate in future sessions with: source .venv/bin/activate"
