import subprocess
from .. import ui

class NucleiWrapper:
    def __init__(self, target):
        self.target = target

    def run(self):
        ui.print_info(f'Running Nuclei scan on {self.target}')
        try:
            # This is a simplified command. In a real scenario, we'd handle templates,
            # output parsing (-json), and error checking much more robustly.
            command = ['nuclei', '-t', 'cves', '-u', self.target]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            ui.print_success('Nuclei scan completed.')
            # A real implementation would parse and return the JSON output.
            return result.stdout
        except FileNotFoundError:
            ui.print_error('Nuclei is not installed or not in PATH. Skipping.')
            return None
        except subprocess.CalledProcessError as e:
            ui.print_error(f'Nuclei scan failed: {e.stderr}')
            return None
