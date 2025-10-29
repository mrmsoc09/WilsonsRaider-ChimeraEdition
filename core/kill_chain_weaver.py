from .ui import UIManager
from .ai_manager import AIManager
from .managers.exploit_runner import ExploitRunner
from .forge_manager import ForgeManager
from core.managers.curated_exploit_manager import CuratedExploitManager

class KillChainWeaver:
    """An AI agent that attempts to chain exploits to demonstrate higher impact."""

    def __init__(self, ai_manager: AIManager, forge_manager: ForgeManager, exploit_runner: ExploitRunner, ui_manager: UIManager):
        self.ai = ai_manager
        self.forge = forge_manager
        self.runner = exploit_runner
        self.ui = ui_manager
        self.curated_exploit_manager = CuratedExploitManager()

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
        self.ui.print("  -> Weaver: Hypothesizing next steps based on initial finding and available intelligence...")
        
        context_for_ai = f"Initial finding: {initial_finding}\n"
        
        relevant_curated_exploits = self.curated_exploit_manager.get_curated_exploits()
        if relevant_curated_exploits:
            context_for_ai += f"Available high-impact exploits: {relevant_curated_exploits}\n"

        hypothesis_prompt = f"""
        You are a Kill Chain Weaver. Given an initial vulnerability finding and available intelligence, propose the most impactful next step in an attack chain.
        Focus on high-risk, high-reward actions. Consider if any known, curated exploits could be directly applied or adapted.

        Context:
        {context_for_ai}
        Target: {target}

        Propose a single, concise next step (e.g., "Use CVE-XXXX-YYYY to gain RCE", "Perform internal network reconnaissance", "Attempt privilege escalation using known Linux kernel exploit").
        """
        hypothesis = self.ai.ai_manager._call_llm(hypothesis_prompt, system_prompt="You are an expert in attack chain construction.", task_type='analysis')
        if not hypothesis:
            hypothesis = "Perform internal network reconnaissance." # Fallback

        self.ui.print(f"  -> Weaver's Hypothesis: '{hypothesis}'")
        
        # --- FORGE & EXECUTE STEP ---
        self.ui.print(f"  -> Weaver: Attempting to execute hypothesis: '{hypothesis}'")
        
        executed_curated_exploit = False
        for curated_exploit in relevant_curated_exploits:
            cve_id = curated_exploit.get('cve_id', '')
            if cve_id and cve_id in hypothesis:
                self.ui.print(f"  -> Weaver: Hypothesis suggests using curated exploit {cve_id}. Executing directly...")
                success, evidence = self.runner._run_curated_exploit(target, curated_exploit)
                if success:
                    self.ui.print("[bold green]  -> WEAVER SUCCESS: Chained curated exploit confirmed![/bold green]")
                    next_step = {'name': hypothesis, 'evidence': evidence, 'exploit_details': curated_exploit}
                    kill_chain.append(next_step)
                    executed_curated_exploit = True
                    break

        if not executed_curated_exploit:
            recon_data_for_forge = {
                'target': target,
                'hypothesis': hypothesis,
                'context': f"Initial exploit confirmed: {initial_finding}"
            }
            if self.forge:
                new_poc_path = self.forge.generate_nuclei_template(
                    template_name="weaver_chain_attempt_1",
                    recon_data=recon_data_for_forge
                )
                
                if new_poc_path:
                    success, evidence = self.runner._run_single_exploit(target, new_poc_path)
                    if success:
                        self.ui.print("[bold green]  -> WEAVER SUCCESS: Chained forged exploit confirmed![/bold green]")
                        next_step = {'name': hypothesis, 'evidence': evidence, 'script': str(new_poc_path)}
                        kill_chain.append(next_step)
        
        if len(kill_chain) > 1:
            self.ui.print(f"[bold green]Kill Chain successfully constructed with {len(kill_chain)} steps.[/bold green]")
        else:
            self.ui.print("[yellow]Weaver could not construct a chain. Reporting initial finding only.[/yellow]")

        return kill_chain

