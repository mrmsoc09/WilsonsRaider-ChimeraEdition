# Security Hardening for Wilsons-Raiders

- Non-root, minimal containers (python:3.12-slim, user wilson)
- Read-only filesystem, tmpfs for /tmp
- Resource limits: 1GB RAM, 1 CPU
- Docker security options: seccomp, AppArmor (replace unconfined with custom profiles)
- Network segmentation: wr_net custom bridge
- See this file for AppArmor/Firejail profile examples and extension guidance.
