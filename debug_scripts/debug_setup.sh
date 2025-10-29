#!/bin/bash

echo "=== Wilsons-Raiders Debug Setup Guide ==="

# --- 1. Install Ollama and Pull Model ---
echo "\n--- 1. Ollama Setup ---"
if command -v ollama &> /dev/null
then
    echo "Ollama is already installed."
else
    echo "Installing Ollama... (Follow instructions on https://ollama.com/download)"
    # Example for Linux:
    # curl -fsSL https://ollama.com/install.sh | sh
    read -p "Press Enter once Ollama is installed." 
fi

OLLAMA_MODEL="phi3:mini"
if ollama list | grep -q "$OLLAMA_MODEL"; then
    echo "Ollama model '$OLLAMA_MODEL' is already pulled."
else
    echo "Pulling Ollama model '$OLLAMA_MODEL'..."
    ollama pull "$OLLAMA_MODEL"
fi

echo "Starting Ollama server in background..."
ollama serve > /dev/null &
OLLAMA_PID=$!
echo "Ollama server started with PID $OLLAMA_PID. (You may need to kill this process later)"

# --- 2. Set DB_ENCRYPTION_KEY ---
echo "\n--- 2. Database Encryption Key ---"
if [ -z "$DB_ENCRYPTION_KEY" ]; then
    read -p "Enter a strong secret key for DB_ENCRYPTION_KEY: " DB_KEY
    export DB_ENCRYPTION_KEY="$DB_KEY"
    echo "DB_ENCRYPTION_KEY set for this session. Add 'export DB_ENCRYPTION_KEY=\"$DB_KEY\"' to your .bashrc/.zshrc for persistence."
else
    echo "DB_ENCRYPTION_KEY is already set."
fi

# --- 3. Run setup.py for Vault Configuration ---
echo "\n--- 3. Vault Configuration ---"
read -p "Press Enter to run setup.py to configure Vault with API keys. Ensure Vault is running." 
python3 setup.py

# --- 4. Install External Tools ---
echo "\n--- 4. External Tools Installation ---"
echo "Please ensure the following tools are installed and in your PATH:"
echo "- nuclei (https://nuclei.sh/)"
echo "- subfinder (https://github.com/projectdiscovery/subfinder)"
echo "- bandit (https://bandit.readthedocs.io/)"
echo "- gitleaks (https://github.com/gitleaks/gitleaks)"
echo "- searchsploit (part of Exploit-DB, usually via 'apt install exploitdb')"
echo "- objection (https://github.com/sensepost/objection)"
echo "- ZAP (OWASP ZAP, https://www.zaproxy.org/)"
read -p "Press Enter once you have verified/installed these tools." 

# --- 5. Android Device Setup (Optional) ---
echo "\n--- 5. Android Device Setup (Optional) ---"
echo "If you plan to use Android devices, remember to:"
echo "- Install Termux and Python on your devices."
echo "- Install OpenSSH in Termux (\`pkg install openssh\`)."
echo "- Start SSHD in Termux (\`sshd\`)."
echo "- Copy your SSH public key to ~/.ssh/authorized_keys on each device."
echo "- Update config/devices.yaml with your device IPs and SSH key name."
read -p "Press Enter to complete setup guide." 

echo "\n=== Setup Guide Complete. You can now run debugging scripts. ==="
