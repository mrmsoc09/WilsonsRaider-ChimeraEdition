#!/usr/bin/env python3
from __future__ import annotations
import os
from pathlib import Path

ENV_PATH = Path('.env')

print("=== WilsonsRaider Onboarding (interactive) ===")
print("Press Enter to skip a field and keep current or empty value. You can rerun anytime.")

current = {}
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
            current[k.strip()] = v.strip()

def prompt(key: str, label: str) -> str:
    existing = current.get(key, "")
    v = input(f"{label} [{existing}]: ").strip()
    return v or existing

updates = {}
updates['VAULT_ADDR'] = prompt('VAULT_ADDR', 'HashiCorp Vault Address (e.g., http://127.0.0.1:8200)')
updates['VAULT_TOKEN'] = prompt('VAULT_TOKEN', 'HashiCorp Vault Token (use AppRole later for prod)')
updates['N8N_BASE_URL'] = prompt('N8N_BASE_URL', 'n8n Base URL (e.g., http://localhost:5678)')
updates['N8N_API_KEY'] = prompt('N8N_API_KEY', 'n8n API Key')
# Database URL optional; default remains SQLite
updates['DATABASE_URL'] = prompt('DATABASE_URL', 'Database URL (empty for SQLite default)')

# Merge and write
current.update({k: v for k, v in updates.items() if v is not None})
lines = [f"{k}={v}" for k, v in current.items()]
ENV_PATH.write_text("\n".join(lines) + "\n")
print(f"Saved .env with {len(current)} keys. You can edit it manually or rerun this script.")
