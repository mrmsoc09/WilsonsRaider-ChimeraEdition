"""AI Manager - Centralized LLM Interaction Layer

Manages all interactions with Language Models across multiple providers.
Version: 2.0.0
"""

import os
import json
import re
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import litellm
from core import ui
from secret_manager import SecretManager
<<<<<<< HEAD

class AIManager:
    """Manages all interactions with multiple LLM providers via litellm."""

    def __init__(self):
        litellm.suppress_provider_output = True
        self.secrets = SecretManager()
        self._load_api_keys()
        
        # Rule-based mapping of task types to specific, best-suited models.
        self.model_map = {
            'default': 'ollama/phi3:mini',
            'prioritization': 'anthropic/claude-3-haiku-20240307',
            'template_generation': 'openai/gpt-4o',
            'analysis': 'google/gemini-1.5-pro-latest',
            'report_writing': 'anthropic/claude-3-sonnet-20240229',
            'workflow_design': 'deepseek/deepseek-chat',
        }
        self.forge_manager = None # Will be set externally
        ui.print_info("AIManager initialized with multi-provider support.")

    def _load_api_keys(self):
        """Load API keys from Vault into environment variables for litellm to use."""
        keys = self.secrets.get_secret('wilsons-raiders/creds')
        if keys:
            os.environ['OPENAI_API_KEY'] = keys.get('OPENAI_API_KEY', '')
            os.environ['ANTHROPIC_API_KEY'] = keys.get('ANTHROPIC_API_KEY', '')
            os.environ['GOOGLE_API_KEY'] = keys.get('GEMINI_API_KEY', '')
            os.environ['DEEPSEEK_API_KEY'] = keys.get('DEEPSEEK_API_KEY', '')
            os.environ['OPENROUTER_API_KEY'] = keys.get('OPENROUTER_API_KEY', '')
            # Note: Grok is not yet a standard litellm provider and may require custom config.
        else:
            ui.print_warning("Could not load LLM API keys from Vault. Only local models will be available.")

    def _call_llm(self, prompt: str, system_prompt: str = "You are a helpful assistant.", task_type: str = 'default'):
        model_to_use = self.model_map.get(task_type, self.model_map['default'])
        ui.print_info(f"Using model: '{model_to_use}' for task type: '{task_type}'")
        
        try:
            # For local ollama models, we need to specify the api_base
            api_base = "http://localhost:11434" if model_to_use.startswith('ollama/') else None
            
            response = litellm.completion(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                api_base=api_base
            )
            return response.choices[0].message.content
        except Exception as e:
            ui.print_error(f"LLM call to '{model_to_use}' failed: {e}")
            
            # Fallback to the default local model if the cloud call failed
            if model_to_use != self.model_map['default']:
                ui.print_warning(f"Falling back to default model: {self.model_map['default']}")
                try:
                    response = litellm.completion(
                        model=self.model_map['default'],
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        api_base="http://localhost:11434"
                    )
                    return response.choices[0].message.content
                except Exception as e2:
                    ui.print_error(f"Fallback LLM call also failed: {e2}")
                    return None
            return None

    def prioritize_assets(self, assets: list[dict]):
        ui.print_subheader("The Oracle's Verdict (AI Analysis) - Asset Prioritization")
        ui.print_info(f"Asking the AI to prioritize from {len(assets)} discovered live assets...")

=======

logger = logging.getLogger(__name__)

