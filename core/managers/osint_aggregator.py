"""OSINT Aggregator - Unified Intelligence Collection

Comprehensive OSINT manager combining Google Dorks, free APIs,
government data sources, and bug bounty reconnaissance tools.
Version: 1.0.0
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Import OSINT tools
from core.tools.google_dorks_wrapper import GoogleDorksWrapper
from core.tools.osint_apis_wrapper import OSINTAPIsWrapper
from core.tools.amass_wrapper import AmassWrapper
from core.tools.subfinder_wrapper import SubfinderWrapper
from core.tools.httpx_wrapper import HttpxWrapper
from core.tools.waybackurls_wrapper import ArchiveURLWrapper

logger = logging.getLogger(__name__)


class OSINTAggregator:
    """
    Unified OSINT intelligence aggregator.

    Combines multiple free/open-source OSINT sources:
    - Google Dorking
    - Certificate Transparency (crt.sh)
    - DNS/WHOIS lookups
    - IP Geolocation
    - ASN information
    - GitHub code search
    - Wayback Machine
    - Have I Been Pwned
    - SEC EDGAR filings
    - Subdomain enumeration (Amass, Subfinder)
    - HTTP probing (httpx)
    """

    def __init__(self,
                 output_dir: str = "/tmp/osint",
                 use_paid_apis: bool = False):
        """
        Initialize OSINT Aggregator.

        Args:
            output_dir: Output directory for results
            use_paid_apis: Enable paid API tiers (Shodan, etc.)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_paid_apis = use_paid_apis

        logger.info("Initializing OSINT Aggregator...")

        # Initialize tools
        try:
            self.google_dorks = GoogleDorksWrapper()
        except Exception as e:
            logger.warning(f"Google Dorks not available: {e}")
            self.google_dorks = None

        try:
            self.osint_apis = OSINTAPIsWrapper()
        except Exception as e:
            logger.warning(f"OSINT APIs not available: {e}")
            self.osint_apis = None

        try:
            self.amass = AmassWrapper(output_dir=str(self.output_dir / "amass"))
        except Exception as e:
            logger.warning(f"Amass not available: {e}")
            self.amass = None

        try:
            self.httpx = HttpxWrapper(output_dir=str(self.output_dir / "httpx"))
        except Exception as e:
            logger.warning(f"Httpx not available: {e}")
            self.httpx = None

        try:
            self.archive_urls = ArchiveURLWrapper(output_dir=str(self.output_dir / "archive"))
        except Exception as e:
            logger.warning(f"Archive URL tools not available: {e}")
            self.archive_urls = None

        logger.info("OSINT Aggregator initialized")

    def comprehensive_recon(self, target_domain: str) -> Dict[str, Any]:
        """
        Run comprehensive OSINT reconnaissance on target.

        Args:
            target_domain: Target domain (e.g., example.com)

        Returns:
            Complete OSINT intelligence report
        """
        logger.info(f"Starting comprehensive OSINT on {target_domain}")

        report = {
            "target": target_domain,
            "timestamp": datetime.utcnow().isoformat(),
            "sources_used": [],
            "subdomains": [],
            "live_hosts": [],
            "urls": [],
            "technologies": [],
            "google_dorks": {},
            "osint_data": {},
            "github_exposure": [],
            "credential_exposure": [],
            "exposed_files": {},
            "admin_panels": [],
            "error_pages": [],
            "total_findings": 0
        }

        # Phase 1: Google Dorking
        if self.google_dorks:
            logger.info("Phase 1: Google Dorking")
            report["sources_used"].append("Google Dorks")

            try:
                # Run comprehensive dorks
                dork_results = self.google_dorks.dork_site(target_domain, category="all")
                report["google_dorks"] = dork_results

                # Extract interesting findings
                if "exposed_files" in dork_results.get("categories", {}):
                    report["exposed_files"] = dork_results["categories"]["exposed_files"]

                if "admin_panels" in dork_results.get("categories", {}):
                    admin_results = dork_results["categories"]["admin_panels"]["results"]
                    report["admin_panels"] = [r["url"] for r in admin_results]

                if "error_messages" in dork_results.get("categories", {}):
                    error_results = dork_results["categories"]["error_messages"]["results"]
                    report["error_pages"] = [r["url"] for r in error_results]

            except Exception as e:
                logger.error(f"Google Dorking failed: {e}")

        # Phase 2: Free OSINT APIs
        if self.osint_apis:
            logger.info("Phase 2: Free OSINT APIs")
            report["sources_used"].append("Free OSINT APIs")

            try:
                osint_data = self.osint_apis.comprehensive_osint(target_domain)
                report["osint_data"] = osint_data

                # Extract subdomains from cert transparency
                cert_subdomains = osint_data.get("subdomains", [])
                report["subdomains"].extend(cert_subdomains)

                # GitHub exposure
                report["github_exposure"] = osint_data.get("github_exposure", [])

                # Archived URLs
                report["urls"].extend(osint_data.get("archived_urls", [])[:500])

            except Exception as e:
                logger.error(f"OSINT APIs failed: {e}")

        # Phase 3: Subdomain Enumeration
        if self.amass:
            logger.info("Phase 3: Subdomain Enumeration (Amass)")
            report["sources_used"].append("Amass")

            try:
                amass_results = self.amass.enum_comprehensive(target_domain)
                amass_subdomains = [s["name"] for s in amass_results.get("subdomains", [])]
                report["subdomains"].extend(amass_subdomains)

            except Exception as e:
                logger.error(f"Amass enumeration failed: {e}")

        # Deduplicate subdomains
        report["subdomains"] = list(set(report["subdomains"]))

        # Phase 4: HTTP Probing
        if self.httpx and report["subdomains"]:
            logger.info("Phase 4: HTTP Probing")
            report["sources_used"].append("httpx")

            try:
                # Build URLs from subdomains
                urls_to_probe = []
                for subdomain in report["subdomains"][:200]:  # Limit for performance
                    urls_to_probe.append(f"https://{subdomain}")

                httpx_results = self.httpx.probe_urls(urls_to_probe, tech_detect=True)
                report["live_hosts"] = httpx_results.get("live_hosts", [])

                # Extract technologies
                for host in report["live_hosts"]:
                    report["technologies"].extend(host.get("technologies", []))

                report["technologies"] = list(set(report["technologies"]))

            except Exception as e:
                logger.error(f"HTTP probing failed: {e}")

        # Phase 5: URL Discovery
        if self.archive_urls:
            logger.info("Phase 5: Historical URL Discovery")
            report["sources_used"].append("Wayback Machine / GAU")

            try:
                archive_results = self.archive_urls.fetch_urls(target_domain, include_subs=True)
                report["urls"].extend(archive_results.get("urls", [])[:1000])
                report["url_categories"] = archive_results.get("categorized", {})

            except Exception as e:
                logger.error(f"URL discovery failed: {e}")

        # Calculate totals
        report["total_findings"] = (
            len(report["subdomains"]) +
            len(report["live_hosts"]) +
            len(report["urls"]) +
            len(report["github_exposure"]) +
            len(report["admin_panels"]) +
            len(report["error_pages"])
        )

        logger.info(f"OSINT complete: {report['total_findings']} total findings")

        return report

    def search_credentials(self, domain: str, check_breaches: bool = True) -> Dict[str, Any]:
        """
        Search for exposed credentials (use ethically!).

        Args:
            domain: Target domain
            check_breaches: Check breach databases

        Returns:
            Credential exposure findings
        """
        logger.warning(f"Searching for credential exposure on {domain} (SENSITIVE)")

        results = {
            "domain": domain,
            "google_dorks": [],
            "github_exposure": [],
            "breach_data": []
        }

        # Google Dorks for credentials
        if self.google_dorks:
            cred_results = self.google_dorks.find_exposed_credentials(domain)
            results["google_dorks"] = cred_results

        # GitHub search for secrets
        if self.osint_apis:
            github_results = self.osint_apis.github_search(f"{domain} password", in_code=True)
            results["github_exposure"] = github_results

            # Also search for API keys
            api_key_results = self.osint_apis.github_search(f"{domain} api_key", in_code=True)
            results["github_exposure"].extend(api_key_results)

        # Breach database check (if emails known)
        # Note: This requires emails to be discovered first

        return results

    def search_company_intel(self, company_name: str) -> Dict[str, Any]:
        """
        Gather intelligence on a company using government/public sources.

        Args:
            company_name: Company name

        Returns:
            Company intelligence
        """
        logger.info(f"Gathering company intelligence: {company_name}")

        intel = {
            "company": company_name,
            "sec_filings": [],
            "whois_data": {},
            "related_domains": []
        }

        # SEC EDGAR filings
        if self.osint_apis:
            sec_results = self.osint_apis.sec_edgar_search(company_name)
            intel["sec_filings"] = sec_results

            # Extract domains from SEC filings (would require parsing filing text)
            # This is a placeholder for enhanced implementation

        return intel

    def monitor_domain(self, domain: str) -> Dict[str, Any]:
        """
        Monitor domain for changes (new subdomains, certs, etc.).

        Args:
            domain: Domain to monitor

        Returns:
            Monitoring report with changes
        """
        logger.info(f"Monitoring domain: {domain}")

        # Get current state
        current_state = self.comprehensive_recon(domain)

        # Save for comparison (would implement database storage)
        # Compare with previous state to detect changes

        return {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "current_subdomains": len(current_state["subdomains"]),
            "current_urls": len(current_state["urls"]),
            "new_subdomains": [],  # Placeholder
            "new_certificates": [],  # Placeholder
            "changes_detected": False
        }

    def export_report(self, report: Dict[str, Any], format: str = "json") -> str:
        """
        Export OSINT report to file.

        Args:
            report: Report data
            format: Output format (json, markdown, html)

        Returns:
            Path to exported file
        """
        target = report.get("target", "unknown")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            output_file = self.output_dir / f"{target}_osint_{timestamp}.json"

            import json
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

        elif format == "markdown":
            output_file = self.output_dir / f"{target}_osint_{timestamp}.md"

            with open(output_file, 'w') as f:
                f.write(f"# OSINT Report: {target}\n\n")
                f.write(f"**Generated**: {report.get('timestamp')}\n\n")
                f.write(f"**Total Findings**: {report.get('total_findings')}\n\n")

                f.write(f"## Subdomains ({len(report.get('subdomains', []))})\n\n")
                for subdomain in report.get("subdomains", [])[:100]:
                    f.write(f"- {subdomain}\n")

                f.write(f"\n## Live Hosts ({len(report.get('live_hosts', []))})\n\n")
                for host in report.get("live_hosts", [])[:50]:
                    f.write(f"- {host.get('url')} - {host.get('title')}\n")

                f.write(f"\n## Technologies Detected\n\n")
                for tech in report.get("technologies", []):
                    f.write(f"- {tech}\n")

                if report.get("admin_panels"):
                    f.write(f"\n## Admin Panels Found ({len(report['admin_panels'])})\n\n")
                    for panel in report["admin_panels"][:20]:
                        f.write(f"- {panel}\n")

                if report.get("github_exposure"):
                    f.write(f"\n## GitHub Exposure ({len(report['github_exposure'])})\n\n")
                    for item in report["github_exposure"][:20]:
                        f.write(f"- {item.get('repository')} - {item.get('path')}\n")

        logger.info(f"Report exported to: {output_file}")

        return str(output_file)

    def get_status(self) -> Dict[str, bool]:
        """Get status of all OSINT tools."""
        return {
            "google_dorks": self.google_dorks is not None,
            "osint_apis": self.osint_apis is not None,
            "amass": self.amass is not None,
            "httpx": self.httpx is not None,
            "archive_urls": self.archive_urls is not None
        }
