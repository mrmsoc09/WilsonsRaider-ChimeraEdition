"""
Vault client wrapper for secure secret access via HashiCorp Vault.
- Uses hvac when available; degrades with clear errors if not configured.
- Never exposes secrets to LLMs; returns handles or values only to trusted code paths.
"""
from __future__ import annotations
import os
from typing import Any, Optional
try:
    import hvac  # type: ignore
except Exception:  # pragma: no cover
    hvac = None  # allow import without hvac installed

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class VaultNotConfigured(Exception):
    pass

class VaultClient:
    def __init__(self, addr: Optional[str] = None, token: Optional[str] = None, namespace: Optional[str] = None):
        if hvac is None:
            raise VaultNotConfigured("hvac not installed. Add 'hvac' to requirements and configure Vault.")
        self.addr = addr or os.getenv("VAULT_ADDR")
        self.namespace = namespace or os.getenv("VAULT_NAMESPACE")
        self._token = token or os.getenv("VAULT_TOKEN")
        if not self.addr:
            raise VaultNotConfigured("VAULT_ADDR not set")
        self.client = hvac.Client(url=self.addr, token=self._token, namespace=self.namespace)
        if not self.client:  # pragma: no cover
            raise VaultNotConfigured("Failed to initialize hvac client")

    def is_ready(self) -> bool:
        if hvac is None:
            return False
        try:
            status = self.client.sys.read_health_status(method="GET")
            return bool(status and not status.get("sealed", True))
        except Exception:
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), reraise=True,
           retry=retry_if_exception_type(Exception))
    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """Read a secret at path; optionally return a single key from data."""
        resp = self.client.secrets.kv.v2.read_secret_version(path=path)
        data = resp.get("data", {}).get("data", {})
        return data.get(key) if key else data

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4), reraise=True,
           retry=retry_if_exception_type(Exception))
    def put_secret(self, path: str, data: dict) -> None:
        self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=data)
