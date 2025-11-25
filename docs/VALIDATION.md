# Validation Profiles and Tactics

This document outlines the available validation methods, profiles, and the rationale behind their use in Wilsons-Raiders.

## Validation Methods (Tactics)

The system supports the following tactics for validating findings:

*   **Metasploit check (non-destructive)**: Utilizes the `check` module of Metasploit to verify the applicability of an exploit without causing harm.
*   **Custom Nuclei template**: Purpose-built Nuclei templates for specific findings, with a preference for safe probes to minimize impact.
*   **Custom sandboxed script**: A last-resort option for validation, executed within a strict sandbox with robust OPSEC controls.

## Validation Profiles

Validation profiles, configured via `policy.yaml`, group these tactics to define different levels of validation aggressiveness:

*   **`safe`**: Primarily uses `nuclei_template` for validation.
*   **`normal`**: Combines `nuclei_template` with `metasploit_check`.
*   **`aggressive`**: Employs all available tactics: `nuclei_template`, `metasploit_check`, and `custom_script`.

## Optional Redundancy

Validation redundancy is optional and disabled by default. When enabled, a quorum of successful validations (e.g., multiple tactics confirming a finding) may be required before a finding is officially marked as validated. By default, the system accepts the highest-confidence single success.
