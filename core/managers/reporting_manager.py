"""Reporting Manager - Multi-format Report Generation and Export

Generates security assessment reports in multiple formats with templates.
Version: 2.0.0
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportFormat:
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"

class ReportingManager:
    """Manages report generation in multiple formats."""

    def __init__(self, state_manager=None, ui_manager=None, config: dict = None):
        self.state_manager = state_manager
        self.ui = ui_manager
        self.config = config or {}
        self.output_dir = Path(self.config.get('reporting', {}).get('output_dir', '/tmp/reports'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReportingManager initialized: output_dir={self.output_dir}")

    def generate_report(self, assessment_id: int, kill_chain_narrative: str = None,
                       format: str = ReportFormat.MARKDOWN) -> str:
        """Generate comprehensive security assessment report."""
        logger.info(f"Generating {format} report for assessment {assessment_id}")
        if self.ui:
            self.ui.run_subheading(f"Report Generation: Assessment {assessment_id}")

        # Gather data
        vulnerabilities = self._get_vulnerabilities(assessment_id)
        metrics = self._calculate_metrics(vulnerabilities)

        # Generate report based on format
        if format == ReportFormat.MARKDOWN:
            content = self._generate_markdown(assessment_id, vulnerabilities, metrics, kill_chain_narrative)
        elif format == ReportFormat.HTML:
            content = self._generate_html(assessment_id, vulnerabilities, metrics, kill_chain_narrative)
        elif format == ReportFormat.JSON:
            content = self._generate_json(assessment_id, vulnerabilities, metrics, kill_chain_narrative)
        elif format == ReportFormat.CSV:
            content = self._generate_csv(vulnerabilities)
        else:
            content = self._generate_markdown(assessment_id, vulnerabilities, metrics, kill_chain_narrative)

        # Save to file
        output_file = self._save_report(assessment_id, content, format)

        logger.info(f"Report generated: {output_file}")
        if self.ui:
            self.ui.print(f"[green]✓ Report saved: {output_file}[/green]")

        return str(output_file)

    def _get_vulnerabilities(self, assessment_id: int) -> List[Any]:
        """Retrieve vulnerabilities from state manager."""
        if self.state_manager:
            return self.state_manager.get_vulnerabilities_for_assessment(assessment_id)
        return []

    def _calculate_metrics(self, vulnerabilities: List[Any]) -> Dict[str, Any]:
        """Calculate report metrics."""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}

        for vuln in vulnerabilities:
            severity = getattr(vuln, 'severity', 'info').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        return {
            'total_findings': len(vulnerabilities),
            'severity_breakdown': severity_counts,
            'critical_count': severity_counts['critical'],
            'high_count': severity_counts['high'],
            'medium_count': severity_counts['medium'],
            'low_count': severity_counts['low']
        }

    def _generate_markdown(self, assessment_id: int, vulnerabilities: List[Any],
                          metrics: Dict[str, Any], kill_chain: str = None) -> str:
        """Generate Markdown report."""
        report = f"""# Security Assessment Report

