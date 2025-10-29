import logging
from .recon_workflow import ReconWorkflow
from .phase_workflows import (
    EnumerationWorkflow, VulnDiscoveryWorkflow, ExploitationWorkflow,
    PostExploitationWorkflow, ReportingWorkflow, RemediationWorkflow, RedTeamWorkflow
)

class WorkflowOrchestrator:
    """
    Orchestrates selection, planning, execution, and chaining of workflow phases.
    Autonomous, extensible, and context-driven.
    """
    PHASE_WORKFLOW_MAP = {
        'recon': ReconWorkflow,
        'enumeration': EnumerationWorkflow,
        'vulndiscovery': VulnDiscoveryWorkflow,
        'exploitation': ExploitationWorkflow,
        'postexploitation': PostExploitationWorkflow,
        'reporting': ReportingWorkflow,
        'remediation': RemediationWorkflow,
        'redteam': RedTeamWorkflow,
    }

    def __init__(self, context):
        """
        context: dict with engagement/task details, including phases and objectives.
        """
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results = {}
        self.errors = []

    def analyze_context(self):
        """
        Analyze context to determine required phases and objectives.
        """
        phases = self.context.get('phases')
        if not phases:
            # Default to all phases in order
            phases = [
                'recon', 'enumeration', 'vulndiscovery', 'exploitation',
                'postexploitation', 'reporting', 'remediation', 'redteam'
            ]
        self.logger.info(f"Selected phases: {phases}")
        return phases

    def select_workflow(self, phase):
        """
        Select the workflow class for a given phase.
        """
        workflow_cls = self.PHASE_WORKFLOW_MAP.get(phase.lower())
        if not workflow_cls:
            raise ValueError(f"No workflow found for phase: {phase}")
        return workflow_cls

    def run(self):
        """
        Plan, execute, and report for each selected workflow phase.
        Chain phases as needed.
        """
        phases = self.analyze_context()
        for phase in phases:
            try:
                self.logger.info(f"--- Starting phase: {phase} ---")
                workflow_cls = self.select_workflow(phase)
                workflow = workflow_cls(self.context)
                workflow.plan()
                workflow.execute()
                report = workflow.report()
                self.results[phase] = {
                    'status': workflow.get_status(),
                    'report': report
                }
                self.logger.info(f"--- Completed phase: {phase} ---")
            except Exception as e:
                self.logger.error(f"Error in phase {phase}: {e}")
                self.errors.append({phase: str(e)})
        return {
            'results': self.results,
            'errors': self.errors
        }

    def get_summary_report(self):
        """
        Aggregate reports from all phases.
        """
        lines = [f"WorkflowOrchestrator Summary Report"]
        for phase, data in self.results.items():
            lines.append(f"
=== {phase.upper()} ===
{data['report']}")
        if self.errors:
            lines.append("
Errors encountered during orchestration:")
            for err in self.errors:
                lines.append(str(err))
        return "
".join(lines)
