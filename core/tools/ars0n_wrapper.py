import subprocess
import json
from core import ui
import os

# Path to the ars0n-framework-v2 submodule
ARS0N_FRAMEWORK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ars0n-framework-v2'))

def run_ars0n_scan(target: str, scan_type: str = 'full') -> dict:
    """
    Executes a scan using ars0n-framework-v2 in headless mode.
    
    Args:
        target (str): The target URL or domain.
        scan_type (str): The type of scan to perform (e.g., 'full', 'recon', 'vuln').
                         This depends on ars0n-framework-v2's CLI options.

    Returns:
        dict: A dictionary containing the scan results or an error message.
    """
    ui.print_info(f"Starting ars0n-framework-v2 scan for '{target}' (type: {scan_type})...")
    
    # Construct the command to run ars0n-framework-v2
    # Assuming ars0n-framework-v2 has a CLI like: python3 main.py --target <target> --scan-type <type> --headless --json-output
    # This will need to be adjusted based on the actual CLI arguments of ars0n-framework-v2
    command = [
        'python3',
        os.path.join(ARS0N_FRAMEWORK_PATH, 'main.py'),
        '--target', target,
        '--scan-type', scan_type, # Placeholder for actual scan type arg
        '--headless',
        '--json-output' # Assuming it supports JSON output
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True, # Raise an exception for non-zero exit codes
            timeout=1800 # 30 minutes timeout
        )
        
        # Attempt to parse JSON output
        try:
            output_json = json.loads(result.stdout)
            ui.print_success(f"ars0n-framework-v2 scan completed for '{target}'.")
            return {"status": "success", "results": output_json}
        except json.JSONDecodeError:
            ui.print_warning(f"ars0n-framework-v2 did not return valid JSON output for '{target}'. Raw output: {result.stdout}")
            return {"status": "success", "results": result.stdout, "raw_output": True}

    except FileNotFoundError:
        ui.print_error("python3 command not found or ars0n-framework-v2 main.py not found.")
        return {"status": "error", "message": "ars0n-framework-v2 not properly set up or python3 not in PATH."}
    except subprocess.TimeoutExpired:
        ui.print_error(f"ars0n-framework-v2 scan for '{target}' timed out.")
        return {"status": "error", "message": "Scan timed out."}
    except subprocess.CalledProcessError as e:
        ui.print_error(f"ars0n-framework-v2 scan failed for '{target}': {e.stderr}")
        return {"status": "error", "message": e.stderr}
    except Exception as e:
        ui.print_error(f"An unexpected error occurred during ars0n-framework-v2 scan: {e}")
        return {"status": "error", "message": str(e)}
