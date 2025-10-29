#!/usr/bin/env python3
import os
import getpass
import hvac
import dotenv
import sys

def prompt_input(var, prompt_text, secret=False, required=False):
    val = os.getenv(var)
    if not val:
        if secret:
            val = getpass.getpass(f"{prompt_text}: ")
        else:
            val = input(f"{prompt_text}: ")
    if required and not val:
        print(f"[!] {prompt_text} is required. Exiting.")
        sys.exit(1)
    return val

def verify_api_key(api_key):
    # Placeholder for real verification logic
    # For example, make a test request to the API
    return True

def main():
    dotenv.load_dotenv(dotenv.find_dotenv())
    print("=== Wilsons-Raiders Initial Setup ===")

    # 1. Vault Configuration
    vault_addr = prompt_input('VAULT_ADDR', 'Vault address (e.g., http://127.0.0.1:8200)', required=True)
    vault_token = prompt_input('VAULT_ROOT_TOKEN', 'Vault root token (for initial setup)', secret=True, required=True)
    
    client = hvac.Client(url=vault_addr, token=vault_token)
    if not client.is_authenticated():
        print("[!] Vault authentication failed. Please check VAULT_ADDR and VAULT_ROOT_TOKEN. Exiting.")
        sys.exit(1)
    print("[+] Authenticated to Vault.")

    # 2. Collect LLM API Keys
    print("\n--- Collecting LLM API Keys (Optional, but recommended for full functionality) ---")
    llm_api_keys = {
        'OPENAI_API_KEY': prompt_input('OPENAI_API_KEY', 'OpenAI API Key (e.g., sk-...)', secret=True),
        'ANTHROPIC_API_KEY': prompt_input('ANTHROPIC_API_KEY', 'Anthropic API Key (e.g., sk-ant-...)', secret=True),
        'GEMINI_API_KEY': prompt_input('GEMINI_API_KEY', 'Google Gemini API Key (e.g., AIza...)', secret=True),
        'DEEPSEEK_API_KEY': prompt_input('DEEPSEEK_API_KEY', 'DeepSeek API Key (e.g., sk-ds-...)', secret=True),
        'OPENROUTER_API_KEY': prompt_input('OPENROUTER_API_KEY', 'OpenRouter API Key (e.g., sk-or-...)', secret=True),
    }
    llm_api_keys = {k: v for k, v in llm_api_keys.items() if v} # Filter out empty keys

    # 3. Collect Security Tool API Keys
    print("\n--- Collecting Security Tool API Keys (Optional) ---")
    tool_api_keys = {
        'NVD_API_KEY': prompt_input('NVD_API_KEY', 'NVD API Key (for higher rate limits)', secret=True),
        'HACKERONE_API_TOKEN': prompt_input('HACKERONE_API_TOKEN', 'HackerOne API Token', secret=True),
        'HACKERONE_USER': prompt_input('HACKERONE_USER', 'HackerOne API User (for basic auth)'),
        'BUGCROWD_API_KEY': prompt_input('BUGCROWD_API_KEY', 'Bugcrowd API Key', secret=True),
        'INTIGRITI_API_KEY': prompt_input('INTIGRITI_API_KEY', 'Intigriti API Key', secret=True),
    }
    tool_api_keys = {k: v for k, v in tool_api_keys.items() if v} # Filter out empty keys

    # 4. Store API Keys in Vault
    api_keys_to_store = {**llm_api_keys, **tool_api_keys}
    if api_keys_to_store:
        secret_path_creds = 'wilsons-raiders/creds'
        print(f"\nStoring API keys in Vault at secret/data/{secret_path_creds} ...")
        client.secrets.kv.v2.create_or_update_secret(
            path=secret_path_creds,
            secret=api_keys_to_store
        )
        print("[+] API keys stored securely in Vault.")
    else:
        print("[!] No API keys provided. Skipping API key storage.")

    # 5. Collect SSH Keys for Android Devices
    print("\n--- Collecting SSH Private Keys for Android Devices (Optional) ---")
    print("If you plan to use Android devices for scanning, you need to provide the private SSH key.")
    print("Ensure you have generated an SSH key pair on your main system (e.g., `ssh-keygen -t ed25519`)")
    print("and copied the public key to your Termux devices (`ssh-copy-id -i ~/.ssh/id_ed25519.pub termux@<device-ip>`).")
    
    ssh_key_name = prompt_input('ANDROID_SSH_KEY_NAME', 'Enter a name for your Android SSH key (e.g., termux_ssh_key) or leave blank to skip:', required=False)
    if ssh_key_name:
        print(f"Please paste the ENTIRE PRIVATE SSH KEY content for '{ssh_key_name}' below.")
        print("Press Enter twice to finish input.")
        ssh_private_key_content = ""
        while True:
            try:
                line = input()
                if not line:
                    break
                ssh_private_key_content += line + "\n"
            except EOFError:
                break
        
        if ssh_private_key_content.strip():
            secret_path_ssh = 'wilsons-raiders/ssh_keys'
            print(f"\nStoring SSH private key '{ssh_key_name}' in Vault at secret/data/{secret_path_ssh} ...")
            client.secrets.kv.v2.create_or_update_secret(
                path=secret_path_ssh,
                secret={ssh_key_name: ssh_private_key_content.strip()}
            )
            print(f"[+] SSH private key '{ssh_key_name}' stored securely in Vault.")
        else:
            print("[!] No SSH private key content provided. Skipping SSH key storage.")
    else:
        print("[!] Skipping SSH key storage for Android devices.")

    print("\n=== Setup Complete ===")
    print("Remember to update config/devices.yaml with your Android device IP addresses and SSH key name.")

if __name__ == '__main__':
    main()
