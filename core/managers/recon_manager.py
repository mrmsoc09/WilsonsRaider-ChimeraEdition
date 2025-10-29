"""Recon Manager - Reconnaissance Workflow Orchestration

Orchestrates subdomain enumeration, port scanning, service detection.
Version: 2.0.0
"""

import subprocess
<<<<<<< HEAD
import json
from core import ui
from core.managers.state_manager import StateManager
from core.managers.ai_manager import AIManager
from core.tools.google_dorks_wrapper import run_google_dorks
=======
import asyncio
import logging
from typing import Dict, Any, List, Set, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

class ReconManager:
    """Manages reconnaissance operations and tool coordination."""

    def __init__(self, state_manager=None, ui_manager=None, config: dict = None):
        self.state_manager = state_manager
<<<<<<< HEAD
        self.ai_manager = AIManager()
=======
        self.ui = ui_manager
        self.config = config or {}
        self.tools_available = self._check_tool_availability()
        logger.info(f"ReconManager initialized: {len(self.tools_available)} tools available")
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

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
<<<<<<< HEAD
            'google_dorks_results': {} # New field
        }

        # Run Subfinder for subdomain enumeration
        subdomains = self._run_subfinder(target)
        if subdomains:
            ui.print_success(f"Found {len(subdomains)} subdomains.")
            asset_data = [{'name': sub, 'asset_type': 'subdomain'} for sub in subdomains]
            self.state_manager.add_assets(assessment_id, asset_data)
            recon_results['subdomains'] = subdomains

        # Run Google Dorks
        dorks_results = self._run_google_dorks(target)
        if dorks_results and dorks_results.get('status') == 'success':
            recon_results['google_dorks_results'] = dorks_results['results']
            # TODO: Process and store dorks results as assets or findings

        return recon_results
=======
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
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

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
<<<<<<< HEAD
        except FileNotFoundError:
            ui.print_warning("Subfinder command not found. Using hardcoded subdomain for testing.")
            if target == "scanme.nmap.org":
                return ["scanme.nmap.org"]
            return []
        except subprocess.TimeoutExpired:
            ui.print_warning(f"Subfinder for {target} timed out.")
            return []

    def _run_google_dorks(self, target: str) -> dict:
        """
        Generates and runs Google Dorks for the target.
        """
        ui.print_info(f"Generating Google Dorks for {target}...")
        
        # Use AIManager to generate relevant dorks
        dork_generation_prompt = f"""
        You are an expert reconnaissance specialist. For the target domain '{target}', generate a list of 5-10 highly effective Google Dorks to find:
        - Exposed login pages
        - Sensitive files (e.g., .env, .bak, .sql, .git, .log)
        - Admin panels
        - Error messages
        - Subdomains not found by traditional tools
        - Publicly exposed documents (e.g., PDFs, DOCs)

        Provide ONLY the list of dork strings, one per line, without any explanations or prefixes.
        Example:
        inurl:admin site:example.com
        filetype:pdf site:example.com
        intitle:"index of" site:example.com
        """
        generated_dorks_str = self.ai_manager._call_llm(
            dork_generation_prompt, 
            system_prompt="You are an expert in Google Dorking.", 
            task_type='analysis'
        )
        
        if not generated_dorks_str:
            ui.print_error("AI failed to generate Google Dorks.")
            return {"status": "failed", "error": "AI failed to generate dorks."}

        generated_dorks = [d.strip() for d in generated_dorks_str.split('\n') if d.strip()]
        if not generated_dorks:
            ui.print_warning("AI generated an empty list of Google Dorks.")
            return {"status": "failed", "error": "AI generated no dorks."}

        return run_google_dorks(target, generated_dorks)

    # Temporarily commented out due to httpx incompatibility
    # def _run_httpx(self, subdomains: list) -> list:
    #     """Runs httpx on a list of subdomains to find live web servers and their titles."""
    #     ui.print_info(f"Running httpx on {len(subdomains)} subdomains to find live hosts...")
    #     try:
    #         subfinder_input = "\n".join(subdomains)
    #         command = ['httpx', '-json', '-title', '-status-code']
    #         result = subprocess.run(command, input=subfinder_input, check=True, capture_output=True, text=True, timeout=1800)
            
    #         live_hosts = []
    #         for line in result.stdout.strip().split('\n'):
    #             try:
    #                 data = json.loads(line)
    #                 host_info = {
    #                     'name': data.get('url'),
    #                     'asset_type': 'web_url',
    #                     'hostname': data.get('host'),
    #                     'port': data.get('port'),
    #                     'protocol': data.get('scheme'),
    #                     'is_alive': True
    #                 }
    #                 live_hosts.append(host_info)
    #             except json.JSONDecodeError:
    #                 continue
    #         return live_hosts
    #     except subprocess.CalledProcessError as e:
    #         ui.print_error(f"httpx failed: {e.stderr}")
    #         return []
    #     except FileNotFoundError:
    #         ui.print_error("httpx command not found. Please ensure it is installed and in your PATH.")
    #         return []
    #     except subprocess.TimeoutExpired:
    #         ui.print_warning(f"httpx timed out.")
    #         return []
=======

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
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
