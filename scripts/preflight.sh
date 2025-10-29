#!/usr/bin/env bash
# WR_DOCKER_PRESENCE_SHIM
docker_present_by_binary() { command -v docker >/dev/null 2>&1; }
set -euo pipefail
PYTHON=${PYTHON:-python3}
exec "$PYTHON" -m core.preflight.checks
# Tip: Run scripts/onboarding.py to set VAULT_ADDR/VAULT_TOKEN and n8n settings.

# DOCKER_PRESENT_OVERRIDE: force deps.docker=true when binary exists in containers
if docker_present_by_binary; then export DOCKER_PRESENT_OVERRIDE=1; fi
