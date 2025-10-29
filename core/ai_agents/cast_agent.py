<<<<<<< HEAD
from crewai import Agent
from core.managers.ai_manager import AIManager

class CASTAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Container Security Testing Agent',
            goal='Analyze container images for known vulnerabilities.',
            backstory='You are a specialized CAST agent, using tools like Trivy and Clair to find security flaws in container images.',
            verbose=True
        )
        self.ai_manager = AIManager()

    def analyze_results(self, tool_output):
        prompt = f"As a CAST analysis expert, summarize the key findings from this container scan report:\n\n{tool_output}"
        return self.ai_manager._call_llm(prompt, system_prompt="You are a security analysis expert.", task_type='analysis')

    def run_scan(self, target_image):
        from core.tools.trivy_wrapper import run_trivy
        from core import ui

        ui.print_info(f"CASTAgent starting Trivy scan on {target_image}...")
        results = run_trivy(target_image)

        if not results or ('error' in results[0]):
            error_message = results[0]['error'] if results and ('error' in results[0]) else "Unknown error"
            ui.print_error(f"CASTAgent Trivy scan failed: {error_message}")
            return {"status": "failed", "error": error_message}

        ui.print_success(f"CASTAgent Trivy scan completed. Analyzing results...")
        return self.analyze_results(results)

=======
"""Container Application Security Testing (CAST) Agent

Specialized agent for container and cloud-native security:
- Docker/Kubernetes security analysis
- Container image vulnerability scanning
- Runtime security monitoring
- Secrets detection in images and manifests
- Integration with: trivy, grype, docker scout, kube-bench, falco

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


class CASTAgent:
    """Container Application Security Testing agent.

    Performs security analysis of containerized applications including
    image scanning, runtime security, orchestration config auditing.

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

    SCAN_TYPES = ['image', 'runtime', 'config', 'secrets', 'compliance']

    CONTAINER_PLATFORMS = ['docker', 'podman', 'containerd', 'kubernetes', 'openshift']

    VULN_SEVERITIES = ['critical', 'high', 'medium', 'low', 'negligible']

    CIS_BENCHMARKS = ['docker', 'kubernetes', 'eks', 'aks', 'gke']

    def __init__(self, cost_tier: str = 'balanced'):
        """Initialize CAST Agent.

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
        logger.info(f"CASTAgent initialized: model={self.model}")

    def _select_model(self) -> str:
        """Select LLM model based on cost tier."""
        return self.COST_TIERS[self.cost_tier]

    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CAST workflow.

        Args:
            data: Task specification containing:
                - target: Container image, registry, or cluster endpoint
                - scan_types: List of scan types to perform
                - platform: Container platform (docker/k8s/etc)
                - severity_threshold: Minimum severity to report
                - cis_benchmark: CIS benchmark to validate against

        Returns:
            Dict containing:
                - vulnerabilities: CVEs found in images
                - misconfigurations: Security config issues
                - secrets_exposed: Detected hardcoded secrets
                - runtime_threats: Runtime security events
                - compliance_violations: CIS benchmark failures
                - recommendations: Remediation guidance
                - status: Task completion status

        Raises:
            ValueError: If required parameters missing
            RuntimeError: If scanning fails
        """
        if 'target' not in data:
            raise ValueError("Missing required parameter: target")

        target = data['target']
        scan_types = data.get('scan_types', self.SCAN_TYPES)
        platform = data.get('platform', 'docker')
        severity_threshold = data.get('severity_threshold', 'medium')
        cis_benchmark = data.get('cis_benchmark')

        logger.info(f"Executing CAST on {target} (platform={platform}, scans={scan_types})")

        # TODO: Implement CAST logic
        # Image Scanning:
        # - Trivy/Grype for CVE detection in OS packages and app dependencies
        # - Docker Scout for supply chain security
        # - Layer-by-layer analysis for bloat and secrets

        # Runtime Security:
        # - Falco for runtime threat detection
        # - Syscall monitoring for anomalous behavior
        # - Network policy validation

        # Configuration Analysis:
        # - Dockerfile best practices (USER directive, minimal base images)
        # - Kubernetes manifest security (securityContext, RBAC)
        # - Pod Security Standards compliance
        # - kube-bench for CIS Kubernetes Benchmark

        # Secrets Detection:
        # - Regex patterns for API keys, passwords, tokens
        # - Environment variable analysis
        # - ConfigMap/Secret resource auditing

        return {
            'status': 'not_implemented',
            'message': 'Full CAST logic pending implementation',
            'target': target,
            'platform': platform,
            'scan_types': scan_types,
            'severity_threshold': severity_threshold,
            'vulnerabilities': [],
            'misconfigurations': [],
            'secrets_exposed': [],
            'runtime_threats': [],
            'compliance_violations': [],
            'recommendations': []
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
