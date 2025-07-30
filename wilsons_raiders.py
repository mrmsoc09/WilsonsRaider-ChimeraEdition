import argparse
from dotenv import load_dotenv
from core import ui
from core.managers.state_manager import StateManager
from core.managers.recon_manager import ReconManager
from core.managers.scanning_manager import ScanningManager
from core.managers.ai_manager import AIManager
from core.managers.reporting_manager import ReportingManager
from core.managers.purple_manager import PurpleManager

def main():
    parser = argparse.ArgumentParser(description='Wilsons Raiders - Chimera Edition')
    parser.add_argument('command', choices=['hunt', 'list', 'report'])
    parser.add_argument('target', nargs='?')
    parser.add_argument('--name', help='A unique name for the hunt/assessment.')
    args = parser.parse_args()

    load_dotenv()
    ui.print_banner()

    state_manager = StateManager()
    ai_manager = AIManager()
    reporting_manager = ReportingManager(state_manager)
    purple_manager = PurpleManager(state_manager)
    scanning_manager = ScanningManager(state_manager)
    recon_manager = ReconManager(state_manager)

    if args.command == 'hunt':
        if not args.target or not args.name:
            ui.print_error('The `hunt` command requires a target and a --name.')
            return

        ui.print_header(f"--- Starting Hunt: {args.name} ---")
        ui.print_info(f"[>] Target: {args.target}")

        assessment = state_manager.create_assessment(name=args.name, target=args.target)
        ui.print_success(f"Assessment created with ID: {assessment.id}")

        # --- Phase 1: Reconnaissance ---
        recon_data = recon_manager.run(assessment.id, args.target)

        # --- Phase 2: AI Prioritization (with guaranteed initialization) ---
        prioritized_assets = []
        prioritized_templates = []
        if recon_data and recon_data.get('subdomains'):
            prioritized_assets, prioritized_templates = ai_manager.prioritize_assets(recon_data.get('subdomains', []))
        else:
            ui.print_warning("No subdomains found, skipping AI component.")

        # --- Phase 3: Active Scanning (with resilient call) ---
        scanning_manager.run(assessment.id, prioritized_assets, prioritized_templates)

        ui.print_header("--- --- Hunt Finished --- ---")

    elif args.command == 'list':
        ui.print_info("Listing assessments...")

    elif args.command == 'report':
        ui.print_info("Generating report...")

if __name__ == "__main__":
    main()
