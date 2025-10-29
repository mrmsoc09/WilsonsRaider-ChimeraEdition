from core.managers.autonomous_validation_manager import AutonomousValidationManager
from crewai import Crew
from core.ai_agents.sast_agent import SASTAgent
from core.ai_agents.red_team_agent import RedTeamAgent
from core.ai_agents.blue_team_agent import BlueTeamAgent
from core.ai_agents.purple_team_agent import PurpleTeamAgent
from core.ai_agents.osint_agent import OSINTAgent
from core.ai_agents.bug_bounty_agent import BugBountyHunterAgent
from orchestrator.team_manager import TeamManager
from core import ui
import json

class Orchestrator(Crew):
    def __init__(self):
        super().__init__()
        # Initialize all agents
        self.sast_agent = SASTAgent()
        self.red_team = RedTeamAgent()
        self.blue_team = BlueTeamAgent()
        self.purple_team = PurpleTeamAgent()
        self.osint_agent = OSINTAgent()
        self.bug_bounty_agent = None  # Initialized per-hunt

        # Register agents with the crew
        self.register_agent(self.sast_agent)
        self.register_agent(self.red_team)
        self.register_agent(self.blue_team)
        self.register_agent(self.purple_team)
        self.register_agent(self.osint_agent)

        # Set up teams
        self.team_manager = TeamManager()
        self.team_manager.create_team('red', [self.red_team])
        self.team_manager.create_team('blue', [self.blue_team])
        self.team_manager.create_team('purple', [self.purple_team])
        self.team_manager.create_team('osint', [self.osint_agent])

    def run_team(self, team_name, *args, **kwargs):
        return self.team_manager.run_team(team_name, *args, **kwargs)

    def run_hunt(self, program_name: str, target: str):
        """
        Initializes and runs a full bug bounty hunt using the BugBountyHunterAgent.
        """
        ui.print_header(f"Orchestrator starting a new hunt for '{target}'")
        try:
            # Each hunt gets a fresh, dedicated agent instance
            self.bug_bounty_agent = BugBountyHunterAgent(program_name=program_name, target=target)
            self.register_agent(self.bug_bounty_agent)
            
            result = self.bug_bounty_agent.run_full_hunt()
            ui.print_success("Orchestrator has completed the hunt.")
            return result
        except Exception as e:
            ui.print_error(f"The hunt orchestrated by the Orchestrator failed: {e}")
            return {"status": "error", "details": str(e)}

if __name__ == "__main__":
    orchestrator = Orchestrator()
    print("--- Running Team Simulations ---")
    print(orchestrator.run_team('red', 'target.example.com'))
    print(orchestrator.run_team('blue', 'target.example.com'))
    print(orchestrator.run_team('purple', {'attack': 'simulated'}, {'defense': 'simulated'}))
    print(orchestrator.run_team('osint', 'example.com'))

    # Example of running a full, orchestrated hunt
    print("\n--- Running a Full Bug Bounty Hunt ---")
    hunt_results = orchestrator.run_hunt(program_name="TestHunt-Nmap", target="scanme.nmap.org")
    print("\n--- Hunt Results ---")
    print(json.dumps(hunt_results, indent=2))
