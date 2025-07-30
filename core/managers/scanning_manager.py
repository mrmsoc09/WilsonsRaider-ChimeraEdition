import os
import subprocess
import tempfile
import json
from core import ui
from core.managers.state_manager import StateManager

class ScanningManager:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        ui.print_info("ScanningManager initialized.")

    def run(self, assessment_id: int, prioritized_assets: list, prioritized_templates: list):
        ui.print_header(f"Initiating Active Scans on Assessment ID: {assessment_id}")
        self._run_nuclei(assessment_id, prioritized_assets, prioritized_templates)

    def _run_nuclei(self, assessment_id: int, prioritized_assets: list, prioritized_templates: list):
        ui.print_info("Running Nuclei scan...")

        # Create a temporary file to hold the list of targets
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write('\n'.join(prioritized_assets))
            temp_list_path = tmp_file.name

        output_file = os.path.join(tempfile.gettempdir(), f"nuclei_results_{assessment_id}.json")

        # --- RESILIENCE FIX --- #
        # If AI fails, fall back to a default set of templates.
        if not prioritized_templates:
            ui.print_warning("AI prioritization failed or returned no templates. Falling back to default CVE scan.")
            command = ['nuclei', '-l', temp_list_path, '-t', 'cves/', '-jsonl', '-o', output_file]
        else:
            # Use AI-provided templates if available
            command = ['nuclei', '-l', temp_list_path, '-t', ','.join(prioritized_templates), '-jsonl', '-o', output_file]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=1800)
            ui.print_success("Nuclei scan completed.")
            self._process_nuclei_results(assessment_id, output_file)
        except subprocess.CalledProcessError as e:
            ui.print_error(f"Nuclei scan failed:\n{e.stderr}")
        except FileNotFoundError:
            ui.print_error("Nuclei command not found. Please ensure it is installed and in your PATH.")
        finally:
            # Clean up the temporary files
            if os.path.exists(temp_list_path):
                os.remove(temp_list_path)
            if os.path.exists(output_file):
                os.remove(output_file) # Or process and then remove

    def _process_nuclei_results(self, assessment_id: int, output_file: str):
        if not os.path.exists(output_file):
            return
        with open(output_file, 'r') as f:
            for line in f:
                try:
                    finding = json.loads(line)
                    self.state_manager.add_vulnerability(
                        assessment_id=assessment_id,
                        name=finding.get('info', {}).get('name'),
                        severity=finding.get('info', {}).get('severity'),
                        description=finding.get('info', {}).get('description'),
                        remediation='N/A',
                        raw_finding=json.dumps(finding)
                    )
                except json.JSONDecodeError:
                    continue
        ui.print_info("Processed and saved Nuclei findings to the database.")
