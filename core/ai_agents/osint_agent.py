from crewai import Agent
from core.managers.ai_manager import AIManager
from core.tools.gitleaks_wrapper import run_gitleaks
from core.tools.darkweb_scraper_wrapper import run_darkweb_scraper
from core import ui

class OSINTAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Open Source Intelligence Specialist',
            goal='Gather intelligence from public sources to identify potential targets, technologies, and personnel, including sensitive data leaks.',
            backstory='You are an OSINT expert, codenamed "Sentinel" from the ALPHA-OMEGA project. You are a master of digital reconnaissance, capable of uncovering hidden information from across the internet, including exposed credentials and sensitive data.',
            verbose=True,
            allow_delegation=False
        )
        self.ai_manager = AIManager()

    def run_github_leak_scan(self, target_repo_url: str) -> dict:
        """
        Scans a GitHub repository URL for exposed secrets using Gitleaks.
        """
        ui.print_info(f"OSINTAgent starting Gitleaks scan on GitHub repo: {target_repo_url}...")
        results = run_gitleaks(target_repo_url)

        if not results or ('error' in results[0]):
            error_message = results[0]['error'] if results and ('error' in results[0]) else "Unknown error"
            ui.print_error(f"OSINTAgent Gitleaks scan failed: {error_message}")
            return {"status": "failed", "error": error_message}
        
        ui.print_success(f"OSINTAgent Gitleaks scan completed for {target_repo_url}. Analyzing results...")
        analysis_prompt = f"Analyze the following Gitleaks output for {target_repo_url} and summarize any critical findings (e.g., exposed API keys, passwords).:\n\n{results}"
        ai_analysis = self.ai_manager._call_llm(analysis_prompt, system_prompt="You are an expert in analyzing security tool output for critical leaks.", task_type='analysis')
        
        return {"status": "success", "raw_results": results, "ai_analysis": ai_analysis}

    def run_osint(self, target):
        """
        Executes a comprehensive OSINT gathering process for the given target.
        """
        ui.print_subheader(f"OSINTAgent: Initiating comprehensive OSINT for {target}")
        all_osint_results = {}

        # 1. Dynamic GitHub Repo Discovery and Leak Scan
        github_repo_prompt = f"You are an OSINT expert. For the target '{target}', identify 1-3 most relevant GitHub repository URLs that might contain sensitive information or code related to this target. Provide ONLY the URLs, one per line."
        relevant_repos_str = self.ai_manager._call_llm(github_repo_prompt, system_prompt="You are an expert OSINT analyst.", task_type='analysis')
        
        if relevant_repos_str:
            relevant_repos = [repo.strip() for repo in relevant_repos_str.split('\n') if repo.strip()]
            for repo_url in relevant_repos:
                github_leak_results = self.run_github_leak_scan(repo_url)
                all_osint_results.setdefault('github_leaks', []).append(github_leak_results)
        else:
            ui.print_warning(f"AI could not identify relevant GitHub repos for {target}.")

        # 2. Dark Web Scraping (Placeholder)
        darkweb_results = run_darkweb_scraper(target)
        all_osint_results['darkweb_scraping'] = darkweb_results

        # 3. General AI-Assisted OSINT Search
        general_osint_prompt = f"You are an OSINT expert. For the target '{target}', perform a general OSINT search to find any publicly available information that could be useful for a bug bounty hunter (e.g., employee names, technologies used, old press releases, forum mentions). Summarize your findings concisely."
        general_osint_summary = self.ai_manager._call_llm(general_osint_prompt, system_prompt="You are an expert OSINT analyst.", task_type='analysis')
        if general_osint_summary:
            all_osint_results['general_osint_summary'] = general_osint_summary

        if not all_osint_results:
            return f"OSINT gathering for {target} found no specific results yet."
        
        summary_prompt = f"Summarize the following OSINT findings for {target} and highlight any critical intelligence or potential attack vectors:\n\n{all_osint_results}"
        overall_summary = self.ai_manager._call_llm(summary_prompt, system_prompt="You are an expert OSINT analyst.", task_type='analysis')

        return {"status": "complete", "summary": overall_summary, "details": all_osint_results}
