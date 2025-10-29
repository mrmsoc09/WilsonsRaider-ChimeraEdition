#!/usr/bin/env bash
set -euo pipefail
exec uvicorn core.ui.server:app --host 0.0.0.0 --port 8080
