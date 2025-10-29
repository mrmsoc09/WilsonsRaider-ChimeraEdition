import argparse
from dotenv import load_dotenv
from core import ui
from core.managers.state_manager import StateManager
from core.managers.recon_manager import ReconManager
from core.managers.scanning_manager import ScanningManager
from core.managers.ai_manager import AIManager
from core.managers.audit_logger import AuditLogger
# from core.managers.forge_manager import ForgeManager # Temporarily commented out

def main():
    parser = argparse.ArgumentParser(description='Wilsons Raiders - Chimera Edition')
    parser.add_argument('command', choices=['hunt'], help='The command to execute. Currently, only "hunt" is supported.')
    parser.add_argument('--target', required=True, help='The root domain to target for the hunt.')
    parser.add_argument('--program-name', required=True, help='A unique name for the program or hunt.')
    args = parser.parse_args()

    load_dotenv()
    ui.print_banner()

    # --- Manager Initialization ---
    audit_logger = AuditLogger()
    db_uri = 'sqlite:///wilsons_raiders.db'
    state_manager = StateManager(db_uri=db_uri)
    # The ForgeManager requires an AIManager instance to generate templates.
    # But the AIManager also needs the ForgeManager to trigger the forging.
    # We solve this by initializing them separately and linking them.
    # forge_manager = ForgeManager(ai_manager=None) # Temporarily None
    ai_manager = AIManager()
    # forge_manager.ai = ai_manager # Now link the AI manager back to the forge.
    # ai_manager.forge_manager = forge_manager # Link forge_manager to AIManager

    scanning_manager = ScanningManager(state_manager)
    recon_manager = ReconManager(state_manager)

    if args.command == 'hunt':
        ui.print_header(f"--- Starting Hunt: {args.program_name} ---")
        audit_logger.log(
            event_name='hunt_started',
            component='Orchestrator',
            details={'program_name': args.program_name, 'target': args.target}
        )
        ui.print_info(f"[>] Target: {args.target}")

        # --- Assessment Creation ---
        try:
            assessment_id = state_manager.create_assessment(program_name=args.program_name, target=args.target)
            ui.print_success(f"Assessment created with ID: {assessment_id}")
            audit_logger.log(
                event_name='assessment_created',
                component='Orchestrator',
                details={'assessment_id': assessment_id}
            )
        except Exception as e:
            ui.print_error(f"Failed to create assessment. Aborting. Error: {e}")
            return

        # --- Phase 1: Reconnaissance ---
        # The ReconManager is responsible for finding assets and persisting them to the DB.
        recon_data = recon_manager.run(assessment_id, args.target)
        if not recon_data.get('subdomains'):
            ui.print_error("Reconnaissance failed to find any subdomains. Aborting hunt.")
            return
        
        ui.print_success(f"Reconnaissance complete. Found {len(recon_data['subdomains'])} subdomains.")
        audit_logger.log(
            event_name='recon_finished',
            component='ReconManager',
            details={'subdomains_found': len(recon_data['subdomains'])}
        )

        # --- Phase 2: AI Prioritization ---
        # The AIManager suggests which assets to focus on and which templates to use.
        prioritized_assets, prioritized_templates = ai_manager.prioritize_assets(recon_data.get('subdomains', []))
        audit_logger.log(
            event_name='prioritization_finished',
            component='AIManager',
            details={
                'prioritized_assets_count': len(prioritized_assets),
                'suggested_templates_count': len(prioritized_templates)
            }
        )
        
        if not prioritized_assets:
            ui.print_warning("AI prioritization did not return any assets. Defaulting to all found subdomains.")
            prioritized_assets = recon_data.get('subdomains', [])

        # --- Phase 3: Active Scanning ---
        # The ScanningManager runs scanners against prioritized assets and saves findings.
        scanning_manager.run(assessment_id, prioritized_assets, prioritized_templates)
        audit_logger.log(
            event_name='scanning_finished',
            component='ScanningManager',
            details={}
        )

        # --- Phase 4: Post-Hunt Analysis ---
        ai_manager.analyze_hunt_results(assessment_id, state_manager)
        audit_logger.log(
            event_name='analysis_finished',
            component='AIManager',
            details={}
        )

        ui.print_header(f"--- Hunt Finished for {args.program_name} ---")
        vuln_count = len(state_manager.get_vulnerabilities_for_assessment(assessment_id))
        ui.print_success(f"Found a total of {vuln_count} potential vulnerabilities.")
        audit_logger.log(
            event_name='hunt_finished',
            component='Orchestrator',
            details={'vulnerabilities_found': vuln_count}
        )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        ui.print_error(f"An unexpected error occurred: {e}")