"""Preflight checks: dependencies, network, Vault reachability, OPSEC profile.
Outputs JSON summary for CI/CD and GUI consumption.
"""
from __future__ import annotations
import json, shutil, subprocess, os, sys
from typing import Dict

def check_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def vault_status() -> Dict:
    addr = os.getenv("VAULT_ADDR")
    try:
        from core.integrations.vault_client import VaultClient
        vc = VaultClient(addr=addr)
        return {"configured": True, "ready": vc.is_ready(), "addr": addr}
    except Exception as e:  # hvac missing or not configured
        return {"configured": False, "ready": False, "addr": addr, "error": str(e)}

def main() -> int:
    deps = {
        "docker": check_cmd("docker"),
        "proxychains4": check_cmd("proxychains4"),
        "git": check_cmd("git"),
        "nuclei": check_cmd("nuclei"),
        "msfconsole": check_cmd("msfconsole"),
        "python3": check_cmd("python3"),
    }
    net_profile = os.getenv("WR_NETWORK_PROFILE", "whitelist")
    result = {
        "deps": deps,
        "vault": vault_status(),
        "network_profile": net_profile,
        "recommendations": []
    }
    for k,v in deps.items():
        if not v:
            result["recommendations"].append(f"Install dependency: {k}")
    print(json.dumps(result, indent=2))
    return 0 if all(deps.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
