# Configuration Guide

This document details the various configuration options available for Wilsons-Raiders, allowing users to tailor the system's behavior to their specific needs. Configuration is primarily managed through YAML and HCL files located in the `config/` and `configs/` directories.

## Configuration Files Overview

### `config/config.yaml`
This is the main application configuration file. It contains core settings for various modules, integrations, and operational parameters.
*(Further details on specific parameters and their values will be added here.)*

### `configs/policy.yaml`
This file defines the policies governing the system's operations, including OPSEC settings, rate limits, and validation profiles. It is central to the Policy Engine (Guardian) as described in [ADR-0001: Introduce Policy Engine (Guardian)](adr/ADR-0001-Policy-Engine.md).
*(Further details on policy parameters and their impact will be added here.)*

### `config/vault-policy.hcl`
This HashiCorp Configuration Language (HCL) file is used to define policies for HashiCorp Vault, managing access to secrets and sensitive operations within the Wilsons-Raiders ecosystem.
*(Further details on Vault policy definitions and usage will be added here.)*

## General Configuration Principles

*   **YAML Structure:** Most configuration is done using YAML, which emphasizes human readability and maintainability.
*   **Default Values:** Many parameters have sensible default values, requiring configuration only for custom requirements.
*   **Environment Variables:** Sensitive information or deployment-specific overrides can often be provided via environment variables, adhering to the principle of "configuration via environment."

## How to Apply Changes

After modifying any configuration file, a restart of the relevant Wilsons-Raiders components may be necessary for the changes to take effect. Consult the [User Guide](USER_GUIDE.md) and [Quickstart Guide](QUICKSTART.md) for detailed instructions on deploying and restarting the system.