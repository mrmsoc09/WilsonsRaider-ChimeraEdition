from __future__ import annotations
from typing import List, Dict, Any
import yaml, os

DEFAULT_PATH = os.getenv("WR_CHAIN_PATTERNS", "configs/chain_patterns.yaml")

def load_patterns(path: str = DEFAULT_PATH) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("patterns", [])
