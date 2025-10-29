"""Scanning Manager - Vulnerability Scanning Orchestration

Orchestrates multiple vulnerability scanning tools with OPSEC controls.
Version: 2.0.0
"""

import os
import subprocess
import tempfile
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ScanningManager:
    """Manages vulnerability scanning operations."""

    def __init__(self, state_manager=None, opsec_manager=None, ui_manager=None, config: dict = None):
        self.state_manager = state_manager
        self.opsec_manager = opsec_manager
        self.ui = ui_manager
        self.config = config or {}
        self.tools_available = self._check_tool_availability()
        self.temp_dir = Path(tempfile.gettempdir()) / 'scanning'
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"ScanningManager initialized: {len(self.tools_available)} tools available")

    def _check_tool_availability(self) -> Dict[str, bool]:
        """Check which scanning tools are installed."""
        tools = ['nuclei', 'nmap', 'nikto', 'sqlmap', 'wpscan']
        available = {}
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], capture_output=True, timeout=2)
                available[tool] = True
            except:
                available[tool] = False
        return available

    async def run(self, assessment_id: int, prioritized_assets: List[str],
                  prioritized_templates: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive vulnerability scanning."""
        logger.info(f"Starting scans for assessment {assessment_id}")
        if self.ui:
            self.ui.run_subheading(f"Vulnerability Scanning: Assessment {assessment_id}")

        results = {
            'assessment_id': assessment_id,
            'scans_completed': [],
            'findings': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Run Nuclei
        if self.tools_available.get('nuclei'):
            nuclei_results = await self._run_nuclei(assessment_id, prioritized_assets, prioritized_templates)
            results['scans_completed'].append('nuclei')
            results['findings'].extend(nuclei_results)

        # Run Nikto for web servers
        if self.tools_available.get('nikto'):
            nikto_results = await self._run_nikto(assessment_id, prioritized_assets)
            results['scans_completed'].append('nikto')
            results['findings'].extend(nikto_results)

        logger.info(f"Scanning complete: {len(results['findings'])} findings")
        return results

    async def _run_nuclei(self, assessment_id: int, targets: List[str],
                         templates: List[str] = None) -> List[Dict[str, Any]]:
        """Run Nuclei vulnerability scanner."""
        logger.info(f"Running Nuclei on {len(targets)} targets")
        if self.ui:
            self.ui.print("[cyan][Nuclei][/cyan] Starting scan...")

        findings = []

        # Create target list file
        target_file = self.temp_dir / f'nuclei_targets_{assessment_id}.txt'
        with open(target_file, 'w') as f:
            f.write('\n'.join(targets))

        output_file = self.temp_dir / f'nuclei_results_{assessment_id}.json'

        # Build command
        if not templates:
            logger.warning("No templates specified, using default CVE scan")
            if self.ui:
                self.ui.print("[yellow]  -> Using default CVE templates[/yellow]")
            command = ['nuclei', '-l', str(target_file), '-t', 'cves/', '-jsonl', '-o', str(output_file)]
        else:
            command = ['nuclei', '-l', str(target_file), '-t', ','.join(templates), '-jsonl', '-o', str(output_file)]

        # Apply OPSEC rate limiting
        if self.opsec_manager:
            await self.opsec_manager.apply_rate_limit()

        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=1800)

            if proc.returncode == 0:
                logger.info("Nuclei scan completed successfully")
                if self.ui:
                    self.ui.print("[green]  -> Nuclei scan complete[/green]")
                findings = self._process_nuclei_results(assessment_id, output_file)
            else:
                logger.error(f"Nuclei scan failed: {stderr.decode()}")
                if self.ui:
                    self.ui.print("[red]  -> Nuclei scan failed[/red]")

        except asyncio.TimeoutError:
            logger.error("Nuclei scan timed out")
            if self.ui:
                self.ui.print("[red]  -> Nuclei scan timed out[/red]")
        except Exception as e:
            logger.error(f"Nuclei scan error: {e}")
        finally:
            # Cleanup
            if target_file.exists():
                target_file.unlink()

        return findings

    def _process_nuclei_results(self, assessment_id: int, output_file: Path) -> List[Dict[str, Any]]:
        """Process Nuclei JSON output."""
        findings = []

        if not output_file.exists():
            return findings

        try:
            with open(output_file, 'r') as f:
                for line in f:
                    try:
                        result = json.loads(line)
                        finding = {
                            'assessment_id': assessment_id,
                            'tool': 'nuclei',
                            'name': result.get('info', {}).get('name'),
                            'severity': result.get('info', {}).get('severity', 'info').upper(),
                            'description': result.get('info', {}).get('description'),
                            'matched_at': result.get('matched-at'),
                            'template_id': result.get('template-id'),
                            'raw_output': json.dumps(result)
                        }

                        findings.append(finding)

                        # Save to state manager
                        if self.state_manager:
                            self.state_manager.add_vulnerability(
                                assessment_id=assessment_id,
                                name=finding['name'],
                                severity=finding['severity'],
                                description=finding['description'],
                                remediation='See template documentation',
                                raw_finding=finding['raw_output']
                            )

                    except json.JSONDecodeError:
                        continue

            logger.info(f"Processed {len(findings)} Nuclei findings")
            if self.ui:
                self.ui.print(f"  -> Processed {len(findings)} findings")

        except Exception as e:
            logger.error(f"Error processing Nuclei results: {e}")
        finally:
            if output_file.exists():
                output_file.unlink()

        return findings

    async def _run_nikto(self, assessment_id: int, targets: List[str]) -> List[Dict[str, Any]]:
        """Run Nikto web server scanner."""
        logger.info(f"Running Nikto on {len(targets)} targets")
        if self.ui:
            self.ui.print("[cyan][Nikto][/cyan] Starting web server scan...")

        findings = []

        for target in targets[:5]:  # Limit to first 5 targets
            # Apply OPSEC delay
            if self.opsec_manager:
                await self.opsec_manager.apply_stealth_delay()

            output_file = self.temp_dir / f'nikto_{assessment_id}_{target.replace("://", "_").replace("/", "_")}.json'

            try:
                command = ['nikto', '-h', target, '-Format', 'json', '-output', str(output_file)]

                proc = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=600)

                if output_file.exists():
                    with open(output_file, 'r') as f:
                        nikto_data = json.load(f)
                        # Process Nikto findings (format varies)
                        logger.info(f"Nikto scan complete for {target}")
                    output_file.unlink()

            except asyncio.TimeoutError:
                logger.warning(f"Nikto scan timed out for {target}")
            except Exception as e:
                logger.error(f"Nikto scan error for {target}: {e}")

        return findings

    def get_scan_metrics(self, assessment_id: int) -> Dict[str, Any]:
        """Get scanning metrics."""
        findings = []
        if self.state_manager:
            findings = self.state_manager.get_vulnerabilities_for_assessment(assessment_id)

        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        for finding in findings:
            severity = getattr(finding, 'severity', 'INFO').upper()
            if severity in severity_counts:
                severity_counts[severity] += 1

        return {
            'total_findings': len(findings),
            'severity_breakdown': severity_counts,
            'tools_available': sum(1 for v in self.tools_available.values() if v)
        }
