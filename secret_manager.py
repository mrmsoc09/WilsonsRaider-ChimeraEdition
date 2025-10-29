import os
import logging
from typing import Any, Dict, Optional, Union
import hvac

class SecretManager:
    def __init__(self, vault_addr: Optional[str] = None, token: Optional[str] = None, approle_id: Optional[str] = None, approle_secret: Optional[str] = None):
        self.vault_addr = vault_addr or os.getenv('VAULT_ADDR', 'http://vault:8200')
        self.token = token or os.getenv('VAULT_TOKEN')
        self.approle_id = approle_id or os.getenv('VAULT_APPROLE_ID')
        self.approle_secret = approle_secret or os.getenv('VAULT_APPROLE_SECRET')
        self.client = hvac.Client(url=self.vault_addr)
        self.authenticated = False
        self.authenticate()

    def authenticate(self):
        try:
            if self.token:
                self.client.token = self.token
                self.authenticated = self.client.is_authenticated()
            elif self.approle_id and self.approle_secret:
                resp = self.client.auth_approle(self.approle_id, self.approle_secret)
                self.client.token = resp['auth']['client_token']
                self.authenticated = self.client.is_authenticated()
            else:
                logging.error('No Vault credentials provided.')
                self.authenticated = False
            if not self.authenticated:
                logging.error('Vault authentication failed.')
        except Exception as e:
            logging.error(f'Vault authentication error: {e}')
            self.authenticated = False

    def get_secret(self, path: str, key: Optional[str] = None) -> Union[str, Dict[str, Any], None]:
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(path=path)
            data = secret['data']['data']
            if key:
                return data.get(key)
            return data
        except Exception as e:
            logging.error(f'Error retrieving secret from {path}: {e}')
            return None

    def set_secret(self, path: str, key: str, value: str) -> bool:
        try:
            self.client.secrets.kv.v2.create_or_update_secret(path=path, secret={key: value})
            return True
        except Exception as e:
            logging.error(f'Error writing secret to {path}: {e}')
            return False
