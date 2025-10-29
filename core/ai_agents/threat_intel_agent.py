<<<<<<< HEAD
from crewai import Agent
from core.managers.ai_manager import AIManager
from core.tools.nvd_client import NVDClient
from core.tools.searchsploit_wrapper import search_exploitdb
import re

class ThreatIntelAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Threat Intelligence Analyst',
            goal='Enrich vulnerability findings with external context from NVD and Exploit-DB.',
            backstory='You are a threat intelligence expert. You provide crucial context on vulnerabilities by cross-referencing findings with the National Vulnerability Database for severity scores and Exploit-DB for public exploits.',
            verbose=True
        )
        self.ai_manager = AIManager()
        self.nvd_client = NVDClient()

    def enrich_finding(self, finding_data: dict) -> dict:
        """
        Enriches a vulnerability finding with data from NVD and Exploit-DB.

        Args:
            finding_data (dict): A dictionary representing the vulnerability. 
                                 Should contain keys like 'name', 'description', etc.

        Returns:
            dict: The original finding data enriched with 'nvd_details' and 'exploitdb_results'.
        """
        enriched_data = finding_data.copy()
        cve_id = self._extract_cve(str(finding_data))

        # 1. Enrich with NVD data if a CVE is found
        if cve_id:
            nvd_details = self.nvd_client.get_cve_details(cve_id)
            if nvd_details:
                enriched_data['nvd_details'] = {
                    'id': nvd_details.get('id'),
                    'summary': nvd_details.get('descriptions', [{}])[0].get('value'),
                    'cvss_v3': self._get_cvss_v3_score(nvd_details)
                }
        
        # 2. Enrich with Exploit-DB data
        search_query = cve_id if cve_id else finding_data.get('name', '')
        if search_query:
            exploitdb_results = search_exploitdb(search_query)
            if exploitdb_results and exploitdb_results['status'] == 'success':
                enriched_data['exploitdb_results'] = exploitdb_results['results']

        # 3. Use LLM to summarize the enriched data
        summary_prompt = f"""
        A vulnerability finding has been enriched with data from NVD and Exploit-DB.
        Summarize the key intelligence points. Is there a public exploit? What is the severity?

        Enriched Data:
        {enriched_data}
        """
        summary = self.ai_manager._call_llm(summary_prompt, system_prompt="You are a threat intelligence summarizer.", task_type='analysis')
        enriched_data['ai_summary'] = summary

        return enriched_data

    def _extract_cve(self, text: str) -> str | None:
        """Extracts the first CVE identifier from a string."""
        cve_match = re.search(r'(CVE-\d{4}-\d{4,7})', text, re.IGNORECASE)
        return cve_match.group(0) if cve_match else None

    def _get_cvss_v3_score(self, nvd_details: dict) -> float | None:
        """Extracts the CVSS V3 base score from the NVD data structure."""
        metrics = nvd_details.get('metrics', {}).get('cvssMetricV31', [])
        if metrics:
            return metrics[0].get('cvssData', {}).get('baseScore')
        return None

=======
"""Threat Intelligence Agent - Security Intelligence Gathering

Specialized agent for threat intelligence collection and analysis:
- CVE database monitoring and correlation
- Exploit database tracking (ExploitDB, Metasploit)
- Dark web intelligence gathering
- Threat actor profiling and attribution
- Integration with: MITRE ATT&CK, CVE, NVD, Shodan, VirusTotal

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


class ThreatIntelAgent:
    """Autonomous threat intelligence collection and analysis agent.
    
    Monitors CVE databases, exploit repositories, dark web sources,
    and correlates threat intelligence with target vulnerabilities.
    
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
    
    INTEL_SOURCES = [
        'cve', 'nvd', 'exploitdb', 'metasploit', 'github',
        'shodan', 'virustotal', 'mitre_attack', 'dark_web'
    ]
    
    THREAT_TYPES = [
        'zero_day', 'known_exploit', 'emerging_threat',
        'apt_activity', 'ransomware', 'malware', 'botnet'
    ]
    
    def __init__(self, cost_tier: str = 'balanced'):
        """Initialize Threat Intel Agent.
        
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
        logger.info(f"ThreatIntelAgent initialized: model={self.model}")
    
    def _select_model(self) -> str:
        """Select LLM model based on cost tier."""
        return self.COST_TIERS[self.cost_tier]
    
    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute threat intelligence gathering workflow.
        
        Args:
            data: Task specification containing:
                - technologies: List of technologies to monitor
                - sources: Intelligence sources to query
                - threat_types: Specific threat categories to track
                - time_range: Historical data range (days)
                - correlate_with: Existing vulnerability findings
        
        Returns:
            Dict containing:
                - cves: Relevant CVE identifiers with details
                - exploits: Available exploit code/modules
                - threat_actors: Relevant threat actor profiles
                - attack_patterns: MITRE ATT&CK techniques
                - recommendations: Defensive measures
                - status: Task completion status
        
        Raises:
            ValueError: If required parameters missing
            RuntimeError: If intel gathering fails
        """
        technologies = data.get('technologies', [])
        sources = data.get('sources', self.INTEL_SOURCES)
        threat_types = data.get('threat_types', self.THREAT_TYPES)
        time_range = data.get('time_range', 30)
        correlate = data.get('correlate_with', [])
        
        logger.info(f"Gathering threat intel for {len(technologies)} technologies")
        
        # TODO: Implement threat intelligence logic
        # - Query CVE/NVD databases for recent vulnerabilities
        # - Search ExploitDB and Metasploit for exploit code
        # - Monitor GitHub for PoC releases
        # - Query Shodan for exposed instances
        # - Correlate intel with existing findings
        # - Generate threat actor profiles
        # - Map to MITRE ATT&CK framework
        
        return {
            'status': 'not_implemented',
            'message': 'Full threat intel logic pending',
            'technologies': technologies,
            'sources': sources,
            'threat_types': threat_types,
            'time_range': time_range,
            'cves': [],
            'exploits': [],
            'threat_actors': [],
            'attack_patterns': [],
            'recommendations': []
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
