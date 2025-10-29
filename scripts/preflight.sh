#!/usr/bin/env bash
set -euo pipefail
PYTHON=${PYTHON:-python3}
exec "$PYTHON" -m core.preflight.checks
# Tip: Run scripts/onboarding.py to set VAULT_ADDR/VAULT_TOKEN and n8n settings.
