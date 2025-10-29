import yaml
from pathlib import Path
from core import ui

class ForgeManager:
    """An AI-driven agent to forge custom scanning templates in real-time."""

    def __init__(self, ai_manager: AIManager):
        self.ai = ai_manager

    def generate_nuclei_template(self, template_name: str, recon_data: dict) -> Path | None:
        """
        Uses the AI to generate a custom Nuclei template based on recon data.

        Args:
            template_name (str): The descriptive name for the template file.
            recon_data (dict): A dictionary of findings from the recon phase.

        Returns:
            Path | None: The path to the generated template file, or None if failed.
        """
        ui.print_purple(f"The Forge: Invoking AI to craft a custom Nuclei template for '{template_name}'...")

        template_content = self.ai.generate_dynamic_nuclei_template(recon_data)

        if not template_content:
            ui.print_danger("The Forge: AI failed to generate a valid template.")
            return None

        try:
            # Validate if the generated content is valid YAML
            yaml.safe_load(template_content)

            # Save the template to a temporary file
            template_dir = Path('/tmp/chimera_templates')
            template_dir.mkdir(exist_ok=True)
            template_path = template_dir / f"{template_name}.yaml"

            with open(template_path, 'w') as f:
                f.write(template_content)

            ui.print_success(f"The Forge: Successfully forged new template: {template_path}")
            return template_path

        except (yaml.YAMLError, IOError) as e:
            ui.print_danger(f"The Forge: Error processing generated template: {e}")
            return None