class AIManager:
    """Centralized manager for all LLM interactions with multi-provider fallback."""
    
    def __init__(self, enable_caching: bool = True, max_retries: int = 3):
        litellm.suppress_debug_info = True
        self.secrets = SecretManager()
        self.max_retries = max_retries
        self.enable_caching = enable_caching
        self.providers = self._initialize_providers()
        self.response_cache = {} if enable_caching else None
        self.token_usage = {}
        ui.print_info(f"AIManager initialized with {len(self.providers)} providers")
    
    def _initialize_providers(self) -> List[Dict[str, Any]]:
        """Initialize provider configurations with Vault credentials."""
        provider_configs = [
            ("openai", "gpt-4-turbo", "OPENAI_API_KEY"),
            ("anthropic", "claude-3-opus-20240229", "ANTHROPIC_API_KEY"),
            ("google", "gemini/gemini-1.5-pro-latest", "GOOGLE_API_KEY"),
            ("openrouter", "openrouter/auto", "OPENROUTER_API_KEY"),
        ]
        
        providers = []
        for provider_name, model, key_name in provider_configs:
            try:
                api_key = self.secrets.get_secret('wilsons-raiders/creds', key_name)
                if api_key:
                    providers.append({
                        'provider': provider_name,
                        'model': model,
                        'api_key': api_key
                    })
                    logger.info(f"Provider {provider_name} configured")
            except Exception as e:
                logger.warning(f"Failed to configure {provider_name}: {e}")
        
        return providers
    
    def _call_llm_with_fallback(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Call LLM with automatic fallback across providers."""
        for provider_config in self.providers:
            provider = provider_config['provider']
            model = provider_config['model']
            api_key = provider_config['api_key']
            
            for attempt in range(self.max_retries):
                try:
                    ui.print_info(f"Attempting AI call with {provider}/{model} (attempt {attempt+1})")
                    
                    response = litellm.completion(
                        model=model,
                        messages=[{"content": prompt, "role": "user"}],
                        api_key=api_key,
                        temperature=temperature
                    )
                    
                    return response.choices[0].message.content
                
                except Exception as e:
                    logger.warning(f"AI call failed for {provider} (attempt {attempt+1}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
        
        ui.print_error("All AI providers failed")
        return None
    
    def prioritize_assets(self, assets: List[str]) -> Tuple[List[str], List[str]]:
        """Use AI to prioritize assets for testing."""
        ui.print_subheader("Asset Prioritization (AI Analysis)")
        ui.print_info(f"Analyzing {len(assets)} assets...")
        
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
        if not assets:
            return [], []
<<<<<<< HEAD

        asset_details = []
        for asset in assets[:200]:
            if isinstance(asset, dict):
                detail = f"- URL: {asset.get('name')}, Title: {asset.get('title', 'N/A')}, Status: {asset.get('status_code', 'N/A')}"
            else:
                detail = f"- URL: {asset}"
            asset_details.append(detail)
        asset_sample = '\n'.join(asset_details)

        prompt = (
            f'You are an expert penetration tester prioritizing assets for a bug bounty hunt. '
            f'Based on the following list of live web assets, identify the top 20 most promising URLs to attack. '
            f'Look for interesting keywords in the URL or page title (e.g., api, admin, dev, jenkins, grafana, old, etc.).\n\n'
            f'Also, based on these promising assets, suggest up to 10 relevant Nuclei template categories (e.g., cves, technologies, exposures, misconfiguration) to run.\n\n' 
            f'Live Asset List:\n{asset_sample}\n\n' 
            f'Respond ONLY with a JSON object with two keys: "prioritized_assets" (a list of URL strings) and "nuclei_templates" (a list of strings).'
        )

        response_text = self._call_llm(prompt, system_prompt="You are an expert penetration tester and bug bounty hunter.", task_type='prioritization')
=======
        
        asset_sample = '\n'.join(assets[:200])
        prompt = (
            f'You are an expert penetration tester. Prioritize these assets for bug bounty testing '
            f'and suggest relevant Nuclei template categories.\n\n'
            f'Assets:\n{asset_sample}\n\n'
            f'Respond with JSON: {{"prioritized_assets": [...], "nuclei_templates": [...]}}'
        )
        
        response_text = self._call_llm_with_fallback(prompt, temperature=0.3)
        
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
        if response_text:
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
<<<<<<< HEAD
                    response_json = json.loads(json_match.group(0))
                    prioritized = response_json.get('prioritized_assets', [])
                    templates = response_json.get('nuclei_templates', [])
                    ui.print_success(f"AI recommended {len(prioritized)} assets and {len(templates)} template categories.")

                    if prioritized and self.forge_manager:
                        most_promising_asset = prioritized[0]
                        hypothesis = f"The most promising asset, {most_promising_asset}, might have a misconfiguration or an exposed panel, given its name or title."
                        recon_data_for_forge = {
                            'target': most_promising_asset,
                            'hypothesis': hypothesis
                        }
                        forged_template_path = self.forge_manager.generate_nuclei_template(
                            template_name="chimera_hypothesis_1",
                            recon_data=recon_data_for_forge
                        )
                        if forged_template_path:
                            templates.append(str(forged_template_path))

                    return prioritized, templates
            except Exception as e:
                ui.print_error(f"AI prioritization failed to parse response: {e}")
        
        ui.print_error("AI prioritization failed.")
        return [], []

    def generate_dynamic_nuclei_template(self, recon_data: dict) -> str | None:
        hypothesis = recon_data.get('hypothesis', 'a potential misconfiguration')
        technologies = ", ".join(recon_data.get('technologies', ['generic']))
        
        prompt = f"""
        Act as a security expert specializing in Nuclei templates. Your task is to create a single, valid, targeted Nuclei template in YAML format based on the provided reconnaissance data. The template should be ready to run.

        **Reconnaissance Data:**
        - **Target:** {recon_data.get('target', 'N/A')}
        - **Detected Technologies:** {technologies}
        - **Interesting Paths:** {recon_data.get('interesting_paths', 'N/A')}
        - **Vulnerability Hypothesis:** {hypothesis}

        **Instructions:**
        1.  Create a unique, descriptive ID for the template.
        2.  Populate the 'info' block with a clear name, author ('WilsonsRaider-Forge'), severity, and description.
        3.  Construct a single `http` request.
        4.  Create a logical `matchers-condition`.
        5.  Define at least one matcher to detect the vulnerability.
        6.  **Output ONLY the raw YAML content of the Nuclei template. Do not include any other text or explanations.**
        """
        
        system_prompt = "You are a security tool expert that generates Nuclei templates in YAML format."
        generated_yaml = self._call_llm(prompt, system_prompt=system_prompt, task_type='template_generation')

        if generated_yaml:
            if '```yaml' in generated_yaml:
                generated_yaml = generated_yaml.split('```yaml')[1].split('```')[0].strip()
            elif '```' in generated_yaml:
                 generated_yaml = generated_yaml.split('```')[1].strip()
            return generated_yaml
        
        ui.print_error("Failed to generate Nuclei template.")
        return None

    def analyze_hunt_results(self, assessment_id: int, state_manager):
        ui.print_subheader("The Oracle's Verdict (AI Analysis) - Post-Hunt Analysis")
        vulnerabilities = state_manager.get_vulnerabilities_for_assessment(assessment_id)

        if not vulnerabilities:
            ui.print_info("No vulnerabilities found in this assessment. Nothing to analyze.")
            return

        ui.print_info(f"Analyzing {len(vulnerabilities)} findings from the hunt...")

        template_counts = {}
        for vuln in vulnerabilities:
            if vuln.tool == 'nuclei' and vuln.raw_finding:
                try:
                    raw = json.loads(vuln.raw_finding)
                    template_id = raw.get('template-id', 'unknown')
                    template_counts[template_id] = template_counts.get(template_id, 0) + 1
                except json.JSONDecodeError:
                    continue
        
        sorted_templates = sorted(template_counts.items(), key=lambda item: item[1], reverse=True)
        top_templates = sorted_templates[:10]

        prompt = (
            f'You are a master security strategist analyzing the results of a penetration test. '
            f'The assessment found {len(vulnerabilities)} total vulnerabilities. '
            f'The top 10 most effective Nuclei templates were:\n'
            f'{json.dumps(top_templates, indent=2)}\n\n'
            f'Based on this information, provide a brief, actionable summary for the human operator. '
            f'What types of vulnerabilities were most common? What should they focus on in the next hunt against a similar target? '
            f'Keep the summary to 3-4 bullet points.'
        )

        response_text = self._call_llm(prompt, system_prompt="You are a master security strategist.", task_type='analysis')

        if response_text:
            ui.print_info("--- Strategic Summary ---")
            print(response_text)
            ui.print_info("-------------------------")
        else:
            ui.print_error("Could not generate strategic summary.")
=======
                    data = json.loads(json_match.group(0))
                    prioritized = data.get('prioritized_assets', [])
                    templates = data.get('nuclei_templates', [])
                    ui.print_success(f"Recommended {len(prioritized)} assets, {len(templates)} templates")
                    return prioritized, templates
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")
        
        return assets[:20], ['cves', 'technologies', 'exposures']
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
