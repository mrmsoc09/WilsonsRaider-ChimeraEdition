import os
import json
import re
import litellm
from core import ui

class AIManager:
    """Manages all interactions with Language Models."""

    def __init__(self):
        litellm.suppress_provider_output = True
        self.providers = [
            {"model": "openrouter/auto", "api_key_env": "OPENROUTER_API_KEY"},
            {"model": "gemini/gemini-1.5-pro-latest", "api_key_env": "GOOGLE_GEMINI_API_KEY"},
            {"model": "claude-3-opus-20240229", "api_key_env": "ANTHROPIC_API_KEY"},
            {"model": "perplexity/llama-3-sonar-small-32k-online", "api_key_env": "PERPLEXITY_API_KEY"},
            {"model": 'gpt-4-turbo', "api_key_env": "OPENAI_API_KEY"},
        ]
        ui.print_info("AIManager initialized.")

    def _call_llm_with_fallback(self, prompt: str):
        for provider in self.providers:
            model = provider["model"]
            api_key_env = provider["api_key_env"]
            api_key = os.environ.get(api_key_env)

            if not api_key:
                ui.print_warning(f"API key for {model} not found. Skipping.")
                continue

            try:
                ui.print_info(f"Attempting AI call with {model}")
                response = litellm.completion(
                    model=model,
                    messages=[{"content": prompt, "role": "user"}],
                    api_key=api_key
                )
                return response.choices[0].message.content
            except Exception as e:
                ui.print_error(f"AI call failed for {model}: {e}")
                continue

        ui.print_error("All AI providers failed.")
        return None

    def prioritize_assets(self, assets: list):
        ui.print_subheader("The Oracle's Verdict (AI Analysis) - Asset Prioritization")
        ui.print_info(f"Asking the AI to prioritize from {len(assets)} discovered assets...")

        if not assets:
            ui.print_warning("No assets provided to prioritize.")
            return [], []

        asset_sample = '\n'.join(assets[:200])
        prompt = (
            f'You are an expert penetration tester prioritizing assets for a bug bounty hunt. '
            f'Based on the following list of subdomains for a target, identify the top 20 most promising assets. '
            f'Also, based on these promising assets, suggest up to 10 relevant Nuclei template categories (e.g., cves, technologies, exposures) to run.\n\n' 
            f'Subdomain List:\n{asset_sample}\n\n' 
            f'Respond ONLY with a JSON object with two keys: "prioritized_assets" and "nuclei_templates".'
        )

        response_text = self._call_llm_with_fallback(prompt)
        if response_text:
            try:
                # Find the JSON object within the response text
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_json = json.loads(json_match.group(0))
                    prioritized = response_json.get('prioritized_assets', [])
                    templates = response_json.get('nuclei_templates', [])
                    ui.print_success(f"AI recommended {len(prioritized)} assets and {len(templates)} template categories.")
                    return prioritized, templates
            except Exception:
                pass # Fall through to the final return if parsing fails
        
        # If all else fails, return two empty lists to fulfill the contract.
        ui.print_error("AI prioritization failed.")
        return [], []
