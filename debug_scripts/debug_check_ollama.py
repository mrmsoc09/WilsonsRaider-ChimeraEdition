import httpx
import sys
import os

# Add project root to sys.path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config_manager import ConfigManager
from core import ui

def check_ollama_config():
    config = ConfigManager()
    ollama_host = config.get('ai_models.ollama_host')
    default_model = config.get('ai_models.default_fallback_model')

    print("=== Checking Ollama Server and Model ===")

    # 1. Check Ollama server availability
    try:
        response = httpx.get(f"{ollama_host}/api/tags", timeout=5)
        response.raise_for_status()
        print(f"[SUCCESS] Ollama server is running at {ollama_host}.")
    except httpx.RequestError as e:
        print(f"[ERROR] Ollama server is not reachable at {ollama_host}: {e}")
        print("Please ensure Ollama is installed and running (`ollama serve`).")
        return False

    # 2. Check if default fallback model is available
    # Extract model name from 'ollama/model:tag' format
    model_name_only = default_model.split('/')[-1]
    try:
        models_data = response.json()
        available_models = [m['name'] for m in models_data.get('models', [])]
        if model_name_only in available_models:
            print(f"[SUCCESS] Default fallback model '{model_name_only}' is available.")
        else:
            print(f"[ERROR] Default fallback model '{model_name_only}' not found locally.")
            print(f"Please pull it using: `ollama pull {model_name_only}`")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to check Ollama models: {e}")
        return False

    print("\n=== Ollama Check Complete ===")
    return True

if __name__ == "__main__":
    check_ollama_config()
