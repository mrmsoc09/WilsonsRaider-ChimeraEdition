from __future__ import annotations
from typing import List, Dict, Any, Tuple
import hashlib
import time

class CorrelationEngine:
    """Normalizes, deduplicates, and correlates OSINT/enum artifacts into assets and signals."""
    def __init__(self):
        pass

    def normalize(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for it in items:
            t = it.get("type")
            v = it.get("value")
            src = it.get("source", "unknown")
            ts = it.get("timestamp") or int(time.time())
            out.append({"type": t, "value": v, "source": src, "timestamp": ts, "raw": it})
        return out

    def fingerprint(self, item: Dict[str, Any]) -> str:
        key = f"{item.get('type')}::{item.get('value')}"
        return hashlib.sha256(key.encode()).hexdigest()

    def deduplicate(self, items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        seen = {}
        dropped = 0
        for it in items:
            fp = self.fingerprint(it)
            if fp in seen:
                # Keep earliest timestamp and aggregate provenance
                prev = seen[fp]
                prev_sources = set(prev.get("provenance", [])) | {prev.get("source"), it.get("source")}
                prev["provenance"] = list({s for s in prev_sources if s})
                prev["timestamp"] = min(prev.get("timestamp", int(time.time())), it.get("timestamp", int(time.time())))
                dropped += 1
            else:
                it["provenance"] = [it.get("source")] if it.get("source") else []
                seen[fp] = it
        return list(seen.values()), dropped

    def score(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Heuristic: higher confidence for multiple sources and sensitive types
        SENSITIVE = {"apikey", "credential", "s3_bucket", "admin_portal", "cloud_asset"}
        for it in items:
            srcs = len([s for s in it.get("provenance", []) if s])
            base = 0.4 + min(srcs, 3) * 0.15
            if it.get("type") in SENSITIVE:
                base += 0.2
            it["confidence"] = min(base, 0.99)
        return items

    def correlate(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Returns categorized assets and signals useful for chaining planner."""
        assets: Dict[str, List[Dict[str, Any]]] = {
            "domains": [], "subdomains": [], "ips": [], "endpoints": [], "secrets": [], "cloud": [], "misc": []
        }
        for it in items:
            t = (it.get("type") or "misc").lower()
            if t in ("domain",):
                assets["domains"].append(it)
            elif t in ("subdomain",):
                assets["subdomains"].append(it)
            elif t in ("ip", "host"): 
                assets["ips"].append(it)
            elif t in ("url", "endpoint"): 
                assets["endpoints"].append(it)
            elif t in ("apikey", "credential", "token"): 
                assets["secrets"].append(it)
            elif t in ("s3_bucket", "gcs_bucket", "azure_blob", "cloud_asset"): 
                assets["cloud"].append(it)
            else:
                assets["misc"].append(it)
        return {"assets": assets}

    def process(self, raw_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        norm = self.normalize(raw_items)
        dedup, _ = self.deduplicate(norm)
        scored = self.score(dedup)
        return self.correlate(scored)
