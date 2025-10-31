from openai import OpenAI
from wr_ui import print_danger

class AIManager:
    """Manages all interactions with the OpenAI API."""

    def __init__(self, config: dict):
        
        api_key = config.get('openai', {}).get('api_key', 'YOUR_OPENAI_API_KEY')
        if not api_key or api_key == 'YOUR_OPENAI_API_KEY':
            raise ValueError("OpenAI API key is not configured in config/config.yaml")
        self.client = OpenAI(api_key=api_key)
        self.model = config.get('openai', {}).get('model', 'gpt-4-turbo')

    def analyze_recon_data(self, recon_data: dict) -> str:
        # Existing method placeholder
        return "AI analysis of recon data."

    def generate_dynamic_nuclei_template(self, recon_data: dict) -> str | None:
        """
        Generates a dynamic Nuclei template based on reconnaissance data.
        """
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a security tool expert that generates Nuclei templates in YAML format."},
                    {"role": "user", "content": prompt}
                ]
            )
            generated_yaml = response.choices[0].message.content.strip()
            if '```yaml' in generated_yaml:
                generated_yaml = generated_yaml.split('```yaml')[1].split('```')[0].strip()
            elif '```' in generated_yaml:
                 generated_yaml = generated_yaml.split('```')[1].strip()

            return generated_yaml
        except Exception as e:
            print_danger(f"Failed to generate Nuclei template: {e}")
            return None
