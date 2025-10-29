class TeamManager:
    def __init__(self):
        self.teams = {}
    def create_team(self, name, agents):
        self.teams[name] = agents
    def get_team(self, name):
        return self.teams.get(name, [])
    def run_team(self, name, *args, **kwargs):
        results = {}
        for agent in self.teams.get(name, []):
            if hasattr(agent, 'run_attack'):
                results[agent.__class__.__name__] = agent.run_attack(*args, **kwargs)
            elif hasattr(agent, 'run_defense'):
                results[agent.__class__.__name__] = agent.run_defense(*args, **kwargs)
            elif hasattr(agent, 'coordinate'):
                results[agent.__class__.__name__] = agent.coordinate(*args, **kwargs)
            elif hasattr(agent, 'run_osint'):
                results[agent.__class__.__name__] = agent.run_osint(*args, **kwargs)
        return results
