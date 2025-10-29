import yaml
import asyncio
from core import ui
from secret_manager import SecretManager
from core.platform_managers.hackerone_manager import HackerOneManager
from core.platform_managers.bugcrowd_manager import BugcrowdManager
from core.platform_managers.intigriti_manager import IntigritiManager
from core.config_manager import ConfigManager

class BountyProgramManager:
    """Consolidates bug bounty program information from static lists and live platforms."""

    def __init__(self):
        self.secrets = SecretManager()
        self.config = ConfigManager()
        self.programs_config_path = self.config.get('paths.programs_config')
        self.static_programs = self._load_static_programs()
        
        h1_api_token = self.secrets.get_secret('wilsons-raiders/creds', 'HACKERONE_API_TOKEN')
        bc_api_key = self.secrets.get_secret('wilsons-raiders/creds', 'BUGCROWD_API_KEY')
        it_api_key = self.secrets.get_secret('wilsons-raiders/creds', 'INTIGRITI_API_KEY')
        
        h1_user = self.secrets.get_secret('wilsons-raiders/creds', 'HACKERONE_USER') or "api_user_placeholder"

        self.hackerone_manager = HackerOneManager(api_user=h1_user, api_key=h1_api_token) if h1_api_token else None
        self.bugcrowd_manager = BugcrowdManager(api_key=bc_api_key) if bc_api_key else None
        self.intigriti_manager = IntigritiManager(api_key=it_api_key) if it_api_key else None
        ui.print_info("BountyProgramManager initialized.")

    def _load_static_programs(self):
        """Loads the curated list of top-tier programs from the YAML config."""
        try:
            with open(self.programs_config_path, 'r') as f:
                programs = yaml.safe_load(f).get('top_tier_programs', [])
                ui.print_info(f"Loaded {len(programs)} static programs from {self.programs_config_path}.")
                return programs
        except FileNotFoundError:
            ui.print_warning(f"{self.programs_config_path} not found. No static programs loaded.")
            return []
        except Exception as e:
            ui.print_error(f"Error loading static programs: {e}")
            return []

    async def get_all_opportunities(self) -> list:
        """Gathers all opportunities from the static list and live platforms."""
        all_programs = self.static_programs.copy()
        
        tasks = []
        if self.hackerone_manager:
            tasks.append(self.hackerone_manager.get_programs())
        if self.bugcrowd_manager:
            tasks.append(self.bugcrowd_manager.get_programs())
        if self.intigriti_manager:
            tasks.append(self.intigriti_manager.get_programs())
        
        if tasks:
            live_results = await asyncio.gather(*tasks)
            for result_list in live_results:
                all_programs.extend(result_list)

        ui.print_success(f"Consolidated a total of {len(all_programs)} potential bounty programs.")
        return all_programs
