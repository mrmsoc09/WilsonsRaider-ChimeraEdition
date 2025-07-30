#!/usr/bin/env python3
import os
import getpass
import hvac
import dotenv

def prompt_env(var, prompt_text, secret=False):
    val = os.getenv(var)
    if not val:
        if secret:
            val = getpass.getpass(f"{prompt_text}: ")
        else:
            val = input(f"{prompt_text}: ")
    return val

def verify_api_key(api_key):
    # Placeholder for real verification logic
    # For example, make a test request to the API
    return True

def main():
    dotenv.load_dotenv(dotenv.find_dotenv())
    print("=== Wilsons-Raiders Initial Setup ===")
    vault_addr = prompt_env('VAULT_ADDR', 'Vault address (e.g., http://127.0.0.1:8200)')
    vault_token = prompt_env('VAULT_ROOT_TOKEN', 'Vault root token', secret=True)
    client = hvac.Client(url=vault_addr, token=vault_token)
    if not client.is_authenticated():
        print("[!] Vault authentication failed. Exiting.")
        return
    print("[+] Authenticated to Vault.")
    api_keys = {}
    while True:
        key_name = input("Enter API key name (or blank to finish): ").strip()
        if not key_name:
            break
        key_value = getpass.getpass(f"Enter value for {key_name}: ")
        verify = input(f"Verify {key_name}? (y/N): ").strip().lower()
        if verify == 'y':
            if not verify_api_key(key_value):
                print(f"[!] Verification failed for {key_name}. Try again.")
                continue
        api_keys[key_name] = key_value
    if not api_keys:
        print("No API keys entered. Exiting.")
        return
    # Store in Vault
    secret_path = 'secret/data/wilsons-raiders/creds'
    print(f"Storing API keys in Vault at {secret_path} ...")
    client.secrets.kv.v2.create_or_update_secret(
        path='wilsons-raiders/creds',
        secret=api_keys
    )
    print("[+] API keys stored securely in Vault.")

if __name__ == '__main__':
    main()
