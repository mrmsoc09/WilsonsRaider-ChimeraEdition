from crewai import Agent, Task
from secret_manager import SecretManager

class SASTAgent(Agent):
    def __init__(self, cost_tier='balanced'):
        super().__init__(name='SASTAgent')
        self.secrets = SecretManager()
        self.cost_tier = cost_tier
        self.llm_api_key = self.secrets.get_secret('wilsons-raiders/creds', 'OPENAI_API_KEY')
        self.model = self._select_model()

    def _select_model(self):
        if self.cost_tier == 'economic':
            return 'gpt-3.5-turbo'
        elif self.cost_tier == 'high-performance':
            return 'gpt-4o'
        return 'gpt-4'

    def run(self, target_path):
        # Example: Run Bandit SAST scan
        import subprocess, json
        cmd = ['bandit', '-r', target_path, '-f', 'json']
        proc = subprocess.run(cmd, capture_output=True, text=True)
        try:
            results = json.loads(proc.stdout)
        except Exception:
            results = {'error': proc.stderr}
        return results
