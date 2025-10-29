from __future__ import annotations
import os
from typing import Any, Dict, Optional
import httpx
from core.policy.guardian import PolicyEngine

class N8nClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, guardian: Optional[PolicyEngine] = None):
        self.guardian = guardian or PolicyEngine()
        self.base_url = base_url or os.getenv("N8N_BASE_URL", "http://localhost:5678")
        self.token = token or os.getenv("N8N_API_KEY")
        self.http = httpx.Client(timeout=20.0)

    def trigger(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.guardian.token_bucket("n8n", qpm=self.guardian.config.get("rate_limits",{}).get("providers",{}).get("github",2)):
            # reuse provider slot config for example
            pass
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["X-N8N-API-KEY"] = self.token
        r = self.http.post(f"{self.base_url}/webhook/{workflow_id}", json=payload, headers=headers)
        r.raise_for_status()
        return r.json() if r.headers.get('content-type','').startswith('application/json') else {"status": r.status_code}
