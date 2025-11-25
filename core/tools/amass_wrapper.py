"""Amass Wrapper - Production-Grade Subdomain Enumeration

Comprehensive wrapper for OWASP Amass with active/passive modes,
API integrations, and result deduplication.
Version: 1.0.0
"""

import subprocess
import json
import logging
import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AmassWrapper:
    """Production-grade Amass subdomain enumeration wrapper."""

    def __init__(self,
                 output_dir: str = "/tmp/amass",
                 config_file: Optional[str] = None,
                 rate_limit: int = 10,
                 timeout: int = 3600):
        """
        Initialize Amass wrapper.

        Args:
            output_dir: Output directory for results
            config_file: Path to Amass config file (for API keys)
            rate_limit: Max requests per second
            timeout: Maximum execution time in seconds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_file
        self.rate_limit = rate_limit
        self.timeout = timeout

        # Check if amass is installed
        try:
            subprocess.run(['amass', '-version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError("Amass not installed. Install from: https://github.com/OWASP/Amass")

    def enum_passive(self,
                     domain: str,
                     sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run passive subdomain enumeration.

        Args:
            domain: Target domain
            sources: Specific data sources to use (e.g., ['virustotal', 'censys'])

        Returns:
            Dict with subdomains and metadata
        """
        logger.info(f"Starting Amass passive enumeration for {domain}")

        output_file = self.output_dir / f"{domain}_passive.json"

        command = [
            'amass', 'enum',
            '-passive',
            '-d', domain,
            '-json', str(output_file),
            '-timeout', str(self.timeout // 60),  # Convert to minutes
        ]

        if self.config_file:
            command.extend(['-config', self.config_file])

        if sources:
            command.extend(['-src'])
            for source in sources:
                command.append(source)

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            duration = time.time() - start_time

            # Parse JSON output
            subdomains = self._parse_json_output(output_file)

            logger.info(f"Amass passive found {len(subdomains)} subdomains in {duration:.2f}s")

            return {
                "domain": domain,
                "mode": "passive",
                "subdomains": subdomains,
                "count": len(subdomains),
                "duration": duration,
                "output_file": str(output_file)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Amass passive timed out after {self.timeout}s")
            return {"error": "timeout", "domain": domain, "subdomains": []}
        except Exception as e:
            logger.error(f"Amass passive failed: {e}")
            return {"error": str(e), "domain": domain, "subdomains": []}

    def enum_active(self,
                    domain: str,
                    brute_force: bool = False,
                    wordlist: Optional[str] = None,
                    resolvers: Optional[str] = None) -> Dict[str, Any]:
        """
        Run active subdomain enumeration with DNS resolution.

        Args:
            domain: Target domain
            brute_force: Enable brute-force enumeration
            wordlist: Custom wordlist for brute-forcing
            resolvers: Custom DNS resolvers file

        Returns:
            Dict with subdomains, IPs, and metadata
        """
        logger.info(f"Starting Amass active enumeration for {domain}")

        output_file = self.output_dir / f"{domain}_active.json"

        command = [
            'amass', 'enum',
            '-active',
            '-d', domain,
            '-json', str(output_file),
            '-timeout', str(self.timeout // 60),
        ]

        if self.config_file:
            command.extend(['-config', self.config_file])

        if brute_force:
            command.append('-brute')
            if wordlist:
                command.extend(['-w', wordlist])

        if resolvers:
            command.extend(['-r', resolvers])

        # Rate limiting
        command.extend(['-max-dns-queries', str(self.rate_limit)])

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            duration = time.time() - start_time

            # Parse JSON output with IP addresses
            subdomains = self._parse_json_output(output_file)

            logger.info(f"Amass active found {len(subdomains)} subdomains in {duration:.2f}s")

            return {
                "domain": domain,
                "mode": "active",
                "subdomains": subdomains,
                "count": len(subdomains),
                "duration": duration,
                "output_file": str(output_file)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Amass active timed out after {self.timeout}s")
            return {"error": "timeout", "domain": domain, "subdomains": []}
        except Exception as e:
            logger.error(f"Amass active failed: {e}")
            return {"error": str(e), "domain": domain, "subdomains": []}

    def enum_comprehensive(self, domain: str) -> Dict[str, Any]:
        """
        Run comprehensive enumeration (passive + active).

        Args:
            domain: Target domain

        Returns:
            Combined results from passive and active scans
        """
        logger.info(f"Starting comprehensive Amass enumeration for {domain}")

        # Run passive first (faster, stealthier)
        passive_results = self.enum_passive(domain)

        # Then run active for verification and additional discovery
        active_results = self.enum_active(domain)

        # Combine and deduplicate
        all_subdomains = {}

        for sub in passive_results.get("subdomains", []):
            all_subdomains[sub["name"]] = sub

        for sub in active_results.get("subdomains", []):
            if sub["name"] in all_subdomains:
                # Merge data (active has IPs)
                all_subdomains[sub["name"]].update(sub)
            else:
                all_subdomains[sub["name"]] = sub

        combined_list = list(all_subdomains.values())

        return {
            "domain": domain,
            "mode": "comprehensive",
            "subdomains": combined_list,
            "count": len(combined_list),
            "passive_count": passive_results.get("count", 0),
            "active_count": active_results.get("count", 0),
            "duration": passive_results.get("duration", 0) + active_results.get("duration", 0)
        }

    def intel(self, organization: str, whois: bool = True) -> Dict[str, Any]:
        """
        Gather intelligence on organization to find root domains.

        Args:
            organization: Organization name
            whois: Include WHOIS reverse lookups

        Returns:
            Dict with discovered root domains
        """
        logger.info(f"Starting Amass intel for organization: {organization}")

        output_file = self.output_dir / f"{organization}_intel.txt"

        command = [
            'amass', 'intel',
            '-org', organization,
            '-o', str(output_file)
        ]

        if whois:
            command.append('-whois')

        if self.config_file:
            command.extend(['-config', self.config_file])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Read discovered domains
            domains = []
            if output_file.exists():
                with open(output_file, 'r') as f:
                    domains = [line.strip() for line in f if line.strip()]

            logger.info(f"Amass intel found {len(domains)} root domains")

            return {
                "organization": organization,
                "domains": domains,
                "count": len(domains),
                "output_file": str(output_file)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Amass intel timed out")
            return {"error": "timeout", "organization": organization, "domains": []}
        except Exception as e:
            logger.error(f"Amass intel failed: {e}")
            return {"error": str(e), "organization": organization, "domains": []}

    def _parse_json_output(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse Amass JSON output file."""
        subdomains = []

        if not json_file.exists():
            logger.warning(f"Output file not found: {json_file}")
            return subdomains

        try:
            with open(json_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        subdomain = {
                            "name": data.get("name"),
                            "domain": data.get("domain"),
                            "addresses": [
                                {
                                    "ip": addr.get("ip"),
                                    "cidr": addr.get("cidr"),
                                    "asn": addr.get("asn"),
                                    "desc": addr.get("desc")
                                }
                                for addr in data.get("addresses", [])
                            ],
                            "sources": data.get("sources", []),
                            "tag": data.get("tag"),
                            "type": data.get("type")
                        }
                        subdomains.append(subdomain)
                    except json.JSONDecodeError as e:
                        logger.debug(f"Failed to parse JSON line: {e}")
                        continue

        except Exception as e:
            logger.error(f"Failed to read JSON output: {e}")

        return subdomains

    def visualize(self, domain: str, output_format: str = "dot") -> Optional[str]:
        """
        Generate visualization of subdomain relationships.

        Args:
            domain: Target domain
            output_format: Output format (dot, gexf, visjs)

        Returns:
            Path to visualization file
        """
        db_path = self.output_dir / "amass.db"

        if not db_path.exists():
            logger.error("No Amass database found. Run enumeration first.")
            return None

        output_file = self.output_dir / f"{domain}_viz.{output_format}"

        command = [
            'amass', 'viz',
            '-d', domain,
            '-dir', str(self.output_dir),
            '-o', str(output_file)
        ]

        if output_format != "dot":
            command.extend(['-' + output_format])

        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
            logger.info(f"Visualization generated: {output_file}")
            return str(output_file)
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            return None
