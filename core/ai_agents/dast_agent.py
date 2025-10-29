<<<<<<< HEAD
from crewai import Agent
from core.managers.ai_manager import AIManager

class DASTAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Dynamic Application Security Testing Agent',
            goal='Analyze web applications for vulnerabilities at runtime.',
            backstory='You are a specialized DAST agent, using tools like ZAP and Arachni to find security flaws in live applications.',
            verbose=True
        )
        self.ai_manager = AIManager()

    def analyze_results(self, tool_output):
        """
        Uses the AI manager to analyze DAST tool output.
        """
        prompt = f"You are a DAST analysis expert. Summarize the following tool output and identify the most critical findings:\n\n{tool_output}"
        summary = self.ai_manager._call_llm(prompt, system_prompt="You are a security analysis expert.", task_type='analysis')
        return summary

    def run_scan(self, target):
        from core.tools.zap_wrapper import run_zap
        from core import ui

        ui.print_info(f"DASTAgent starting ZAP scan on {target}...")
        results = run_zap(target)

        if not results or ('error' in results[0]):
            error_message = results[0]['error'] if results and ('error' in results[0]) else "Unknown error"
            ui.print_error(f"DASTAgent ZAP scan failed: {error_message}")
            return {"status": "failed", "error": error_message}

        ui.print_success(f"DASTAgent ZAP scan completed. Analyzing results...")
        return self.analyze_results(results)

=======
"""Dynamic Application Security Testing (DAST) Agent

Specialized agent for dynamic web application security testing:
- Black-box web vulnerability scanning
- Authentication and session management testing
- Input validation and injection testing
- Business logic vulnerability discovery
- Integration with: OWASP ZAP, Burp Suite, Nuclei, ffuf, sqlmap

Version: 2.0.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from secret_manager import SecretManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class DASTAgent:
    """Dynamic Application Security Testing agent.

    Performs black-box security testing of running web applications
    including automated scanning, manual testing, and exploit validation.

    Attributes:
        cost_tier: LLM model selection strategy
        secrets: Vault integration for credentials
        model: Selected LLM model
        llm_api_key: OpenAI API key from Vault
    """

    COST_TIERS = {
        'economic': 'gpt-3.5-turbo',
        'balanced': 'gpt-4',
        'high-performance': 'gpt-4o'
    }

    SCAN_PROFILES = ['quick', 'standard', 'thorough', 'custom']

    OWASP_TOP_10 = [
        'broken_access_control', 'cryptographic_failures',
        'injection', 'insecure_design', 'security_misconfiguration',
        'vulnerable_components', 'auth_failures', 'data_integrity_failures',
        'logging_monitoring_failures', 'ssrf'
    ]

    TEST_CATEGORIES = [
        'xss', 'sqli', 'csrf', 'idor', 'path_traversal',
        'xxe', 'rce', 'ssrf', 'open_redirect', 'sensitive_data_exposure'
    ]

    def __init__(self, cost_tier: str = 'balanced'):
        """Initialize DAST Agent.

        Args:
            cost_tier: Model selection strategy

        Raises:
            ValueError: If cost_tier invalid
            RuntimeError: If Vault initialization fails
        """
        if cost_tier not in self.COST_TIERS:
            raise ValueError(f"Invalid cost_tier: {cost_tier}")

        self.cost_tier = cost_tier
        self.secrets = SecretManager()
        self.llm_api_key = self.secrets.get_secret('wilsons-raiders/creds', 'OPENAI_API_KEY')

        if not self.llm_api_key:
            raise RuntimeError("Failed to retrieve OPENAI_API_KEY")

        self.model = self._select_model()
        logger.info(f"DASTAgent initialized: model={self.model}")

    def _select_model(self) -> str:
        """Select LLM model based on cost tier."""
        return self.COST_TIERS[self.cost_tier]

    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DAST workflow.

        Args:
            data: Task specification containing:
                - target_url: Web application endpoint
                - scan_profile: Scan depth/thoroughness
                - authenticated: Whether to test authenticated endpoints
                - credentials: Login credentials if authenticated
                - scope: URL patterns to include/exclude
                - test_categories: Specific vulnerability types to test

        Returns:
            Dict containing:
                - vulnerabilities: Detected security issues
                - exploits: Validated exploits with PoCs
                - attack_surface: Discovered endpoints and parameters
                - risk_score: Overall application risk assessment
                - recommendations: Prioritized remediation guidance
                - status: Task completion status

        Raises:
            ValueError: If required parameters missing
            RuntimeError: If scanning fails
        """
        if 'target_url' not in data:
            raise ValueError("Missing required parameter: target_url")

        target_url = data['target_url']
        scan_profile = data.get('scan_profile', 'standard')
        authenticated = data.get('authenticated', False)
        credentials = data.get('credentials', {})
        scope = data.get('scope', {})
        test_categories = data.get('test_categories', self.TEST_CATEGORIES)

        logger.info(f"Executing DAST on {target_url} (profile={scan_profile}, auth={authenticated})")

        # TODO: Implement DAST logic
        # Crawling & Discovery:
        # - Spider web application to map attack surface
        # - Extract forms, parameters, endpoints, APIs
        # - Identify technology stack (Wappalyzer-style)

        # Authentication Testing:
        # - Weak password policies
        # - Session management flaws
        # - Password reset vulnerabilities
        # - OAuth/SAML misconfigurations

        # Injection Testing:
        # - SQL injection (error-based, blind, time-based)
        # - XSS (reflected, stored, DOM-based)
        # - Command injection
        # - Template injection (SSTI)
        # - XXE and XML bombs

        # Access Control Testing:
        # - IDOR (horizontal/vertical privilege escalation)
        # - Path traversal and LFI
        # - Missing function-level access control
        # - CSRF token validation

        # Business Logic Testing:
        # - Race conditions
        # - Parameter tampering
        # - Price manipulation
        # - Workflow bypass

        return {
            'status': 'not_implemented',
            'message': 'Full DAST logic pending implementation',
            'target_url': target_url,
            'scan_profile': scan_profile,
            'authenticated': authenticated,
            'test_categories': test_categories,
            'vulnerabilities': [],
            'exploits': [],
            'attack_surface': {},
            'risk_score': 0,
            'recommendations': []
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
