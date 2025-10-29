from __future__ import annotations
import os, time, sqlite3, json
from typing import Any, Dict, List, Optional
import httpx
from core.policy.guardian import PolicyEngine

DB_PATH = os.getenv("WR_CACHE_DB", "data/cache.db")
NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

class NVDClient:
    def __init__(self, guardian: Optional[PolicyEngine] = None):
        self.guardian = guardian or PolicyEngine()
        self._ensure_db()
        self.api_key = self._load_api_key()
        self.http = httpx.Client(timeout=20.0)

    def _load_api_key(self) -> Optional[str]:
        # Try Vault first
        try:
            from core.integrations.vault_client import VaultClient
            vc = VaultClient()
            k = vc.get_secret("integrations/nvd", "api_key")
            if k:
                return k
        except Exception:
            pass
        return os.getenv("NVD_API_KEY")

    def _ensure_db(self) -> None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as c:
            c.execute("CREATE TABLE IF NOT EXISTS nvd_meta (k TEXT PRIMARY KEY, v TEXT)")
            c.execute("""
            CREATE TABLE IF NOT EXISTS nvd_cves (
              id TEXT PRIMARY KEY,
              json TEXT NOT NULL,
              last_seen INTEGER NOT NULL
            )
            """)

    def _cache_put(self, cves: List[Dict[str, Any]]) -> None:
        now = int(time.time())
        with sqlite3.connect(DB_PATH) as c:
            for item in cves:
                cid = item.get("cve", {}).get("id") or item.get("id")
                if not cid:
                    continue
                c.execute(
                    "REPLACE INTO nvd_cves(id, json, last_seen) VALUES(?,?,?)",
                    (cid, json.dumps(item), now),
                )

    def _api_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.guardian.token_bucket("nvd", qpm=self.guardian.config.get("rate_limits",{}).get("providers",{}).get("nvd",3)):
            time.sleep(1.0)
        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key
        r = self.http.get(NVD_API, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    def query_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(DB_PATH) as c:
            row = c.execute("SELECT json FROM nvd_cves WHERE id=?", (cve_id,)).fetchone()
            if row:
                return json.loads(row[0])
        # fetch if not cached
        data = self._api_get({"cveId": cve_id})
        items = data.get("vulnerabilities") or []
        cves = [i.get("cve") or i for i in items]
        if cves:
            self._cache_put(cves)
            return cves[0]
        return None

    def sync_recent(self, days: int = 7, start_index: int = 0, max_pages: int = 3) -> int:
        total = 0
        pubStartDate = time.strftime("%Y-%m-%dT00:00:00.000", time.gmtime(time.time()-days*86400))
        for page in range(max_pages):
            params = {"pubStartDate": pubStartDate, "startIndex": start_index + page*200}
            data = self._api_get(params)
            items = data.get("vulnerabilities") or []
            cves = [i.get("cve") or i for i in items]
            if not cves:
                break
            self._cache_put(cves)
            total += len(cves)
        return total
