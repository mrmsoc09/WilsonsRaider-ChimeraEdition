from .ui import UIManager
from .ai_manager import AIManager
from .managers.exploit_runner import ExploitRunner
from .forge_manager import ForgeManager

class KillChainWeaver:
    """An AI agent that attempts to chain exploits to demonstrate higher impact."""

    def __init__(self, ai_manager: AIManager, forge_manager: ForgeManager, exploit_runner: ExploitRunner, ui_manager: UIManager):
        self.ai = ai_manager
        self.forge = forge_manager
        self.runner = exploit_runner
        self.ui = ui_manager

    def attempt_to_chain(self, initial_finding: dict, target: str) -> list:
        """
        Takes an initial, confirmed vulnerability and tries to build an attack chain.

        Args:
            initial_finding (dict): The first confirmed vulnerability.
            target (str): The primary target URL or domain.

        Returns:
            list: A list of dictionaries, where each dict is a step in the kill chain.
        """
        self.ui.run_subheading("Initiating Kill Chain Weaver")
        self.ui.print(f"  -> Initial finding: [yellow]{initial_finding.get('name', 'Unknown Vulnerability')}[/yellow]")
        kill_chain = [initial_finding]

        # --- AI HYPOTHESIS STEP ---
        # TODO: Implement AI call to brainstorm next steps based on the initial finding.
        self.ui.print("  -> Weaver: Hypothesizing next steps... (Placeholder)")
        hypothesis = "Use the initial finding to perform internal network reconnaissance."
        
        # --- FORGE & EXECUTE STEP ---
        # The Weaver uses the Forge to create a tool for its hypothesis.
        self.ui.print(f"  -> Weaver: Forging a new tool for hypothesis: '{hypothesis}'")
        recon_data_for_forge = {
            'target': target,
            'hypothesis': hypothesis,
            # Include details from the initial finding to give the AI context
            'context': f"Initial exploit confirmed: {initial_finding}"
        }
        # new_poc_path = self.forge.generate_nuclei_template(
        #     template_name="weaver_chain_attempt_1",
        #     recon_data=recon_data_for_forge
        # )
        
        # if new_poc_path:
        #     # The Weaver uses the ExploitRunner to execute its custom-forged tool.
        #     success, evidence = self.runner.run_single_exploit(target, new_poc_path)
        #     if success:
        #         self.ui.print("[bold green]  -> WEAVER SUCCESS: Chained exploit confirmed![/bold green]")
        #         next_step = {'name': hypothesis, 'evidence': evidence}
        #         kill_chain.append(next_step)
        
        if len(kill_chain) > 1:
            self.ui.print(f"[bold green]Kill Chain successfully constructed with {len(kill_chain)} steps.[/bold green]")
        else:
            self.ui.print("[yellow]Weaver could not construct a chain. Reporting initial finding only.[/yellow]")

        return kill_chain

