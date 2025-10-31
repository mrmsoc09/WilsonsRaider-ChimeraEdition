from core.managers.autonomous_validation_manager import AutonomousValidationManager
from crewai import Crew
from ai_agents.sast_agent import SASTAgent
from ai_agents.red_team_agent import RedTeamAgent
from ai_agents.blue_team_agent import BlueTeamAgent
from ai_agents.purple_team_agent import PurpleTeamAgent
from orchestrator.team_manager import TeamManager

class Orchestrator(Crew):
    def __init__(self):
        super().__init__()
        self.sast_agent = SASTAgent()
        self.red_team = RedTeamAgent()
        self.blue_team = BlueTeamAgent()
        self.purple_team = PurpleTeamAgent()
        self.team_manager = TeamManager()
        # Register default teams
        self.team_manager.create_team('red', [self.red_team])
        self.team_manager.create_team('blue', [self.blue_team])
        self.team_manager.create_team('purple', [self.purple_team])
        self.register_agent(self.sast_agent)
        self.register_agent(self.red_team)
        self.register_agent(self.blue_team)
        self.register_agent(self.purple_team)

    def run_team(self, team_name, *args, **kwargs):
        return self.team_manager.run_team(team_name, *args, **kwargs)

if __name__ == "__main__":
    orchestrator = Orchestrator()
    print(orchestrator.run_team('red', 'target.example.com'))
    print(orchestrator.run_team('blue', 'target.example.com'))
    print(orchestrator.run_team('purple', {'attack': 'simulated'}, {'defense': 'simulated'}))
