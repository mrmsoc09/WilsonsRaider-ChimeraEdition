<<<<<<< HEAD
from crewai import Agent
from core.managers.ai_manager import AIManager
from typing import Dict, Any

class ReportGenerationAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Security Report Writer',
            goal='Generate high-quality, professional vulnerability reports in Markdown format.',
            backstory='You are a skilled technical writer specializing in cybersecurity. You can take raw vulnerability data and transform it into a clear, comprehensive, and professional report suitable for submission.',
            verbose=True
        )
        self.ai_manager = AIManager()

    def generate_report(self, finding_data: Dict[str, Any]) -> str:
        prompt = f"Based on the following structured vulnerability data, write a high-quality vulnerability report in Markdown format. Include sections for Title, Severity, Target, Description, Impact, Steps to Reproduce, and Remediation.\n\nData:\n{finding_data}"
        return self.ai_manager._call_llm(prompt, system_prompt="You are an expert security report writer.", task_type='report_writing')

=======
"""Report Generation Agent - Automated Security Documentation

Specialized agent for comprehensive security report generation:
- Vulnerability report creation with detailed findings
- Executive summaries for stakeholders
- Technical deep-dive documentation
- Compliance report generation (OWASP, PCI-DSS, etc.)
- Integration with: Markdown, PDF, HTML, Jira, Slack

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


class ReportGenerationAgent:
    """Autonomous security report generation agent.
    
    Creates comprehensive security reports from scan results,
    vulnerability findings, and threat intelligence data.
    
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
    
    REPORT_TYPES = [
        'vulnerability', 'penetration_test', 'compliance',
        'executive_summary', 'technical_deep_dive', 'remediation'
    ]
    
    OUTPUT_FORMATS = ['markdown', 'html', 'pdf', 'json', 'jira']
    
    SEVERITY_LEVELS = ['critical', 'high', 'medium', 'low', 'info']
    
    def __init__(self, cost_tier: str = 'balanced'):
        """Initialize Report Generation Agent.
        
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
        logger.info(f"ReportGenerationAgent initialized: model={self.model}")
    
    def _select_model(self) -> str:
        """Select LLM model based on cost tier."""
        return self.COST_TIERS[self.cost_tier]
    
    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation workflow.
        
        Args:
            data: Task specification containing:
                - findings: List of vulnerability findings
                - report_type: Type of report to generate
                - format: Output format (markdown|html|pdf|json)
                - target: Target organization/system name
                - scope: Tested scope details
                - metadata: Additional context (dates, testers, etc.)
        
        Returns:
            Dict containing:
                - report_path: Path to generated report
                - executive_summary: High-level findings summary
                - statistics: Vulnerability counts by severity
                - recommendations: Prioritized remediation steps
                - status: Task completion status
        
        Raises:
            ValueError: If required parameters missing
            RuntimeError: If report generation fails
        """
        if 'findings' not in data:
            raise ValueError("Missing required parameter: findings")
        
        findings = data['findings']
        report_type = data.get('report_type', 'vulnerability')
        output_format = data.get('format', 'markdown')
        target = data.get('target', 'Unknown Target')
        scope = data.get('scope', [])
        metadata = data.get('metadata', {})
        
        if report_type not in self.REPORT_TYPES:
            raise ValueError(f"Invalid report_type: {report_type}")
        
        if output_format not in self.OUTPUT_FORMATS:
            raise ValueError(f"Invalid output format: {output_format}")
        
        logger.info(f"Generating {report_type} report for {target} (format={output_format})")
        
        # TODO: Implement report generation logic
        # - Parse and categorize findings by severity
        # - Generate executive summary
        # - Create technical vulnerability details
        # - Add remediation recommendations
        # - Generate charts/graphs for statistics
        # - Format output (Markdown, HTML, PDF)
        # - Optional: Push to Jira/Slack
        
        return {
            'status': 'not_implemented',
            'message': 'Full report generation logic pending',
            'report_type': report_type,
            'target': target,
            'format': output_format,
            'findings_count': len(findings) if isinstance(findings, list) else 0,
            'report_path': None,
            'executive_summary': None,
            'statistics': {},
            'recommendations': []
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
