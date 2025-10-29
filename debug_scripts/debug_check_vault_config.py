import os
import sys
import hvac
import dotenv

# Add project root to sys.path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config_manager import ConfigManager
from secret_manager import SecretManager

def check_vault_config():
    dotenv.load_dotenv(dotenv.find_dotenv())
    config = ConfigManager()
    secrets = SecretManager()

    print("=== Checking Vault Configuration ===")

    # Check Vault connection
    try:
        if not secrets.client.is_authenticated():
            print("[ERROR] Vault is not authenticated. Please run setup.py.")
            return False
        print("[SUCCESS] Successfully authenticated to Vault.")
    except Exception as e:
        print(f"[ERROR] Could not connect to Vault: {e}. Please ensure VAULT_ADDR is correct and Vault is running.")
        return False

    # Check LLM API Keys
    print("\n--- LLM API Keys ---")
    llm_keys_path = 'wilsons-raiders/creds'
    try:
        llm_creds = secrets.get_secret(llm_keys_path)
        if not llm_creds:
            print(f"[WARNING] No LLM API keys found in Vault at {llm_keys_path}.")
            print("  Only local Ollama models will be available for AI tasks.")
        else:
            for key_name in config.get('ai_models.task_model_map').keys():
                if key_name != 'default' and key_name != 'ollama/' and key_name.upper() + '_API_KEY' in llm_creds:
                    print(f"[SUCCESS] {key_name.upper()}_API_KEY found.")
                elif key_name != 'default' and key_name != 'ollama/':
                    print(f"[WARNING] {key_name.upper()}_API_KEY not found. Tasks routed to this model may fail or fallback.")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve LLM API keys from Vault: {e}")
        return False

    # Check Security Tool API Keys
    print("\n--- Security Tool API Keys ---")
    tool_keys_to_check = [
        'NVD_API_KEY', 'HACKERONE_API_TOKEN', 'HACKERONE_USER',
        'BUGCROWD_API_KEY', 'INTIGRITI_API_KEY'
    ]
    try:
        tool_creds = secrets.get_secret(llm_keys_path) # Tool keys are also in creds path
        for key_name in tool_keys_to_check:
            if tool_creds and tool_creds.get(key_name):
                print(f"[SUCCESS] {key_name} found.")
            else:
                print(f"[WARNING] {key_name} not found. Related tool integrations may be limited.")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve Security Tool API keys from Vault: {e}")
        return False

    # Check SSH Keys for Android Devices
    print("\n--- Android SSH Keys ---")
    ssh_keys_path = 'wilsons-raiders/ssh_keys'
    try:
        ssh_creds = secrets.get_secret(ssh_keys_path)
        if not ssh_creds:
            print(f"[WARNING] No SSH keys found in Vault at {ssh_keys_path}. Android device integration will not work.")
        else:
            for key_name in ssh_creds.keys():
                print(f"[SUCCESS] SSH key '{key_name}' found for Android devices.")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve SSH keys from Vault: {e}")
        return False

    print("\n=== Vault Configuration Check Complete ===")
    return True

if __name__ == "__main__":
    check_vault_config()
