"""NVD (National Vulnerability Database) Client - Production-Grade Integration

Comprehensive NVD API client with CVE search, CVSS parsing,
local caching, and change feed monitoring.
Version: 2.0.0
"""

import os
import time
import sqlite3
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

class NVDNotConfigured(Exception):
    """Raised when NVD client is not properly configured."""
    pass

class NVDClient:
    """Production-grade NVD API client with local caching."""

    NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    RATE_LIMIT_NO_KEY = 5
    RATE_LIMIT_WITH_KEY = 50

    def __init__(self, api_key: Optional[str] = None, cache_db: Optional[str] = None, vault_client=None):
        if httpx is None:
            raise NVDNotConfigured("httpx not installed. Install with: pip install httpx")

        self.api_key = self._load_api_key(api_key, vault_client)
        self.cache_db = Path(cache_db or os.getenv("WR_CACHE_DB", "data/nvd_cache.db"))
        self.rate_limit = self.RATE_LIMIT_WITH_KEY if self.api_key else self.RATE_LIMIT_NO_KEY
        self.request_timestamps: List[float] = []

        self.client = httpx.Client(timeout=30.0, headers=self._get_headers())
        self._init_db()

        logger.info(f"NVDClient initialized: cache={self.cache_db}, rate_limit={self.rate_limit}/30s")

    def _load_api_key(self, api_key: Optional[str], vault_client) -> Optional[str]:
        if api_key:
            return api_key
        if vault_client:
            try:
                key = vault_client.get_secret("integrations/nvd", "api_key")
                if key:
                    logger.info("NVD API key loaded from Vault")
                    return key
            except Exception as e:
                logger.warning(f"Failed to load NVD key from Vault: {e}")

        env_key = os.getenv("NVD_API_KEY")
        if env_key:
            logger.info("NVD API key loaded from environment")
            return env_key

        logger.warning("No NVD API key configured - using lower rate limit")
        return None

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "WilsonsRaider-Security-Research/2.0"}
        if self.api_key:
            headers["apiKey"] = self.api_key
        return headers

    def _init_db(self) -> None:
        self.cache_db.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS cves (
                cve_id TEXT PRIMARY KEY, data JSON NOT NULL, cvss_v3_score REAL,
                cvss_v3_severity TEXT, published_date TEXT, last_modified TEXT, cached_at INTEGER NOT NULL)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at INTEGER NOT NULL)""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cvss_score ON cves(cvss_v3_score)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON cves(cvss_v3_severity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_published ON cves(published_date)")
            conn.commit()
        logger.debug("NVD cache database initialized")

    def _rate_limit_wait(self) -> None:
        now = time.time()
        window_start = now - 30
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > window_start]

        if len(self.request_timestamps) >= self.rate_limit:
            sleep_time = self.request_timestamps[0] + 30 - now + 0.5
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)

        self.request_timestamps.append(time.time())

    def _api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self._rate_limit_wait()
        try:
            response = self.client.get(self.NVD_API_BASE, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"NVD API request failed: {e}")
            raise

    def get_cve(self, cve_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        if use_cache:
            cached = self._get_cached_cve(cve_id)
            if cached:
                logger.debug(f"Cache hit: {cve_id}")
                return cached

        try:
            data = self._api_request({"cveId": cve_id})
            vulnerabilities = data.get("vulnerabilities", [])
            if not vulnerabilities:
                logger.warning(f"CVE not found: {cve_id}")
                return None

            cve = vulnerabilities[0].get("cve", {})
            self._cache_cve(cve)
            logger.info(f"Retrieved CVE: {cve_id}")
            return cve
        except Exception as e:
            logger.error(f"Failed to get CVE {cve_id}: {e}")
            return None

    def search_cves(self, keyword: Optional[str] = None, cvss_v3_severity: Optional[str] = None,
                    published_start: Optional[datetime] = None, published_end: Optional[datetime] = None,
                    results_per_page: int = 100, start_index: int = 0) -> List[Dict[str, Any]]:
        params = {"resultsPerPage": results_per_page, "startIndex": start_index}
        if keyword:
            params["keywordSearch"] = keyword
        if cvss_v3_severity:
            params["cvssV3Severity"] = cvss_v3_severity.upper()
        if published_start:
            params["pubStartDate"] = published_start.strftime("%Y-%m-%dT%H:%M:%S.000")
        if published_end:
            params["pubEndDate"] = published_end.strftime("%Y-%m-%dT%H:%M:%S.000")

        try:
            data = self._api_request(params)
            vulnerabilities = data.get("vulnerabilities", [])
            cves = [v.get("cve", {}) for v in vulnerabilities]
            for cve in cves:
                self._cache_cve(cve)
            logger.info(f"Search returned {len(cves)} CVEs")
            return cves
        except Exception as e:
            logger.error(f"CVE search failed: {e}")
            return []

    def bulk_sync(self, days: int = 7, max_results: int = 2000) -> int:
        start_date = datetime.utcnow() - timedelta(days=days)
        total_synced = 0
        start_index = 0
        results_per_page = 100

        logger.info(f"Starting bulk sync: last {days} days")
        while total_synced < max_results:
            cves = self.search_cves(published_start=start_date, results_per_page=results_per_page, start_index=start_index)
            if not cves:
                break
            total_synced += len(cves)
            start_index += results_per_page
            logger.info(f"Bulk sync progress: {total_synced} CVEs")
            if len(cves) < results_per_page:
                break

        self._set_metadata("last_bulk_sync", datetime.utcnow().isoformat())
        logger.info(f"Bulk sync complete: {total_synced} CVEs")
        return total_synced

    def parse_cvss(self, cve: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        metrics = cve.get("metrics", {})
        cvss_v3_list = metrics.get("cvssMetricV31", []) or metrics.get("cvssMetricV30", [])
        if cvss_v3_list:
            cvss_v3 = cvss_v3_list[0].get("cvssData", {})
            return {"version": "3.x", "score": cvss_v3.get("baseScore"),
                    "severity": cvss_v3.get("baseSeverity"), "vector": cvss_v3.get("vectorString"),
                    "exploitability": cvss_v3_list[0].get("exploitabilityScore"),
                    "impact": cvss_v3_list[0].get("impactScore")}

        cvss_v2_list = metrics.get("cvssMetricV2", [])
        if cvss_v2_list:
            cvss_v2 = cvss_v2_list[0].get("cvssData", {})
            score = cvss_v2.get("baseScore")
            severity = "HIGH" if score and score >= 7.0 else "MEDIUM" if score and score >= 4.0 else "LOW"
            return {"version": "2.0", "score": score, "severity": severity, "vector": cvss_v2.get("vectorString")}
        return None

    def _get_cached_cve(self, cve_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.cache_db) as conn:
            row = conn.execute("SELECT data FROM cves WHERE cve_id = ?", (cve_id,)).fetchone()
            if row:
                return json.loads(row[0])
        return None

    def _cache_cve(self, cve: Dict[str, Any]) -> None:
        cve_id = cve.get("id")
        if not cve_id:
            return
        cvss = self.parse_cvss(cve)
        published = cve.get("published", "")
        modified = cve.get("lastModified", "")

        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("""REPLACE INTO cves (cve_id, data, cvss_v3_score, cvss_v3_severity,
                published_date, last_modified, cached_at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (cve_id, json.dumps(cve), cvss.get("score") if cvss else None,
                 cvss.get("severity") if cvss else None, published, modified, int(time.time())))
            conn.commit()

    def _set_metadata(self, key: str, value: str) -> None:
        with sqlite3.connect(self.cache_db) as conn:
            conn.execute("REPLACE INTO metadata (key, value, updated_at) VALUES (?, ?, ?)",
                        (key, value, int(time.time())))
            conn.commit()

    def close(self) -> None:
        self.client.close()
        logger.info("NVDClient closed")
