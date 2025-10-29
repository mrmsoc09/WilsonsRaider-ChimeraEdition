# Validation Tactics (Redundancy Optional)

Available validation methods:
- Metasploit check (non-destructive): Uses module `check` to verify applicability.
- Custom Nuclei template: Purpose-built templates per finding; safe probes preferred.
- Custom sandboxed script: Last resort with strict sandbox and OPSEC controls.

Profiles (policy.yaml):
- safe: nuclei_template
- normal: nuclei_template + metasploit_check
- aggressive: nuclei_template + metasploit_check + custom_script

Redundancy is optional (default: disabled). When enabled, a quorum can be required before a finding is marked validated.
