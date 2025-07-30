from .. import ui, branding
from ..state_manager import StateManager, Vulnerability

class ReportingManager:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        ui.print_info("ReportingManager initialized.")

    def generate_report(self, assessment_id, kill_chain_narrative):
        ui.print_header(branding.get_name('reporting'))
        
        vulnerabilities = self.state_manager.get_vulnerabilities_for_assessment(assessment_id)
        
        report = f"""# Security Assessment Report for Assessment ID: {assessment_id}

## Dynamic Kill Chain Analysis

{kill_chain_narrative}

## Detailed Findings

"""

        if not vulnerabilities:
            report += "No vulnerabilities were found during this assessment.\n"
        else:
            for vuln in vulnerabilities:
                report += f"""### {vuln.name} ({vuln.severity})\n
- **Tool:** {vuln.tool}
- **Asset:** {vuln.asset.name if vuln.asset else 'N/A'}
- **Description:** {vuln.description}\n\n"""
        
        ui.print_info("--- Generating Final Report ---")
        print(report)
        ui.print_success("Report generation complete.")

