import subprocess
from .. import ui

class SubfinderWrapper:
    def __init__(self, domain):
        self.domain = domain

    def run(self):
        ui.print_info(f'Running Subfinder on {self.domain}')
        try:
            command = ['subfinder', '-d', self.domain, '-silent']
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            subdomains = result.stdout.strip().split('\n')
            ui.print_success(f'Subfinder found {len(subdomains)} subdomains.')
            return subdomains
        except FileNotFoundError:
            ui.print_error('Subfinder is not installed or not in PATH. Skipping.')
            return []
        except subprocess.CalledProcessError as e:
            ui.print_error(f'Subfinder scan failed: {e.stderr}')
            return []

