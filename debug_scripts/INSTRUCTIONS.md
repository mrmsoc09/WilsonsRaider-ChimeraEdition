# Wilsons-Raiders Debugging Instructions

This guide will help you set up your environment and run initial debugging checks for the Wilsons-Raiders project.

## 1. Initial Setup

Run the setup script to configure your environment:

```bash
bash debug_scripts/debug_setup.sh
```

This script will guide you through:
- Installing/starting Ollama and pulling the `phi3:mini` model.
- Setting the `DB_ENCRYPTION_KEY` environment variable.
- Running `setup.py` to authenticate with Vault and store your API keys.
- Reminding you to install external tools (nuclei, subfinder, bandit, gitleaks, searchsploit, objection, ZAP).
- Reminding you about Android device setup (if applicable).

**Important:** Ensure your HashiCorp Vault server is running and accessible before running `setup.py`.

## 2. Verify Configuration

After running `debug_setup.sh`, use these scripts to verify your setup:

### 2.1. Check Ollama Server and Model

```bash
python3 debug_scripts/debug_check_ollama.py
```

**Expected Output**: Should confirm Ollama is running and `phi3:mini` is available.

### 2.2. Check Vault Configuration

```bash
python3 debug_scripts/debug_check_vault_config.py
```

**Expected Output**: Should confirm successful authentication to Vault and list all found/missing API keys.

## 3. Run a Test Hunt

Once your environment is set up and verified, you can run a full test hunt:

```bash
bash debug_scripts/debug_run_hunt.sh
```

This script executes the main orchestrator, which will attempt to run a full bug bounty hunt against `scanme.nmap.org`.

**What to look for in the output:**
- Any `[ERROR]` or `[WARNING]` messages.
- Confirmation of agents initializing.
- Reconnaissance results (subdomains, dorks).
- AI prioritization results.
- Scanner output (Nuclei, etc.).
- Threat intelligence enrichment.
- Kill chain attempts.
- Report generation.

## 4. Next Steps for Android Devices (If Applicable)

If you plan to use Android devices for distributed scanning:
- Ensure SSH is set up and running in Termux on each device.
- Copy the entire Wilsons-Raiders project to your devices.
- Update `config/devices.yaml` with the correct IP addresses and SSH key name.
- Ensure the `device_agent.py` script is present in the project root on your Android devices.

Happy hunting!
