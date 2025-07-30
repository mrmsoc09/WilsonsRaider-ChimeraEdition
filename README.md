# Wilsons-Raiders

## Architecture
Wilsons-Raiders is a modular, AI-driven bug bounty and security automation framework. It leverages Docker, Whonix, and a non-root user for OPSEC, with all secrets managed in HashiCorp Vault. Core components:
- **EC2 Instances**: For scalable, cloud-based operations.
- **Docker Compose**: Orchestrates Postgres, MongoDB, MantisBT, Vault, and the main hunting container.
- **Whonix Gateway**: Ensures all traffic is routed through Tor for anonymity.
- **Proxychains4**: Forces all tool traffic through Whonix.
- **Non-root User**: All operations run as an unprivileged user for security.

## Supported Security Tools
- **SAST**: Bandit, Semgrep, SonarQube
- **DAST**: OWASP ZAP, Arachni, Nikto
- **BAST**: Lynis, OpenSCAP
- **CAST**: Trivy, Clair
- **Other**: Nuclei, Subfinder, Httpx, FFUF, Arjun, SQLmap, Metasploit, Dependency-Check, Gitleaks, Nmap, MassDNS

## AI Agents
- **ProgramSelectorAgent**: Analyzes and selects optimal bug bounty programs.
- **ReconAnalysisAgent**: Synthesizes raw recon data into actionable insights.
- **VulnerabilityScanAgent**: Analyzes scanner output to prioritize findings and filter false positives.
- **ReportGenerationAgent**: Drafts high-quality vulnerability reports in Markdown.
- **SASTAgent, DASTAgent, BASTAgent, CASTAgent**: Specialized agents for each security testing protocol.
- **ComplianceAgent**: Ensures findings and workflow meet compliance standards.
- **ThreatIntelAgent**: Integrates threat intelligence feeds and context.
- **RemediationAgent**: Suggests and tracks remediation steps.
- **AutomationOrchestratorAgent**: Coordinates multi-agent workflows and automation.

## Setup
1. Clone the repo:
   ```bash
   git clone <your-repo-url>
   cd wilsons-raiders
   ```
2. Copy and edit environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your secrets and Whonix Gateway IP
   ```
3. Run the setup script:
   ```bash
   python3 setup.py
   ```
4. Start the stack:
   ```bash
   docker-compose up --build
   ```

## Usage
- Start a hunt:
  ```bash
  python3 orchestrator.py start --target example.com --cost-tier balanced
  ```
- Review a finding:
  ```bash
  python3 orchestrator.py review --id <finding_id>
  ```
- Use the developer CLI:
  ```bash
  python3 dev_cli.py setup|build|run|lint|test|clean
  ```

## Security
- **Vault**: All secrets (API keys, tokens) are stored and accessed securely via Vault.
- **Whonix & Proxychains4**: All network traffic is anonymized through Tor.
- **Non-root User**: The main container runs as an unprivileged user.
- **Cost Tiers**: Control LLM/model usage and tool intensity for OPSEC and budget.
- **Industry Best Practices**: Minimal base image, up-to-date packages, secure configs, and strict secret handling.

## Cost Tiers
- **Economic**: Uses low-cost LLMs (e.g., GPT-3.5), minimal tool intensity.
- **Balanced**: Default; moderate LLMs (e.g., GPT-4), balanced tool usage.
- **High-Performance**: Uses top-tier LLMs (e.g., GPT-4o), maximum tool intensity.

## SelfCritic_Agent
See `SelfCritic_Agent.md` for the conceptual definition.

## Automated Reporting & Communication
- **HackerOne Automation**: Reports are generated and submitted automatically. Follow-up status checks and comments are supported.
- **Notifications**:
  - **Telegram**: Automated updates and follow-ups are sent to your Telegram bot/channel.
  - **Matrix/Element**: Automated updates and follow-ups are sent to your self-hosted Element (Matrix) room.
- All credentials are securely managed in Vault and .env.


## Multi-Agent Architecture (2025 Update)
- Orchestrator: crewAI-based, coordinates all agents and workflows.
- User Hub: FastAPI backend, React frontend for interactive dashboard.
- REST API: Secure endpoints for automation and integration.
- Plugin/Script Loader: Auto-discovers and manages scripts/plugins.
- Workflow Editor: Visual, drag-and-drop pipeline builder.
- Enhanced CLI: Interactive terminal experience.
- All security/testing agents are modular and crewAI-compatible.

**Migration:**
- Existing agents and tools will be refactored as crewAI-compatible modules.
- User hub and API will provide a unified, interactive experience.
- Scripts and plugins can be dropped into the scripts/ directory for auto-loading.


## MAST (Mobile Application Security Testing)
- **MASTAgent:** crewAI agent for mobile app and hardware analysis.
- **Tool Wrappers:** MobSF, Frida, Objection, apktool, jadx, Ghidra, QARK, otool, class-dump, Hopper, etc.
- **Script Templates:** For static, dynamic, and hardware analysis.
- **Supports:** Android (APK), iOS (IPA), and hardware/firmware workflows.


## Team Personas
- **RedTeamAgent:** Offensive security automation.
- **BlueTeamAgent:** Defensive security automation.
- **PurpleTeamAgent:** Coordination, assessment, and collaboration.
- **TeamManager:** Create, manage, and orchestrate teams of agents for scenario-based workflows.


## Security Controls (2025)
- Non-root, minimal containers (see Dockerfile).
- Agent isolation: process/container separation, AppArmor/Firejail profiles (in progress).
- Vault-only secrets, no secrets in code or env files.
- Centralized, tamper-evident audit logging for all agent and user actions.
- Team-based workflows: Red, Blue, Purple Team agents, dynamic team creation.
