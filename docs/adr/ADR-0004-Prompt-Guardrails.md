# ADR-0004: Prompt Guardrails and Untrusted Content Handling
- Separate control prompts from untrusted data.
- Sanitize untrusted inputs; provenance tagging; tool-calling only.
- Secrets never injected into model prompts; use handles.
