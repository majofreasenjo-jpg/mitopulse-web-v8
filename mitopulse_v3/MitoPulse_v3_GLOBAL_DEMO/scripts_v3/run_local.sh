#!/usr/bin/env bash
set -e
# Run backend + webapp (dev) in two terminals.
echo "Backend: cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py"
echo "Webapp:  cd webapp  && npm install && npm run dev"
