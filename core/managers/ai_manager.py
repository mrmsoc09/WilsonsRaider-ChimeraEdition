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
        
        if not assets:
            return [], []
        
        asset_sample = '\n'.join(assets[:200])
        prompt = (
            f'You are an expert penetration tester. Prioritize these assets for bug bounty testing '
            f'and suggest relevant Nuclei template categories.\n\n'
            f'Assets:\n{asset_sample}\n\n'
            f'Respond with JSON: {{"prioritized_assets": [...], "nuclei_templates": [...]}}'
        )
        
        response_text = self._call_llm_with_fallback(prompt, temperature=0.3)
        
        if response_text:
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    prioritized = data.get('prioritized_assets', [])
                    templates = data.get('nuclei_templates', [])
                    ui.print_success(f"Recommended {len(prioritized)} assets, {len(templates)} templates")
                    return prioritized, templates
            except Exception as e:
                logger.error(f"Failed to parse AI response: {e}")
        
        return assets[:20], ['cves', 'technologies', 'exposures']