"""
        report += f"**Assessment ID:** {assessment_id}\n"
        report += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n
"

        # Executive Summary
        report += "## Executive Summary\n\n"
        report += f"Total Findings: **{metrics['total_findings']}**\n\n"
        report += "### Severity Breakdown\n\n"
        report += f"- Critical: {metrics['critical_count']}\n"
        report += f"- High: {metrics['high_count']}\n"
        report += f"- Medium: {metrics['medium_count']}\n"
        report += f"- Low: {metrics['low_count']}\n\n"

        # Kill Chain Analysis
        if kill_chain:
            report += "## Dynamic Kill Chain Analysis\n\n"
            report += kill_chain + "\n\n"

        # Detailed Findings
        report += "## Detailed Findings\n\n"

        if not vulnerabilities:
            report += "No vulnerabilities found.\n"
        else:
            for i, vuln in enumerate(vulnerabilities, 1):
                report += f"### {i}. {vuln.name} ({vuln.severity})\n\n"
                report += f"- **Tool:** {vuln.tool}\n"
                report += f"- **Asset:** {getattr(vuln.asset, 'name', 'N/A') if hasattr(vuln, 'asset') else 'N/A'}\n"
                report += f"- **Description:** {getattr(vuln, 'description', 'N/A')}\n"

                if hasattr(vuln, 'cwe_id'):
                    report += f"- **CWE:** {vuln.cwe_id}\n"
                if hasattr(vuln, 'cvss_score'):
                    report += f"- **CVSS:** {vuln.cvss_score}\n"

                report += "\n"

        return report

    def _generate_html(self, assessment_id: int, vulnerabilities: List[Any],
                      metrics: Dict[str, Any], kill_chain: str = None) -> str:
        """Generate HTML report."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Security Assessment Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .metric { background: #f0f0f0; padding: 10px; margin: 10px 0; }
        .critical { color: #d32f2f; }
        .high { color: #f57c00; }
        .medium { color: #fbc02d; }
        .low { color: #388e3c; }
    </style>
</head>
<body>
"""

        html += f"<h1>Security Assessment Report</h1>"
        html += f"<p><strong>Assessment ID:</strong> {assessment_id}</p>"
        html += f"<p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>"

        html += "<h2>Executive Summary</h2>"
        html += f"<div class='metric'>Total Findings: {metrics['total_findings']}</div>"
        html += "<h3>Severity Breakdown</h3>"
        html += f"<ul>"
        html += f"<li class='critical'>Critical: {metrics['critical_count']}</li>"
        html += f"<li class='high'>High: {metrics['high_count']}</li>"
        html += f"<li class='medium'>Medium: {metrics['medium_count']}</li>"
        html += f"<li class='low'>Low: {metrics['low_count']}</li>"
        html += f"</ul>"

        html += "<h2>Detailed Findings</h2>"
        for i, vuln in enumerate(vulnerabilities, 1):
            html += f"<h3>{i}. {vuln.name}</h3>"
            html += f"<p><strong>Severity:</strong> <span class='{vuln.severity.lower()}'>{vuln.severity}</span></p>"
            html += f"<p><strong>Tool:</strong> {vuln.tool}</p>"
            html += f"<p><strong>Description:</strong> {getattr(vuln, 'description', 'N/A')}</p>"

        html += "</body></html>"
        return html

    def _generate_json(self, assessment_id: int, vulnerabilities: List[Any],
                      metrics: Dict[str, Any], kill_chain: str = None) -> str:
        """Generate JSON report."""
        report_data = {
            'assessment_id': assessment_id,
            'generated_at': datetime.utcnow().isoformat(),
            'metrics': metrics,
            'kill_chain': kill_chain,
            'vulnerabilities': []
        }

        for vuln in vulnerabilities:
            vuln_data = {
                'name': vuln.name,
                'severity': vuln.severity,
                'tool': vuln.tool,
                'description': getattr(vuln, 'description', None),
                'asset': getattr(vuln.asset, 'name', None) if hasattr(vuln, 'asset') else None
            }
            report_data['vulnerabilities'].append(vuln_data)

        return json.dumps(report_data, indent=2)

    def _generate_csv(self, vulnerabilities: List[Any]) -> str:
        """Generate CSV report."""
        csv = "Name,Severity,Tool,Asset,Description\n"

        for vuln in vulnerabilities:
            name = vuln.name.replace(',', ';')
            desc = getattr(vuln, 'description', 'N/A').replace(',', ';')
            asset = getattr(vuln.asset, 'name', 'N/A') if hasattr(vuln, 'asset') else 'N/A'
            csv += f"{name},{vuln.severity},{vuln.tool},{asset},{desc}\n"

        return csv

    def _save_report(self, assessment_id: int, content: str, format: str) -> Path:
        """Save report to file."""
        extensions = {
            ReportFormat.MARKDOWN: 'md',
            ReportFormat.HTML: 'html',
            ReportFormat.JSON: 'json',
            ReportFormat.CSV: 'csv',
            ReportFormat.PDF: 'pdf'
        }

        ext = extensions.get(format, 'txt')
        filename = f"assessment_{assessment_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{ext}"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            f.write(content)

        return filepath

    def generate_executive_summary(self, assessment_id: int) -> str:
        """Generate executive summary only."""
        vulnerabilities = self._get_vulnerabilities(assessment_id)
        metrics = self._calculate_metrics(vulnerabilities)

        summary = f"""Executive Summary - Assessment {assessment_id}\n"""
        summary += f"Total Findings: {metrics['total_findings']}\n"
        summary += f"Critical: {metrics['critical_count']}, High: {metrics['high_count']}, "
        summary += f"Medium: {metrics['medium_count']}, Low: {metrics['low_count']}\n"

        return summary
