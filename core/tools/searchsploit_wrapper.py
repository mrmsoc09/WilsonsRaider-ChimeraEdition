import subprocess
import json
from core import ui

def search_exploitdb(query: str) -> dict:
    """
    Uses searchsploit to find public exploits in the local Exploit-DB database.
    
    Args:
        query (str): The search term (e.g., 'CVE-2021-44228', 'Apache 2.4.49').

    Returns:
        dict: A dictionary containing the search results or an error message.
    """
    ui.print_info(f"Querying Exploit-DB for: '{query}'...")
    try:
        command = ['searchsploit', '--json', query]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        
        # searchsploit can print non-JSON status lines before the JSON output.
        # We need to find the start of the JSON structure.
        json_output_start = result.stdout.find('{')
        if json_output_start == -1:
            ui.print_warning(f"No valid JSON output from searchsploit for query: '{query}'. It may have found no results.")
            return {"status": "success", "results": []}

        parsed_json = json.loads(result.stdout[json_output_start:])
        ui.print_success(f"Found {len(parsed_json.get('RESULTS_EXPLOIT', []))} potential exploits in Exploit-DB.")
        return {"status": "success", "results": parsed_json.get('RESULTS_EXPLOIT', [])}

    except FileNotFoundError:
        ui.print_error("`searchsploit` command not found. Please install Exploit-DB.")
        return {"status": "error", "message": "searchsploit is not installed."}
    except subprocess.TimeoutExpired:
        ui.print_error("searchsploit command timed out.")
        return {"status": "error", "message": "searchsploit timed out."}
    except subprocess.CalledProcessError as e:
        # searchsploit can exit with non-zero status even with valid (but empty) results.
        if "No Results" in e.stderr or "No Results" in e.stdout:
             ui.print_info(f"No exploits found in Exploit-DB for '{query}'.")
             return {"status": "success", "results": []}
        ui.print_error(f"searchsploit command failed: {e.stderr}")
        return {"status": "error", "message": e.stderr}
    except json.JSONDecodeError as e:
        ui.print_error(f"Failed to parse JSON from searchsploit: {e}")
        return {"status": "error", "message": "Failed to parse searchsploit output."}
