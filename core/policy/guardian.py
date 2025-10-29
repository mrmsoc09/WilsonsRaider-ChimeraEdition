"""Policy engine (Guardian) for OPSEC, rate limiting, and execution gating."""
from __future__ import annotations
import time
import threading
from typing import Dict, Any
import os
import yaml

class PolicyEngine:
    def __init__(self, policy_path: str = "configs/policy.yaml"):
        self._lock = threading.Lock()
        self.config = self._load(policy_path)
        self._buckets: Dict[str, Dict[str, Any]] = {}

    def _load(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        # defaults
        return {
            "opsec": {"mode": "low_and_slow", "network_profile": "whitelist", "jitter_ms": [200, 1500]},
            "rate_limits": {"default_qpm": 10},
            "validation": {"redundancy": False, "profile": "safe"},
        }

    def allow_tool(self, tool: str) -> bool:
        tools = self.config.get("tools", {})
        rule = tools.get(tool, {"enabled": True})
        return bool(rule.get("enabled", True))

    def token_bucket(self, key: str, qpm: int | None = None) -> bool:
        now = time.time()
        with self._lock:
            bucket = self._buckets.setdefault(key, {"tokens": 0.0, "last": now})
            rate = (qpm or self.config.get("rate_limits", {}).get("default_qpm", 10)) / 60.0
            elapsed = now - bucket["last"]
            bucket["tokens"] = min(2 * rate, bucket["tokens"] + elapsed * rate)
            bucket["last"] = now
            if bucket["tokens"] >= 1.0:
                bucket["tokens"] -= 1.0
                return True
            return False

    def validation_redundancy(self) -> bool:
        return bool(self.config.get("validation", {}).get("redundancy", False))

    def validation_profile(self) -> str:
        return str(self.config.get("validation", {}).get("profile", "safe"))
