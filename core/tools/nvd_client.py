import httpx
from core import ui
from secret_manager import SecretManager
from core.config_manager import ConfigManager

class NVDClient:
    """A client for interacting with the NVD CVE API 2.0."""

    def __init__(self):
        self.secrets = SecretManager()
        self.config = ConfigManager()
        self.BASE_URL = self.config.get('api_endpoints.nvd')
        self.api_key = self.secrets.get_secret('wilsons-raiders/creds', 'NVD_API_KEY')
        self.headers = {'apiKey': self.api_key} if self.api_key else {}
        if not self.api_key:
            ui.print_warning("NVD_API_KEY not found in Vault. Requests will be severely rate-limited.")

    def get_cve_details(self, cve_id: str) -> dict | None:
        """
        Fetches the details for a single CVE ID from the NVD API.

        Args:
            cve_id (str): The CVE identifier (e.g., 'CVE-2021-44228').

        Returns:
            dict | None: A dictionary containing the CVE details, or None on failure.
        """
        ui.print_info(f"Querying NVD for details on: {cve_id}...")
        try:
            with httpx.Client(headers=self.headers, timeout=30.0) as client:
                response = client.get(f"{self.BASE_URL}?cveId={cve_id}")
                response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
                
                data = response.json()
                if data.get('totalResults', 0) > 0:
                    ui.print_success(f"Successfully fetched details for {cve_id}.")
                    return data['vulnerabilities'][0]['cve']
                else:
                    ui.print_warning(f"No results found in NVD for {cve_id}.")
                    return None

        except httpx.HTTPStatusError as e:
            ui.print_error(f"NVD API request failed for {cve_id}: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            ui.print_error(f"An unexpected error occurred while querying NVD: {e}")
            return None
