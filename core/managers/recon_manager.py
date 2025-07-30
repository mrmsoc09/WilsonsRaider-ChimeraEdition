import subprocess
from core import ui
from core.managers.state_manager import StateManager

class ReconManager:
    """Manages the initial reconnaissance phase."""

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def run(self, assessment_id: int, target: str) -> dict:
        """Runs a series of reconnaissance tools against the target."""
        recon_results = {
            'target': target,
            'subdomains': [],
        }

        # Run Subfinder for subdomain enumeration
        subdomains = self._run_subfinder(target)
        if subdomains:
            ui.print_success(f"Found {len(subdomains)} subdomains.")
            # Persist the assets to the database
            self.state_manager.add_assets(assessment_id, subdomains)
            recon_results['subdomains'] = subdomains

        return recon_results

    def _run_subfinder(self, target: str) -> list:
        """Runs subfinder to discover subdomains."""
        ui.print_info(f"Running subfinder on {target}...")
        try:
            command = ['subfinder', '-d', target, '-silent']
            result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=600)
            subdomains = result.stdout.strip().split('\n')
            return [s for s in subdomains if s]
        except subprocess.CalledProcessError as e:
            ui.print_error(f"Subfinder failed: {e.stderr}")
            return []
        except FileNotFoundError:
            ui.print_error("Subfinder command not found. Please ensure it is installed and in your PATH.")
            return []
        except subprocess.TimeoutExpired:
            ui.print_warning(f"Subfinder for {target} timed out.")
            return []
