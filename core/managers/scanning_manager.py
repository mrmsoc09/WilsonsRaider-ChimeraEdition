"""Scanning Manager - Vulnerability Scanning Orchestration

Orchestrates multiple vulnerability scanning tools with OPSEC controls.
Version: 2.0.0
"""

import os
import subprocess
import tempfile
import json
<<<<<<< HEAD
from core import ui
from core.managers.state_manager import StateManager, Asset
=======
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

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

<<<<<<< HEAD
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write('\n'.join(prioritized_assets))
            temp_list_path = tmp_file.name
=======
        results = {
            'assessment_id': assessment_id,
            'scans_completed': [],
            'findings': [],
            'timestamp': datetime.utcnow().isoformat()
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

        # Run Nuclei
        if self.tools_available.get('nuclei'):
            nuclei_results = await self._run_nuclei(assessment_id, prioritized_assets, prioritized_templates)
            results['scans_completed'].append('nuclei')
            results['findings'].extend(nuclei_results)

<<<<<<< HEAD
        if not prioritized_templates:
            ui.print_warning("AI prioritization failed or returned no templates. Falling back to default CVE scan.")
            command = ['nuclei', '-l', temp_list_path, '-t', 'cves/', '-jsonl', '-o', output_file]
        else:
            command = ['nuclei', '-l', temp_list_path, '-t', ', '.join(prioritized_templates), '-jsonl', '-o', output_file]

import os
import subprocess
import tempfile
import json
from core import ui
from core.managers.state_manager import StateManager, Asset
from core.tools.ars0n_wrapper import run_ars0n_scan

class ScanningManager:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        ui.print_info("ScanningManager initialized.")

    def run(self, assessment_id: int, prioritized_assets: list, prioritized_templates: list):
        ui.print_header(f"Initiating Active Scans on Assessment ID: {assessment_id}")
        
        # Run Nuclei scan
        self._run_nuclei(assessment_id, prioritized_assets, prioritized_templates)

        # Run ars0n-framework-v2 scan
        # For now, ars0n-framework-v2 will run on the first prioritized asset as a full scan.
        # This can be made more sophisticated later.
        if prioritized_assets:
            self._run_ars0n_framework_scan(assessment_id, prioritized_assets[0])

    def _run_nuclei(self, assessment_id: int, prioritized_assets: list, prioritized_templates: list):
        ui.print_info("Running Nuclei scan...")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write('\n'.join(prioritized_assets))
            temp_list_path = tmp_file.name

        output_file = os.path.join(tempfile.gettempdir(), f"nuclei_results_{assessment_id}.json")

        if not prioritized_templates:
            ui.print_warning("AI prioritization failed or returned no templates. Falling back to default CVE scan.")
            command = ['nuclei', '-l', temp_list_path, '-t', 'cves/', '-jsonl', '-o', output_file]
        else:
            command = ['nuclei', '-l', temp_list_path, '-t', ', '.join(prioritized_templates), '-jsonl', '-o', output_file]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=1800)
            ui.print_success("Nuclei scan completed.")
            self._process_nuclei_results(assessment_id, output_file)
        except subprocess.CalledProcessError as e:
            ui.print_warning(f"Nuclei scan finished. Processing results.")
            self._process_nuclei_results(assessment_id, output_file)
        except FileNotFoundError:
            ui.print_warning("Nuclei command not found. Skipping scan.")
            with open(output_file, 'w') as f:
                f.write('')
            self._process_nuclei_results(assessment_id, output_file)
        finally:
            if os.path.exists(temp_list_path):
                os.remove(temp_list_path)
            if os.path.exists(output_file):
                os.remove(output_file)

    def _process_nuclei_results(self, assessment_id: int, output_file: str):
        if not os.path.exists(output_file):
            ui.print_warning("Nuclei output file not found. No results to process.")
            return

        session = self.state_manager.get_session()
=======
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

>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
        try:
            with open(output_file, 'r') as f:
                for line in f:
                    try:
<<<<<<< HEAD
                        finding = json.loads(line)
                        host = finding.get('host')
                        if not host:
                            continue

                        vuln_data = {
                            'name': finding.get('info', {}).get('name'),
                            'severity': finding.get('info', {}).get('severity'),
                            'description': finding.get('info', {}).get('description'),
                            'raw_finding': json.dumps(finding),
                            'tool': 'nuclei'
                        }
                        
                        self.state_manager.add_vulnerability(
                            assessment_id=assessment_id,
                            asset_id=asset.id,
                            vuln_data=vuln_data
                        )
                    except json.JSONDecodeError:
                        continue
            ui.print_info("Processed and saved Nuclei findings to the database.")
        finally:
            session.close()

    def _run_ars0n_framework_scan(self, assessment_id: int, target_asset: str):
        """
        Runs ars0n-framework-v2 scan on a given target asset.
        """
        ui.print_info(f"Running ars0n-framework-v2 scan on {target_asset}...")
        ars0n_results = run_ars0n_scan(target_asset, scan_type='full')

        if ars0n_results.get('status') == 'success':
            ui.print_success(f"ars0n-framework-v2 scan completed for {target_asset}.")
            self._process_ars0n_results(assessment_id, target_asset, ars0n_results.get('results'))
        else:
            ui.print_error(f"ars0n-framework-v2 scan failed for {target_asset}: {ars0n_results.get('message', 'Unknown error')}")

    def _process_ars0n_results(self, assessment_id: int, target_asset_name: str, results: dict | str):
        """
        Processes results from ars0n-framework-v2 and saves them to the database.
        """
        if not results:
            ui.print_warning(f"No ars0n-framework-v2 results to process for {target_asset_name}.")
            return

        session = self.state_manager.get_session()
        try:
            asset = session.query(Asset).filter_by(assessment_id=assessment_id, name=target_asset_name).first()
            if not asset:
                ui.print_warning(f"Could not find asset for host: {target_asset_name}. Skipping ars0n findings.")
                return

            if isinstance(results, dict) and results.get('vulnerabilities'):
                for vuln_entry in results['vulnerabilities']:
                    vuln_data = {
                        'name': vuln_entry.get('name', 'Ars0n Framework Finding'),
                        'severity': vuln_entry.get('severity', 'unknown'),
                        'description': vuln_entry.get('description', 'No description provided.'),
                        'raw_finding': json.dumps(vuln_entry),
                        'tool': 'ars0n-framework-v2'
                    }
                    self.state_manager.add_vulnerability(
                        assessment_id=assessment_id,
                        asset_id=asset.id,
                        vuln_data=vuln_data
                    )
                ui.print_info(f"Processed and saved {len(results['vulnerabilities'])} ars0n-framework-v2 findings to the database.")
            elif isinstance(results, str):
                ui.print_info(f"Ars0n-framework-v2 returned raw string output. Saving as a single finding.")
                vuln_data = {
                    'name': 'Ars0n Framework Raw Output',
                    'severity': 'info',
                    'description': 'Raw output from ars0n-framework-v2 scan.',
                    'raw_finding': results,
                    'tool': 'ars0n-framework-v2'
                }
                self.state_manager.add_vulnerability(
                    assessment_id=assessment_id,
                    asset_id=asset.id,
                    vuln_data=vuln_data
                )
            else:
                ui.print_warning(f"Unknown ars0n-framework-v2 result format for {target_asset_name}.")
        finally:
            session.close()
=======
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
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
