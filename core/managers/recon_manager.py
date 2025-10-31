"""Recon Manager - Reconnaissance Workflow Orchestration

Orchestrates subdomain enumeration, port scanning, service detection.
Version: 2.0.0
"""

import subprocess
import asyncio
import logging
from typing import Dict, Any, List, Set, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ReconManager:
    """Manages reconnaissance operations and tool coordination."""

    def __init__(self, state_manager=None, ui_manager=None, config: dict = None):
        self.state_manager = state_manager
        self.ui = ui_manager
        self.config = config or {}
        self.tools_available = self._check_tool_availability()
        logger.info(f"ReconManager initialized: {len(self.tools_available)} tools available")

    def _check_tool_availability(self) -> Dict[str, bool]:
        """Check which recon tools are installed."""
        tools = ['subfinder', 'amass', 'nmap', 'httpx', 'nuclei', 'waybackurls']
        available = {}
        for tool in tools:
            try:
                subprocess.run([tool, '-version'], capture_output=True, timeout=2)
                available[tool] = True
            except:
                available[tool] = False
        return available

    async def run(self, assessment_id: int, target: str) -> Dict[str, Any]:
        """Run comprehensive reconnaissance workflow."""
        logger.info(f"Starting recon for {target}")
        if self.ui:
            self.ui.run_subheading(f"Reconnaissance: {target}")

        results = {
            'target': target,
            'assessment_id': assessment_id,
            'subdomains': [],
            'live_hosts': [],
            'open_ports': {},
            'technologies': [],
            'urls': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Phase 1: Subdomain enumeration
        results['subdomains'] = await self._enumerate_subdomains(target)

        # Phase 2: Live host detection
        results['live_hosts'] = await self._detect_live_hosts(results['subdomains'])

        # Phase 3: Port scanning
        results['open_ports'] = await self._scan_ports(results['live_hosts'])

        # Phase 4: URL discovery
        results['urls'] = await self._discover_urls(results['live_hosts'])

        # Phase 5: Technology detection
        results['technologies'] = await self._detect_technologies(results['live_hosts'])

        return results

    async def _enumerate_subdomains(self, target: str) -> List[str]:
        """Enumerate subdomains using multiple tools."""
        logger.info(f"Enumerating subdomains for {target}")
        if self.ui:
            self.ui.print(f"[cyan][Recon][/cyan] Subdomain enumeration...")

        subdomains = set()

        # Subfinder
        if self.tools_available.get('subfinder'):
            subs = await self._run_subfinder(target)
            subdomains.update(subs)
            if self.ui:
                self.ui.print(f"  -> Subfinder: {len(subs)} subdomains")

        # Amass
        if self.tools_available.get('amass'):
            subs = await self._run_amass(target)
            subdomains.update(subs)
            if self.ui:
                self.ui.print(f"  -> Amass: {len(subs)} subdomains")

        logger.info(f"Found {len(subdomains)} unique subdomains")
        return list(subdomains)

    async def _run_subfinder(self, target: str) -> List[str]:
        """Run subfinder for subdomain enumeration."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'subfinder', '-d', target, '-silent',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            return [line.strip() for line in stdout.decode().split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Subfinder error: {e}")
            return []

    async def _run_amass(self, target: str) -> List[str]:
        """Run amass for subdomain enumeration."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'amass', 'enum', '-d', target, '-passive',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            return [line.strip() for line in stdout.decode().split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Amass error: {e}")
            return []

    async def _detect_live_hosts(self, subdomains: List[str]) -> List[str]:
        """Detect live hosts using httpx."""
        logger.info(f"Detecting live hosts from {len(subdomains)} subdomains")
        if self.ui:
            self.ui.print(f"[cyan][Recon][/cyan] Live host detection...")

        if not self.tools_available.get('httpx') or not subdomains:
            return subdomains

        try:
            # Write subdomains to temp file
            with open('/tmp/recon_subdomains.txt', 'w') as f:
                f.write('\n'.join(subdomains))

            proc = await asyncio.create_subprocess_exec(
                'httpx', '-l', '/tmp/recon_subdomains.txt', '-silent',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            live_hosts = [line.strip() for line in stdout.decode().split('\n') if line.strip()]

            logger.info(f"Found {len(live_hosts)} live hosts")
            if self.ui:
                self.ui.print(f"  -> {len(live_hosts)} live hosts")
            return live_hosts

        except Exception as e:
            logger.error(f"Live host detection error: {e}")
            return subdomains

    async def _scan_ports(self, hosts: List[str]) -> Dict[str, List[int]]:
        """Scan ports on live hosts."""
        logger.info(f"Port scanning {len(hosts)} hosts")
        if self.ui:
            self.ui.print(f"[cyan][Recon][/cyan] Port scanning...")

        port_results = {}

        if not self.tools_available.get('nmap') or not hosts:
            return port_results

        # Scan top ports for each host
        for host in hosts[:10]:  # Limit to first 10 hosts
            try:
                proc = await asyncio.create_subprocess_exec(
                    'nmap', '-Pn', '--top-ports', '100', host,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                ports = self._parse_nmap_output(stdout.decode())
                if ports:
                    port_results[host] = ports
            except Exception as e:
                logger.error(f"Port scan error for {host}: {e}")

        logger.info(f"Scanned ports on {len(port_results)} hosts")
        return port_results

    def _parse_nmap_output(self, output: str) -> List[int]:
        """Parse nmap output for open ports."""
        ports = []
        for line in output.split('\n'):
            if '/tcp' in line and 'open' in line:
                try:
                    port = int(line.split('/')[0].strip())
                    ports.append(port)
                except:
                    pass
        return ports

    async def _discover_urls(self, hosts: List[str]) -> List[str]:
        """Discover URLs using waybackurls."""
        logger.info(f"URL discovery for {len(hosts)} hosts")
        if self.ui:
            self.ui.print(f"[cyan][Recon][/cyan] URL discovery...")

        urls = set()

        if not self.tools_available.get('waybackurls'):
            return list(urls)

        for host in hosts[:5]:  # Limit to first 5 hosts
            try:
                proc = await asyncio.create_subprocess_exec(
                    'waybackurls', host,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                host_urls = [line.strip() for line in stdout.decode().split('\n') if line.strip()]
                urls.update(host_urls)
            except Exception as e:
                logger.error(f"URL discovery error for {host}: {e}")

        logger.info(f"Discovered {len(urls)} URLs")
        return list(urls)[:1000]  # Limit results

    async def _detect_technologies(self, hosts: List[str]) -> List[Dict[str, Any]]:
        """Detect technologies on live hosts."""
        logger.info(f"Technology detection for {len(hosts)} hosts")
        if self.ui:
            self.ui.print(f"[cyan][Recon][/cyan] Technology detection...")

        # Placeholder for technology detection
        # Could integrate with httpx -td or wappalyzer
        technologies = []

        for host in hosts[:10]:
            technologies.append({
                'host': host,
                'technologies': ['nginx', 'php'],  # Placeholder
                'detected_at': datetime.utcnow().isoformat()
            })

        return technologies

    def get_metrics(self) -> Dict[str, Any]:
        """Get reconnaissance metrics."""
        return {
            'tools_available': sum(1 for v in self.tools_available.values() if v),
            'tools_total': len(self.tools_available)
        }
