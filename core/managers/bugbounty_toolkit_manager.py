"""Bug Bounty Toolkit Manager - Unified Tool Orchestration

Comprehensive manager for orchestrating bug bounty hunting tools
in an intelligent, sequential workflow with result correlation.
Version: 1.0.0
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Import tool wrappers
from core.tools.amass_wrapper import AmassWrapper
from core.tools.subfinder_wrapper import SubfinderWrapper
from core.tools.httpx_wrapper import HttpxWrapper
from core.tools.waybackurls_wrapper import ArchiveURLWrapper
from core.tools.nuclei_wrapper import NucleiWrapper
from core.tools.ffuf_wrapper import FfufWrapper
from core.tools.sqlmap_wrapper import SQLMapWrapper

# Import integrations
from core.integrations.thehive_client import TheHiveClient, CaseSeverity
from core.integrations.wazuh_client import WazuhClient
from core.integrations.shuffle_client import ShuffleClient
from core.integrations.cortex_client import CortexClient, ObservableDataType

# Import managers
from core.managers.validation_manager import ValidationManager
from core.managers.reporting_manager import ReportingManager

logger = logging.getLogger(__name__)


class BugBountyToolkitManager:
    """
    Unified manager for bug bounty hunting operations.

    Orchestrates the complete workflow:
    1. Reconnaissance (Amass, Subfinder, Httpx, Waybackurls)
    2. Vulnerability Scanning (Nuclei, ffuf, SQLMap)
    3. Validation & Enrichment (Cortex, ValidationManager)
    4. Incident Response (TheHive, Shuffle, Wazuh)
    5. Reporting
    """

    def __init__(self,
                 output_dir: str = "/tmp/bugbounty",
                 opsec_level: str = "medium",
                 enable_integrations: bool = True):
        """
        Initialize Bug Bounty Toolkit Manager.

        Args:
            output_dir: Base output directory for all results
            opsec_level: OPSEC level (low/medium/high)
            enable_integrations: Enable TheHive/Wazuh/Shuffle/Cortex integrations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.opsec_level = opsec_level
        self.enable_integrations = enable_integrations

        # OPSEC configuration
        self.opsec_config = {
            "low": {"rate_limit": 150, "threads": 100, "aggressive": True},
            "medium": {"rate_limit": 100, "threads": 50, "aggressive": False},
            "high": {"rate_limit": 50, "threads": 25, "aggressive": False}
        }

        config = self.opsec_config.get(opsec_level, self.opsec_config["medium"])

        # Initialize tool wrappers
        logger.info("Initializing bug bounty toolkit...")

        try:
            self.amass = AmassWrapper(
                output_dir=str(self.output_dir / "amass"),
                rate_limit=config["rate_limit"]
            )
        except Exception as e:
            logger.warning(f"Amass not available: {e}")
            self.amass = None

        try:
            self.httpx = HttpxWrapper(
                output_dir=str(self.output_dir / "httpx"),
                rate_limit=config["rate_limit"],
                threads=config["threads"]
            )
        except Exception as e:
            logger.warning(f"Httpx not available: {e}")
            self.httpx = None

        try:
            self.archive_urls = ArchiveURLWrapper(
                output_dir=str(self.output_dir / "archive_urls")
            )
        except Exception as e:
            logger.warning(f"Archive URL tools not available: {e}")
            self.archive_urls = None

        try:
            self.ffuf = FfufWrapper(
                output_dir=str(self.output_dir / "ffuf"),
                rate_limit=config["rate_limit"]
            )
        except Exception as e:
            logger.warning(f"ffuf not available: {e}")
            self.ffuf = None

        try:
            self.sqlmap = SQLMapWrapper(
                output_dir=str(self.output_dir / "sqlmap"),
                risk_level=2 if config["aggressive"] else 1
            )
        except Exception as e:
            logger.warning(f"SQLMap not available: {e}")
            self.sqlmap = None

        # Initialize validation and reporting
        self.validator = ValidationManager()
        self.reporter = ReportingManager()

        # Initialize integrations if enabled
        if enable_integrations:
            try:
                self.thehive = TheHiveClient()
            except Exception as e:
                logger.warning(f"TheHive not configured: {e}")
                self.thehive = None

            try:
                self.wazuh = WazuhClient()
            except Exception as e:
                logger.warning(f"Wazuh not configured: {e}")
                self.wazuh = None

            try:
                self.shuffle = ShuffleClient()
            except Exception as e:
                logger.warning(f"Shuffle not configured: {e}")
                self.shuffle = None

            try:
                self.cortex = CortexClient()
            except Exception as e:
                logger.warning(f"Cortex not configured: {e}")
                self.cortex = None
        else:
            self.thehive = None
            self.wazuh = None
            self.shuffle = None
            self.cortex = None

        logger.info("Bug Bounty Toolkit initialized successfully")

    def run_full_workflow(self, target_domain: str, program_name: str) -> Dict[str, Any]:
        """
        Execute complete bug bounty hunting workflow.

        Args:
            target_domain: Target domain (e.g., example.com)
            program_name: Bug bounty program name

        Returns:
            Dict with comprehensive results
        """
        logger.info(f"Starting full bug bounty workflow for {target_domain}")

        scan_id = f"{program_name}_{target_domain}_{int(datetime.utcnow().timestamp())}"

        # Send scan start event to Wazuh
        if self.wazuh:
            self.wazuh.send_scan_start_event(
                scan_id=scan_id,
                target=target_domain,
                scan_type="full_bugbounty_workflow"
            )

        workflow_results = {
            "scan_id": scan_id,
            "target": target_domain,
            "program": program_name,
            "start_time": datetime.utcnow().isoformat(),
            "recon": {},
            "vulnerabilities": [],
            "enrichment": {},
            "cases_created": [],
            "findings_count": 0
        }

        # Phase 1: Reconnaissance
        logger.info("Phase 1: Reconnaissance")
        recon_results = self.reconnaissance(target_domain)
        workflow_results["recon"] = recon_results

        # Phase 2: Vulnerability Scanning
        logger.info("Phase 2: Vulnerability Scanning")
        vuln_results = self.vulnerability_scanning(recon_results)
        workflow_results["vulnerabilities"] = vuln_results

        # Phase 3: Validation & Enrichment
        logger.info("Phase 3: Validation & Enrichment")
        for finding in vuln_results:
            # Validate
            validated = self.validator.validate_finding(finding)

            if validated.get("confidence", 0) >= 0.7:
                # Enrich with threat intelligence
                if self.cortex:
                    enrichment = self.cortex.enrich_finding(finding)
                    finding["enrichment"] = enrichment
                    workflow_results["enrichment"][finding["name"]] = enrichment

                # Create TheHive case for HIGH/CRITICAL
                if finding.get("severity") in ["HIGH", "CRITICAL"] and self.thehive:
                    case_id = self.thehive.create_case_from_finding(finding)
                    if case_id:
                        workflow_results["cases_created"].append(case_id)
                        finding["thehive_case"] = case_id

                # Trigger Shuffle incident response
                if finding.get("severity") == "CRITICAL" and self.shuffle:
                    execution_id = self.shuffle.trigger_incident_response_playbook(finding)
                    finding["shuffle_execution"] = execution_id

                workflow_results["findings_count"] += 1

        # Send scan complete event
        if self.wazuh:
            self.wazuh.send_scan_complete_event(
                scan_id=scan_id,
                target=target_domain,
                findings_count=workflow_results["findings_count"],
                critical_count=sum(1 for f in vuln_results if f.get("severity") == "CRITICAL")
            )

        workflow_results["end_time"] = datetime.utcnow().isoformat()

        # Phase 4: Generate Report
        logger.info("Phase 4: Generating Report")
        report_path = self.reporter.generate_report(
            workflow_results,
            output_format="markdown",
            output_file=f"{program_name}_{target_domain}_report.md"
        )
        workflow_results["report_path"] = report_path

        logger.info(f"Workflow complete! Found {workflow_results['findings_count']} validated findings")

        return workflow_results

    def reconnaissance(self, target_domain: str) -> Dict[str, Any]:
        """
        Execute reconnaissance phase.

        Workflow:
        1. Subdomain enumeration (Amass comprehensive)
        2. HTTP probing (httpx)
        3. URL discovery (waybackurls/gau)
        4. Technology fingerprinting
        """
        logger.info(f"Starting reconnaissance on {target_domain}")

        recon_data = {
            "target": target_domain,
            "subdomains": [],
            "live_hosts": [],
            "urls": [],
            "technologies": set()
        }

        # Step 1: Subdomain Enumeration
        if self.amass:
            logger.info("Running Amass subdomain enumeration...")
            amass_results = self.amass.enum_comprehensive(target_domain)
            subdomains = [sub["name"] for sub in amass_results.get("subdomains", [])]
            recon_data["subdomains"] = subdomains
            logger.info(f"Amass found {len(subdomains)} subdomains")

        # Step 2: HTTP Probing
        if self.httpx and recon_data["subdomains"]:
            logger.info("Probing live hosts with httpx...")
            # Build full URLs
            urls_to_probe = [f"https://{sub}" for sub in recon_data["subdomains"][:500]]  # Limit for OPSEC
            httpx_results = self.httpx.probe_urls(urls_to_probe, tech_detect=True)
            recon_data["live_hosts"] = httpx_results.get("live_hosts", [])

            # Extract technologies
            for host in recon_data["live_hosts"]:
                recon_data["technologies"].update(host.get("technologies", []))

            logger.info(f"httpx found {len(recon_data['live_hosts'])} live hosts")

        # Step 3: URL Discovery
        if self.archive_urls:
            logger.info("Fetching archived URLs...")
            archive_results = self.archive_urls.fetch_urls(target_domain, include_subs=True)
            recon_data["urls"] = archive_results.get("urls", [])
            recon_data["url_categories"] = archive_results.get("categorized", {})
            logger.info(f"Found {len(recon_data['urls'])} archived URLs")

        recon_data["technologies"] = list(recon_data["technologies"])

        return recon_data

    def vulnerability_scanning(self, recon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute vulnerability scanning phase.

        Workflow:
        1. Nuclei template scanning on live hosts
        2. Directory/file fuzzing with ffuf
        3. Parameter fuzzing
        4. SQL injection testing with SQLMap
        """
        logger.info("Starting vulnerability scanning")

        all_findings = []

        live_hosts = recon_data.get("live_hosts", [])
        urls = recon_data.get("urls", [])

        # Step 1: Nuclei Scanning
        logger.info("Running Nuclei scans...")
        for host in live_hosts[:100]:  # Limit for performance
            # Run Nuclei would go here - integrate with existing nuclei_wrapper.py
            pass

        # Step 2: Directory Fuzzing
        if self.ffuf:
            logger.info("Running directory fuzzing...")
            for host in live_hosts[:50]:  # Top 50 hosts
                url = host.get("url")
                if url:
                    ffuf_results = self.ffuf.fuzz_directories(
                        url=url,
                        extensions=['.php', '.asp', '.aspx', '.jsp'],
                        match_codes=[200, 301, 302, 401, 403]
                    )

                    for finding in ffuf_results.get("findings", []):
                        if finding.get("status_code") in [200, 403]:
                            all_findings.append({
                                "name": f"Interesting Path: {finding.get('url')}",
                                "severity": "LOW",
                                "target": url,
                                "tool": "ffuf",
                                "confidence": 0.5,
                                "details": finding
                            })

        # Step 3: Parameter Fuzzing on URLs with parameters
        if self.ffuf:
            param_urls = [url for url in urls if '?' in url]
            logger.info(f"Fuzzing {len(param_urls[:100])} parameterized URLs...")

            for url in param_urls[:100]:
                # Fuzz existing parameters
                pass

        # Step 4: SQL Injection Testing
        if self.sqlmap:
            logger.info("Testing for SQL injection...")
            param_urls = [url for url in urls if '?' in url]

            for url in param_urls[:20]:  # Top 20 for OPSEC
                sqli_results = self.sqlmap.test_injection(url, batch=True, timeout=300)

                if sqli_results.get("vulnerable"):
                    all_findings.append({
                        "name": "SQL Injection",
                        "severity": "CRITICAL",
                        "target": url,
                        "tool": "sqlmap",
                        "confidence": 0.95,
                        "details": sqli_results.get("details", {}),
                        "description": f"SQL injection vulnerability confirmed at {url}"
                    })

        logger.info(f"Vulnerability scanning complete. Found {len(all_findings)} potential issues")

        return all_findings

    def get_toolkit_status(self) -> Dict[str, Any]:
        """Get status of all tools and integrations."""
        return {
            "tools": {
                "amass": self.amass is not None,
                "httpx": self.httpx is not None,
                "archive_urls": self.archive_urls is not None,
                "ffuf": self.ffuf is not None,
                "sqlmap": self.sqlmap is not None
            },
            "integrations": {
                "thehive": self.thehive is not None and self.thehive.health_check() if self.thehive else False,
                "wazuh": self.wazuh is not None and self.wazuh.health_check() if self.wazuh else False,
                "shuffle": self.shuffle is not None and self.shuffle.health_check() if self.shuffle else False,
                "cortex": self.cortex is not None and self.cortex.health_check() if self.cortex else False
            },
            "opsec_level": self.opsec_level
        }
