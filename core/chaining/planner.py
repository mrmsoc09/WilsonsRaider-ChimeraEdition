from __future__ import annotations
from typing import List, Dict, Any, Optional
import math

class ChainPlanner:
    def __init__(self):
        pass

    def suggest_next(self, artifacts: List[Dict[str, Any]], goals: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        # Stub heuristic: prioritize steps by expected value = likelihood * impact / cost
        steps = []
        for a in artifacts:
            # example heuristic
            ev = a.get('likelihood', 0.3) * a.get('impact', 0.7) / (a.get('cost', 1.0) or 1.0)
            steps.append({"action": a.get('proposed_action', 'enumerate'), "expected_value": ev})
        steps.sort(key=lambda x: x['expected_value'], reverse=True)
        return steps[:5]
