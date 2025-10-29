from crewai import Agent
from core.managers.state_manager import StateManager
from core.managers.recon_manager import ReconManager
from core.managers.scanning_manager import ScanningManager
from core.managers.ai_manager import AIManager
from core.managers.exploit_runner import ExploitRunner
from core.forge_manager import ForgeManager
from core.kill_chain_weaver import KillChainWeaver
from core.managers.reporting_manager import ReportingManager
from core import ui

class BugBountyHunterAgent(Agent):
    """
    An autonomous agent that orchestrates the entire bug bounty hunting process.
    """
    def __init__(self, program_name: str, target: str):
        super().__init__(
            role='Lead Bug Bounty Hunter',
            goal=f'Autonomously find, validate, chain, and report vulnerabilities for {target}'.',
            backstory='You are an elite AI security researcher, equipped with a suite of advanced tools to automate the entire bug bounty hunting process from reconnaissance to kill chain analysis and reporting.',
            verbose=True,
            allow_delegation=False
        )
        self.program_name = program_name
        self.target = target

        # Initialize all the necessary managers for the hunt
        ui.print_info("Initializing managers for the Bug Bounty Hunter Agent...")
        try:
            self.state_manager = StateManager()
            self.ai_manager = AIManager()
            self.forge_manager = ForgeManager(ai_manager=self.ai_manager)
            self.ai_manager.forge_manager = self.forge_manager # Link back
            
            # The ui_manager dependency in ExploitRunner and KillChainWeaver seems to expect a class,
            # but the project uses the ui module directly. We pass the module itself.
            self.exploit_runner = ExploitRunner(ui_manager=ui)
            self.kill_chain_weaver = KillChainWeaver(
                ai_manager=self.ai_manager,
                forge_manager=self.forge_manager,
                exploit_runner=self.exploit_runner,
                ui_manager=ui
            )
            self.recon_manager = ReconManager(state_manager=self.state_manager)
            self.scanning_manager = ScanningManager(state_manager=self.state_manager)
            self.reporting_manager = ReportingManager(state_manager=self.state_manager)
            ui.print_success("All managers initialized successfully.")
        except Exception as e:
            ui.print_error(f"Failed to initialize managers: {e}")
            raise

    def run_full_hunt(self):
        """
        Executes the entire bug bounty hunting workflow from start to finish.
        """
        ui.print_header(f"--- Starting Full Hunt via Agent for Program: {self.program_name} ---")
        ui.print_info(f"[>] Target: {self.target}")

        # Step 1: Create a new assessment in the database
        try:
            assessment_id = self.state_manager.create_assessment(program_name=self.program_name, target=self.target)
            ui.print_success(f"Assessment created with ID: {assessment_id}")
        except Exception as e:
            ui.print_error(f"Failed to create assessment. Aborting hunt. Error: {e}")
            return {"status": "failed", "error": "Could not create assessment."}

        # Step 2: Perform reconnaissance
        recon_data = self.recon_manager.run(assessment_id, self.target)
        if not recon_data.get('subdomains'):
            ui.print_error("Reconnaissance failed to find any subdomains. Aborting hunt.")
            return {"status": "failed", "error": "Reconnaissance found no subdomains."}
        ui.print_success(f"Reconnaissance complete. Found {len(recon_data['subdomains'])} subdomains.")

        # Step 3: Use AI to prioritize assets and select scanner templates
        prioritized_assets, prioritized_templates = self.ai_manager.prioritize_assets(recon_data.get('subdomains', []))
        if not prioritized_assets:
            ui.print_warning("AI prioritization did not return any assets. Defaulting to all found subdomains.")
            prioritized_assets = recon_data.get('subdomains', [])

        # Step 4: Run active scans on the prioritized assets
        self.scanning_manager.run(assessment_id, prioritized_assets, prioritized_templates)

        # Step 5: Analyze findings, validate, and attempt to build kill chains
        vulnerabilities = self.state_manager.get_vulnerabilities_for_assessment(assessment_id)
        if not vulnerabilities:
            ui.print_info("No potential vulnerabilities were found after scanning. Hunt concluded.")
            return {"status": "complete", "message": "No vulnerabilities found."}

        ui.print_header("--- Validating Findings and Weaving Kill Chains ---")
        final_kill_chains = []
        for vuln in vulnerabilities:
            ui.print_vulnerability(vuln)
            # Use the KillChainWeaver to attempt to build an attack chain from this finding
            chain = self.kill_chain_weaver.attempt_to_chain(
                initial_finding={'name': vuln.name, 'description': vuln.description},
                target=vuln.asset.name if vuln.asset else self.target
            )
            if len(chain) > 1:
                final_kill_chains.append(chain)

        # Step 6: Generate a final report
        narrative = "The following potential attack chains were identified:\n\n"
        if final_kill_chains:
            for i, chain in enumerate(final_kill_chains):
                narrative += f"**Chain {i+1}:**\n"
                for step in chain:
                    narrative += f"- {step.get('name', 'Unknown Step')}\n"
                narrative += "\n"
        else:
            narrative = "No complex attack chains were constructed. The report contains standalone findings."

        self.reporting_manager.generate_report(assessment_id, narrative)

        ui.print_header(f"--- Hunt Finished for {self.program_name} ---")
        vuln_count = len(vulnerabilities)
        ui.print_success(f"Found a total of {vuln_count} potential vulnerabilities.")
        
        return {"status": "complete", "vulnerabilities_found": vuln_count, "chains_found": len(final_kill_chains)}
