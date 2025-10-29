import requests
import logging
from secret_manager import SecretManager

class HackerOneReporter:
    def __init__(self):
        self.secrets = SecretManager()
        self.h1_api_token = self.secrets.get_secret('wilsons-raiders/creds', 'HACKERONE_API_TOKEN')
        self.mantisbt_url = self.secrets.get_secret('wilsons-raiders/creds', 'MANTISBT_URL')
        self.mantisbt_user = self.secrets.get_secret('wilsons-raiders/creds', 'MANTISBT_USER')
        self.mantisbt_pass = self.secrets.get_secret('wilsons-raiders/creds', 'MANTISBT_PASSWORD')

    def check_validation_status(self, finding_id: str) -> bool:
        try:
            url = f"{self.mantisbt_url}/api/rest/issues/{finding_id}"
            resp = requests.get(url, auth=(self.mantisbt_user, self.mantisbt_pass))
            if resp.status_code == 200:
                issue = resp.json().get('issue', {})
                # Assume custom field 'hil_status' or status name
                status = issue.get('status', {}).get('name', '').lower()
                hil_status = next((f['value'].lower() for f in issue.get('custom_fields', []) if f['name'].lower() == 'hil_status'), None)
                return (status == 'hil-approved') or (hil_status == 'approved')
            else:
                logging.error(f"MantisBT API error: {resp.status_code}")
                return False
        except Exception as e:
            logging.error(f"Error checking HiL status: {e}")
            return False

    def generate_report(self, finding: dict) -> str:
        # Simple Markdown report generator
        report = f"""# Vulnerability Report

**Title:** {finding.get('title', 'N/A')}

**Target:** {finding.get('target', 'N/A')}

**Description:**
{finding.get('description', 'N/A')}

**Impact:**
{finding.get('impact', 'N/A')}

**Steps to Reproduce:**
{finding.get('steps', 'N/A')}

**Remediation:**
{finding.get('remediation', 'N/A')}

**References:**
{finding.get('references', 'N/A')}

---
"""
        return report

    def submit_to_hackerone(self, finding: dict) -> bool:
        if not self.check_validation_status(finding['id']):
            logging.warning('Finding has not passed HiL check. Submission blocked.')
            return False
        url = 'https://api.hackerone.com/v1/reports'
        headers = {
            'Authorization': f'Bearer {self.h1_api_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'title': finding.get('title'),
            'vulnerability_information': self.generate_report(finding),
            'target': finding.get('target'),
            'severity_rating': finding.get('severity', 'medium'),
            # Add other required fields as needed
        }
        try:
            resp = requests.post(url, json=data, headers=headers)
            if resp.status_code in (200, 201):
                logging.info('Report submitted to HackerOne.')
                return True
            else:
                logging.error(f'HackerOne API error: {resp.status_code} {resp.text}')
                return False
        except Exception as e:
            logging.error(f'Error submitting to HackerOne: {e}')
            return False
