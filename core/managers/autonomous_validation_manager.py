"""Autonomous Validation Manager - Multi-Agent Validation Orchestration

Orchestrates redundant validation using multiple agents and tools.
Version: 2.0.0
"""

import subprocess
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ValidationAgent:
    """Represents a validation agent/tool."""
    def __init__(self, name: str, path: str, command_template: List[str]):
        self.name = name
        self.path = Path(path)
        self.command_template = command_template
        self.available = self.path.exists()

class AutonomousValidationManager:
    """Manages autonomous validation using multiple redundant agents."""

    def __init__(self, config: dict, ui_manager=None, state_manager=None):
        self.config = config
        self.ui = ui_manager
        self.state_manager = state_manager

        # Initialize validation agents
        self.agents = self._initialize_agents()

        # Validation policy: require N out of M agents to confirm
        self.min_confirmations = config.get('validation', {}).get('min_confirmations', 2)

        logger.info(f"AutonomousValidationManager initialized: {len(self.agents)} agents, "
                   f"min_confirmations={self.min_confirmations}")

    def _initialize_agents(self) -> Dict[str, ValidationAgent]:
        """Initialize validation agents."""
        base_path = Path(self.config.get('validation', {}).get('tools_path', './tools'))

        agents = {
            'pentest_agent': ValidationAgent(
                name='PentestAgent',
                path=base_path / 'PentestAgent',
                command_template=['python', 'main.py', '--url', '{target}']
            ),
            'nuclei': ValidationAgent(
                name='Nuclei',
                path=Path('/usr/bin/nuclei'),
                command_template=['nuclei', '-u', '{target}', '-t', '{template}']
            ),
            'metasploit': ValidationAgent(
                name='Metasploit',
                path=Path('/usr/bin/msfconsole'),
                command_template=['msfconsole', '-q', '-x', 'use {module}; set RHOST {target}; check']
            ),
            'custom_validator': ValidationAgent(
                name='CustomValidator',
                path=base_path / 'custom_validator.py',
                command_template=['python', str(base_path / 'custom_validator.py'), '{target}']
            )
        }

        available = [name for name, agent in agents.items() if agent.available]
        logger.info(f"Validation agents available: {', '.join(available)}")

        return agents

    async def run(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run autonomous validation on list of vulnerabilities."""
        logger.info(f"Starting autonomous validation on {len(vulnerabilities)} findings")
        if self.ui:
            self.ui.run_subheading("Autonomous Validation")

        validation_results = {
            'total_findings': len(vulnerabilities),
            'validated_findings': [],
            'failed_validations': [],
            'pending_manual': [],
            'timestamp': datetime.utcnow().isoformat()
        }

        if not vulnerabilities:
            logger.info("No vulnerabilities to validate")
            return validation_results

        for vuln in vulnerabilities:
            result = await self.validate_vulnerability(vuln)

            if result['status'] == 'confirmed':
                validation_results['validated_findings'].append(result)
            elif result['status'] == 'failed':
                validation_results['failed_validations'].append(result)
            else:
                validation_results['pending_manual'].append(result)

        logger.info(f"Validation complete: {len(validation_results['validated_findings'])} confirmed")

        if self.ui:
            self.ui.print(f"[green]✓ {len(validation_results['validated_findings'])} findings confirmed[/green]")

        return validation_results

    async def validate_vulnerability(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single vulnerability using redundant agents."""
        vuln_name = vulnerability.get('name', 'Unknown')
        target = vulnerability.get('matched_at') or vulnerability.get('host', '')

        logger.info(f"Validating: {vuln_name} at {target}")
        if self.ui:
            self.ui.print(f"[cyan]Validating: {vuln_name}[/cyan]")

        result = {
            'vulnerability': vuln_name,
            'target': target,
            'status': 'pending',
            'confirmations': 0,
            'agent_results': [],
            'validated_at': datetime.utcnow().isoformat()
        }

        # Select appropriate agents for vulnerability type
        selected_agents = self._select_agents_for_vuln(vulnerability)

        # Run validation with each agent
        for agent_name in selected_agents:
            if agent_name not in self.agents or not self.agents[agent_name].available:
                continue

            agent_result = await self._run_agent_validation(agent_name, vulnerability, target)
            result['agent_results'].append(agent_result)

            if agent_result['confirmed']:
                result['confirmations'] += 1

        # Determine final status based on confirmations
        if result['confirmations'] >= self.min_confirmations:
            result['status'] = 'confirmed'
            logger.info(f"Vulnerability confirmed by {result['confirmations']} agents")
            if self.ui:
                self.ui.print(f"  [green]✓ Confirmed by {result['confirmations']} agents[/green]")
        elif result['confirmations'] > 0:
            result['status'] = 'partial'
            logger.warning(f"Partial confirmation: {result['confirmations']}/{self.min_confirmations}")
            if self.ui:
                self.ui.print(f"  [yellow]⚠ Partial confirmation - manual review needed[/yellow]")
        else:
            result['status'] = 'failed'
            logger.info(f"Validation failed: no confirmations")
            if self.ui:
                self.ui.print("  [red]✗ Could not validate[/red]")

        return result

    def _select_agents_for_vuln(self, vulnerability: Dict[str, Any]) -> List[str]:
        """Select appropriate validation agents for vulnerability type."""
        vuln_name = vulnerability.get('name', '').lower()

        # Agent selection logic based on vulnerability type
        if 'xss' in vuln_name or 'injection' in vuln_name:
            return ['pentest_agent', 'nuclei', 'custom_validator']
        elif 'sqli' in vuln_name or 'sql' in vuln_name:
            return ['pentest_agent', 'nuclei', 'metasploit']
        elif 'rce' in vuln_name or 'command' in vuln_name:
            return ['metasploit', 'nuclei', 'custom_validator']
        else:
            return ['nuclei', 'custom_validator']

    async def _run_agent_validation(self, agent_name: str, vulnerability: Dict[str, Any],
                                    target: str) -> Dict[str, Any]:
        """Run validation with specific agent."""
        agent = self.agents[agent_name]

        logger.debug(f"Running {agent.name} validation on {target}")

        result = {
            'agent': agent_name,
            'confirmed': False,
            'evidence': [],
            'error': None
        }

        try:
            # Build command from template
            command = self._build_command(agent, vulnerability, target)

            # Execute validation
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(agent.path.parent) if agent.path.is_file() else str(agent.path)
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)

            # Parse results
            if proc.returncode == 0:
                output = stdout.decode()
                result['confirmed'] = self._parse_agent_output(agent_name, output)
                result['evidence'].append(output[:500])  # Truncate for storage
            else:
                result['error'] = stderr.decode()

        except asyncio.TimeoutError:
            logger.warning(f"{agent.name} validation timed out")
            result['error'] = 'Timeout'
        except Exception as e:
            logger.error(f"{agent.name} validation error: {e}")
            result['error'] = str(e)

        return result

    def _build_command(self, agent: ValidationAgent, vulnerability: Dict[str, Any],
                      target: str) -> List[str]:
        """Build command from agent template."""
        command = []

        for part in agent.command_template:
            if '{target}' in part:
                command.append(part.replace('{target}', target))
            elif '{template}' in part:
                template = vulnerability.get('template_id', 'default')
                command.append(part.replace('{template}', template))
            elif '{module}' in part:
                module = self._get_msf_module(vulnerability)
                command.append(part.replace('{module}', module))
            else:
                command.append(part)

        return command

    def _get_msf_module(self, vulnerability: Dict[str, Any]) -> str:
        """Get appropriate Metasploit module for vulnerability."""
        vuln_name = vulnerability.get('name', '').lower()

        # Simple mapping - could be expanded
        if 'apache' in vuln_name:
            return 'exploit/multi/http/apache_mod_cgi_bash_env_exec'
        elif 'wordpress' in vuln_name:
            return 'auxiliary/scanner/http/wordpress_scanner'
        else:
            return 'auxiliary/scanner/http/http_version'

    def _parse_agent_output(self, agent_name: str, output: str) -> bool:
        """Parse agent output to determine if vulnerability is confirmed."""
        # Agent-specific parsing logic
        confirmation_indicators = {
            'pentest_agent': ['VULNERABLE', 'CONFIRMED', 'SUCCESS'],
            'nuclei': ['[high]', '[critical]', '[medium]'],
            'metasploit': ['The target is vulnerable', 'Exploit completed'],
            'custom_validator': ['CONFIRMED', 'TRUE']
        }

        indicators = confirmation_indicators.get(agent_name, [])
        return any(indicator.lower() in output.lower() for indicator in indicators)

    def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        available_agents = sum(1 for agent in self.agents.values() if agent.available)

        return {
            'total_agents': len(self.agents),
            'available_agents': available_agents,
            'min_confirmations_required': self.min_confirmations,
            'agents': {name: agent.available for name, agent in self.agents.items()}
        }
