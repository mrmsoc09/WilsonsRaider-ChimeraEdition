Below is the reconciled content for the README.md file after resolving the merge conflicts:

# WilsonsRaider-ChimeraEdition

**AI-Powered Autonomous Bug Bounty Hunting & Security Research Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Security: Vault](https://img.shields.io/badge/security-HashiCorp_Vault-purple.svg)](https://www.vaultproject.io/)

## 🎯 Overview

WilsonsRaider-ChimeraEdition is a next-generation autonomous security research platform combining advanced AI orchestration with battle-tested security tools. The framework enables security researchers to efficiently identify and exploit vulnerabilities.

### Key Capabilities

- **Self-Hosted AI Setup**
  - Wilsons-Raiders uses a local, self-hosted small language model (SLM) for all AI operations to ensure privacy and security. External API calls have been removed, and all operations are locally hosted.
  - **Installation Steps:**
    1. **Install Ollama**: Follow the instructions at [https://ollama.com](https://ollama.com) to install Ollama on your system.
    2. **Pull the Recommended Model**: The tool is optimized for small, fast models. The recommended model is `phi3:mini`.
       ```bash
       ollama pull phi3:mini
       ```
    3. **Run the Ollama Server**: In a separate terminal, run the Ollama server.
       ```bash
       ollama serve
       ```

- **🤖 Autonomous AI Orchestration**: Multi-agent coordination with adaptive LLM selection
- **🔍 Comprehensive Reconnaissance**: Subdomain enumeration, port scanning, tech fingerprinting
- **🛡️ Vulnerability Detection**: SAST, DAST, API security testing, exploit validation
- **📊 Intelligent Reporting**: Automated report generation with severity-based prioritization
- **🔐 Enterprise Security**: HashiCorp Vault integration, OPSEC-aware operations
- **⚡ Workflow Automation**: n8n-based orchestration with optional Human-in-Loop support

---

## 🏗️ System Architecture

### High-Level Architecture


┌─────────────────────────────────────────────────────────────────────┐
│ WilsonsRaider-ChimeraEdition Framework │
│ │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Automation Orchestrator Agent (Core Intelligence) │ │
│ │ • Multi-agent task coordination │ │
│ │ • Adaptive LLM selection (GPT-3.5/4/4o) │ │
│ │ • OPSEC enforcement & rate limiting │ │
│ │ • Comprehensive audit trails │ │
│ │ • Optional HiL checkpoints (non-mandatory) │ │
│ └─────────────────┬────────────────────────────────────────────┘ │
│ │ │
│ ┌──────────┴──────────┐ │
│ ▼ ▼ │
│ ┌─────────────┐ ┌─────────────┐ │
│ │ Recon │ │ Vuln Scan │ │
│ │ Agent │ │ Agent │ │
│ │ • Subfinder│ │ • Nuclei │ │
│ │ • Amass │ │ • SQLMap │ │
│ │ • Nmap │ │ • ffuf │ │
│ └─────────────┘ └─────────────┘ │
│ │ │ │
│ └──────────┬──────────┘ │
│ ▼ │
│ ┌──────────────────────────────────────────┐ │
│ │ Report Generation Agent │ │
│ │ • Markdown/PDF/HTML generation │ │
│ │ • Severity-based prioritization │ │
│ │ • Jira/Slack integration │ │
│ └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘


## 🧠 Core Component: Automation Orchestrator Agent

The **`automation_orchestrator_agent.py`** is the central intelligence hub orchestrating all AI-driven security workflows.

### Orchestration Flow

```python
# Detailed Orchestration Pipeline

1. Task Reception & Validation
   ├─ Input sanitization (injection prevention)
   ├─ Schema validation (required fields)
   ├─ OPSEC level enforcement
   └─ Scope boundary verification

2. Intelligent Model Selection
   ├─ Economic: gpt-3.5-turbo (fast, $0.0015/1K tokens)
   ├─ Balanced: gpt-4 (accurate, $0.03/1K tokens)
   └─ High-Performance: gpt-4o (maximum capability)

3. Task Decomposition
   ├─ Break complex tasks into atomic subtasks
   ├─ Identify required specialized agents
   ├─ Determine execution sequence
   └─ Allocate resources (timeouts, retries)

4. Subordinate Agent Delegation
   ├─ ReconAnalysisAgent: Asset discovery
   ├─ VulnerabilityScanAgent: Exploit testing
   ├─ SASTAgent: Code security analysis
   ├─ ThreatIntelAgent: CVE monitoring
   ├─ ReportGenerationAgent: Documentation
   └─ RemediationAgent: Fix generation

Key Implementation Features
1. Input Validation & Security
def _validate_task_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Prevents injection attacks, validates schema, sanitizes inputs"""
    # Allowlist-based validation
    if task_type not in self.VALID_TASK_TYPES:
        raise ValueError(f"Invalid task_type: {task_type}")
    # String sanitization
    sanitized[key] = value.replace('\\x00', '').replace('\\r', '').strip()
    
    # OPSEC validation
    if opsec_level not in self.OPSEC_LEVELS:
        raise ValueError(f"Invalid opsec_level: {opsec_level}")

2. Adaptive Model Selection
COST_TIERS = {
    'economic': 'gpt-3.5-turbo',        # Fast, cost-effective
    'balanced': 'gpt-4',                 # Accuracy vs cost tradeoff
    'high-performance': 'gpt-4o'         # Maximum capability
}

3. OPSEC Configuration
OPSEC_LEVELS = {
    'low': {
        'rate_limit': 100,              # requests/min
        'jitter': 0.1,                  # random delay
        'user_agent_rotation': False
    },
    'high': {
        'rate_limit': 10,
        'jitter': 0.5,
        'user_agent_rotation': True
    }
}

🚀 Quick Start
Prerequisites
Python 3.9+
Docker & Docker Compose
HashiCorp Vault
PostgreSQL 13+
Redis 6+
Installation
# Clone repository
git clone https://github.com/yourusername/WilsonsRaider-ChimeraEdition.git
cd WilsonsRaider-ChimeraEdition

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Vault
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='your-vault-token'

# Store secrets
vault kv put secret/wilsons-raiders/creds \
  OPENAI_API_KEY="sk-..." \
  SHODAN_API_KEY="..."

# Launch infrastructure
docker-compose up -d

Basic Usage
from core.ai_agents.automation_orchestrator_agent import AutomationOrchestratorAgent

# Initialize orchestrator
orchestrator = AutomationOrchestratorAgent(
    cost_tier='balanced',
    hil_enabled=False  # Optional HiL (default: False)
)

# Execute reconnaissance
recon_result = orchestrator.execute_task({
    'task_type': 'recon',
    'target': 'example.com',
    'opsec_level': 'high'
})

# Execute vulnerability scan
vuln_result = orchestrator.execute_task({
    'task_type': 'vulnerability_scan',
    'targets': recon_result['result']['subdomains']
})

📋 Workflow Examples
Automated Bug Bounty Hunt
from workflows.bug_bounty_workflow import BugBountyWorkflow

workflow = BugBountyWorkflow(
    program='example-corp',
    scope_file='scopes/example-corp.txt'
)

results = workflow.execute()

📚 Documentation
User Guide
Quick Start
Configuration
Workflows
🔒 Security & OPSEC
Use high OPSEC level for production
Rotate user agents and IPs
Implement rate limiting
Maintain audit trails
📄 License

MIT License - see LICENSE for details.


Ensure the above content is saved into your `README.md` file, replacing any conflicting lines. This will ensure a clean merge and accurate project presentation.
