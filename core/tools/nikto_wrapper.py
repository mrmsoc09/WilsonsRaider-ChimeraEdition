import subprocess
from .. import ui

class NiktoWrapper:
    def __init__(self, target):
        self.target = target

    def run(self):
        ui.print_info(f'Running Nikto scan on {self.target}')
        try:
            command = ['nikto', '-h', self.target]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            ui.print_success('Nikto scan completed.')
            return result.stdout
        except FileNotFoundError:
            ui.print_error('Nikto is not installed or not in PATH. Skipping.')
            return None
        except subprocess.CalledProcessError as e:
            # Nikto often exits with a non-zero status code even on success, so we check stderr.
            if '0 host(s) tested' in e.stderr:
                 ui.print_error(f'Nikto could not connect to target: {self.target}')
            else:
                 ui.print_warning(f'Nikto scan finished with findings (or a potential error). Review output.')
            return e.stdout
