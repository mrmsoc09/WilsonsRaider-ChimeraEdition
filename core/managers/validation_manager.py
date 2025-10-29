"""Validation Manager - Finding Validation and False Positive Filtering

Validates findings with confidence scoring and evidence collection.
Version: 2.0.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    CONFIRMED = 5      # 100% validated with PoC
    HIGH = 4           # Multiple indicators, high likelihood
    MEDIUM = 3         # Some indicators, manual review recommended
    LOW = 2            # Weak indicators, likely false positive
    UNVALIDATED = 1    # Not yet validated

class ValidationStatus(Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    FALSE_POSITIVE = "false_positive"
    REQUIRES_MANUAL = "requires_manual_review"

class ValidationManager:
    """Manages finding validation and false positive filtering."""

    def __init__(self, state_manager=None, ui_manager=None, config: dict = None):
        self.state_manager = state_manager
        self.ui = ui_manager
        self.config = config or {}
        self.validation_rules = self._load_validation_rules()
        logger.info("ValidationManager initialized")

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different vulnerability types."""
        return {
            'xss': {
                'indicators': ['alert(', 'prompt(', 'confirm(', '<script', 'onerror='],
                'false_positive_patterns': ['Content-Security-Policy', 'X-XSS-Protection'],
                'min_confidence': ConfidenceLevel.MEDIUM
            },
            'sqli': {
                'indicators': ['sleep(', 'UNION SELECT', "' OR '1'='1", 'BENCHMARK('],
                'false_positive_patterns': ['mysql_real_escape_string', 'prepared statement'],
                'min_confidence': ConfidenceLevel.HIGH
            },
            'rce': {
                'indicators': ['whoami', 'id', 'cmd.exe', '/bin/bash'],
                'false_positive_patterns': [],
                'min_confidence': ConfidenceLevel.CONFIRMED
            }
        }

    def validate_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single finding with confidence scoring."""
        logger.info(f"Validating finding: {finding.get('name')}")

        validation_result = {
            'finding_id': finding.get('id'),
            'status': ValidationStatus.PENDING.value,
            'confidence': ConfidenceLevel.UNVALIDATED,
            'confidence_score': 0.0,
            'evidence': [],
            'false_positive_indicators': [],
            'validation_notes': [],
            'validated_at': datetime.utcnow().isoformat()
        }

        # Extract finding details
        vuln_name = finding.get('name', '').lower()
        vuln_type = self._identify_vulnerability_type(vuln_name)

        # Calculate confidence score
        confidence_score = self._calculate_confidence(finding, vuln_type)
        validation_result['confidence_score'] = confidence_score
        validation_result['confidence'] = self._score_to_level(confidence_score)

        # Check for false positive indicators
        fp_indicators = self._check_false_positive_indicators(finding, vuln_type)
        validation_result['false_positive_indicators'] = fp_indicators

        # Collect evidence
        evidence = self._collect_evidence(finding)
        validation_result['evidence'] = evidence

        # Determine final status
        if fp_indicators:
            validation_result['status'] = ValidationStatus.FALSE_POSITIVE.value
            validation_result['validation_notes'].append('False positive indicators detected')
        elif confidence_score >= 0.8:
            validation_result['status'] = ValidationStatus.VALIDATED.value
            validation_result['validation_notes'].append('High confidence validation')
        elif confidence_score >= 0.5:
            validation_result['status'] = ValidationStatus.REQUIRES_MANUAL.value
            validation_result['validation_notes'].append('Medium confidence - manual review recommended')
        else:
            validation_result['status'] = ValidationStatus.FALSE_POSITIVE.value
            validation_result['validation_notes'].append('Low confidence - likely false positive')

        logger.info(f"Validation complete: {validation_result['status']} (confidence: {confidence_score:.2f})")

        if self.ui:
            status_color = 'green' if validation_result['status'] == ValidationStatus.VALIDATED.value else 'yellow'
            self.ui.print(f"[{status_color}]Validated: {finding.get('name')} - {validation_result['status']}[/{status_color}]")

        return validation_result

    def _identify_vulnerability_type(self, vuln_name: str) -> Optional[str]:
        """Identify vulnerability type from name."""
        if 'xss' in vuln_name or 'cross-site scripting' in vuln_name:
            return 'xss'
        elif 'sqli' in vuln_name or 'sql injection' in vuln_name:
            return 'sqli'
        elif 'rce' in vuln_name or 'command injection' in vuln_name:
            return 'rce'
        return None

    def _calculate_confidence(self, finding: Dict[str, Any], vuln_type: Optional[str]) -> float:
        """Calculate confidence score for finding."""
        score = 0.0

        # Base score from severity
        severity_scores = {
            'critical': 0.4,
            'high': 0.3,
            'medium': 0.2,
            'low': 0.1
        }
        severity = finding.get('severity', 'low').lower()
        score += severity_scores.get(severity, 0.1)

        # Check for vulnerability-specific indicators
        if vuln_type and vuln_type in self.validation_rules:
            rules = self.validation_rules[vuln_type]
            raw_output = finding.get('raw_output', '')

            indicator_matches = sum(1 for ind in rules['indicators'] if ind in raw_output)
            if indicator_matches > 0:
                score += min(0.4, indicator_matches * 0.2)

        # Check for evidence artifacts
        if finding.get('matched_at'):
            score += 0.1
        if finding.get('template_id'):
            score += 0.1

        return min(1.0, score)

    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """Convert confidence score to level."""
        if score >= 0.9:
            return ConfidenceLevel.CONFIRMED
        elif score >= 0.7:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.3:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.UNVALIDATED

    def _check_false_positive_indicators(self, finding: Dict[str, Any], 
                                        vuln_type: Optional[str]) -> List[str]:
        """Check for false positive indicators."""
        indicators = []

        if not vuln_type or vuln_type not in self.validation_rules:
            return indicators

        rules = self.validation_rules[vuln_type]
        raw_output = finding.get('raw_output', '')

        for pattern in rules['false_positive_patterns']:
            if pattern in raw_output:
                indicators.append(f"Protection detected: {pattern}")

        return indicators

    def _collect_evidence(self, finding: Dict[str, Any]) -> List[Dict[str, str]]:
        """Collect evidence artifacts for finding."""
        evidence = []

        if finding.get('matched_at'):
            evidence.append({
                'type': 'url',
                'value': finding['matched_at'],
                'description': 'Vulnerable endpoint'
            })

        if finding.get('template_id'):
            evidence.append({
                'type': 'template',
                'value': finding['template_id'],
                'description': 'Detection template used'
            })

        if finding.get('raw_output'):
            evidence.append({
                'type': 'raw_output',
                'value': finding['raw_output'][:500],  # Truncate for storage
                'description': 'Raw scanner output'
            })

        return evidence

    def batch_validate(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate multiple findings in batch."""
        logger.info(f"Batch validating {len(findings)} findings")

        results = {
            'total': len(findings),
            'validated': 0,
            'false_positives': 0,
            'requires_manual': 0,
            'details': []
        }

        for finding in findings:
            validation = self.validate_finding(finding)
            results['details'].append(validation)

            if validation['status'] == ValidationStatus.VALIDATED.value:
                results['validated'] += 1
            elif validation['status'] == ValidationStatus.FALSE_POSITIVE.value:
                results['false_positives'] += 1
            elif validation['status'] == ValidationStatus.REQUIRES_MANUAL.value:
                results['requires_manual'] += 1

        logger.info(f"Batch validation complete: {results['validated']} validated, "
                   f"{results['false_positives']} false positives")

        return results
