#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r backend/requirements.txt
if [ ! -f frontend/dist/index.html ]; then
  (cd frontend && npm ci --no-audit --no-fund && npm run build)
fi
echo 'Open http://127.0.0.1:8000. Press Ctrl+C to stop.'
exec .venv/bin/python -m uvicorn backend.app:create_app --factory --host 127.0.0.1 --port 8000
