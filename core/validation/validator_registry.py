"""Validation tactics registry.
- Supports independent tactics: metasploit_check, nuclei_template, custom_script
- Redundancy is optional, controlled by policy (default off per user approval)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ValidationResult:
    tactic: str
    success: bool
    confidence: float
    evidence: Dict[str, Any]

class ValidatorRegistry:
    def __init__(self, guardian):
        self.guardian = guardian

    def run(self, finding: Dict[str, Any], tactics: List[str]) -> Dict[str, Any]:
        results: List[ValidationResult] = []
        for t in tactics:
            if t == "metasploit_check":
                results.append(self._metasploit_check(finding))
            elif t == "nuclei_template":
                results.append(self._nuclei_template(finding))
            elif t == "custom_script":
                results.append(self._custom_script(finding))
        agg = self._aggregate(results)
        return {"results": [r.__dict__ for r in results], "aggregate": agg}

    def _metasploit_check(self, finding: Dict[str, Any]) -> ValidationResult:
        # Stub: integrate msfconsole -q -x 'use ...; set RHOST ...; check; exit'
        return ValidationResult("metasploit_check", success=False, confidence=0.0, evidence={"note": "stub"})

    def _nuclei_template(self, finding: Dict[str, Any]) -> ValidationResult:
        # Stub: run nuclei -t custom.yaml -u target
        return ValidationResult("nuclei_template", success=False, confidence=0.0, evidence={"note": "stub"})

    def _custom_script(self, finding: Dict[str, Any]) -> ValidationResult:
        # Stub: sandboxed script execution
        return ValidationResult("custom_script", success=False, confidence=0.0, evidence={"note": "stub"})

    def _aggregate(self, results: List[ValidationResult]) -> Dict[str, Any]:
        # Redundancy optional; by default accept the highest-confidence single success
        any_success = any(r.success for r in results)
        max_conf = max((r.confidence for r in results), default=0.0)
        return {"validated": any_success and max_conf >= 0.6, "max_confidence": max_conf}
