# ADR-0003: Data Storage and Caching
- Use PostgreSQL for core entities; local caches for NVD/Exploit-DB with integrity checks.
- Artifact storage externalized (S3-compatible) with retention policies.
