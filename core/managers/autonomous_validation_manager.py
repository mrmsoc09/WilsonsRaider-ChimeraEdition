
import subprocess
import os
import json
from core.ui import Z_UI

# Assuming ui is initialized somewhere globally or passed in
ui = Z_UI()

class AutonomousValidationManager:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.pentest_agent_path = os.path.join('core', 'validation_tools', 'PentestAgent')
        self.cai_path = os.path.join('core', 'validation_tools', 'cai')

    def run_validation(self, vulnerability_id, target_info):
        """
        Orchestrates the execution of autonomous validation tools.

        :param vulnerability_id: The ID of the vulnerability to validate.
        :param target_info: A dictionary containing target details like URL, IP, etc.
        """
        ui.print_info(f"Starting autonomous validation for vulnerability ID: {vulnerability_id}")

        # For now, we will focus on PentestAgent
        # Future logic can determine which tool to use based on vulnerability type

        success, evidence = self._run_pentest_agent(target_info)

        if success:
            ui.print_success(f"PentestAgent validation successful for {target_info.get('url')}")
            self.state_manager.update_vulnerability_validation_status(
                vulnerability_id, 'VALIDATED', json.dumps(evidence)
            )
        else:
            ui.print_warning(f"PentestAgent validation failed or could not confirm exploitability.")
            self.state_manager.update_vulnerability_validation_status(
                vulnerability_id, 'VALIDATION_FAILED', json.dumps(evidence)
            )

        # Placeholder for CAI integration
        # self._run_cai(target_info)

        return success

    def _run_pentest_agent(self, target_info):
        """
        Executes the PentestAgent tool in a subprocess.
        """
        target_url = target_info.get('url')
        if not target_url:
            return False, {"error": "Target URL not provided for PentestAgent."}

        # This command is a placeholder and will need to be adapted to PentestAgent's actual CLI
        # For example: python main.py --url <target_url> --scan
        command = ["python3", "main.py", "--url", target_url, "--non-interactive", "--output-json"]

        try:
            ui.print_info(f"Executing PentestAgent: {' '.join(command)}")

            # Execute from within the tool's directory
            result = subprocess.run(
                command,
                cwd=self.pentest_agent_path,
                capture_output=True,
                text=True,
                timeout=600  # 10-minute timeout
            )

            if result.returncode == 0:
                try:
                    output_json = json.loads(result.stdout)
                    return True, output_json
                except json.JSONDecodeError:
                    return True, {"raw_output": result.stdout}
            else:
                return False, {"error": result.stderr}

        except FileNotFoundError:
            return False, {"error": f"PentestAgent main.py not found at {self.pentest_agent_path}"}
        except subprocess.TimeoutExpired:
            return False, {"error": "PentestAgent execution timed out."}
        except Exception as e:
            return False, {"error": str(e)}

    def _run_cai(self, target_info):
        """
        Placeholder for running the CAI tool.
        """
        ui.print_info("CAI validation is not yet implemented.")
        return False, {"status": "not_implemented"}

