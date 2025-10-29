#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
UVI="uvicorn"
if [ -x "venv/bin/uvicorn" ]; then UVI="venv/bin/uvicorn"; fi
exec "$UVI" app.main:app --host 0.0.0.0 --port 8080
