# ADR-0001: Introduce Policy Engine (Guardian)
- Enforce OPSEC (low-and-slow), rate limits, and tool gating centrally.
- Token-bucket rate limiting per provider; configurable via configs/policy.yaml.
- Validation redundancy optional; default disabled per user decision.
