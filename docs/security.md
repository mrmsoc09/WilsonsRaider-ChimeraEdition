# Security Hardening for Wilsons-Raiders

Ensuring the security of the Wilsons-Raiders platform is paramount, especially given its role in offensive security operations. This document outlines the key security hardening measures implemented and provides guidance for maintaining a secure deployment.

## Core Security Hardening Measures

*   **Non-root, Minimal Containers**: All Wilsons-Raiders components are designed to run within containers using a non-root user (`wilson`) and leveraging minimal base images (e.g., `python:3.12-slim`). This approach significantly reduces the attack surface by limiting privileges and unnecessary software.

*   **Read-only Filesystem, tmpfs for /tmp**: Containers are configured with a read-only root filesystem. Temporary files and runtime data are directed to `tmpfs` mounts for `/tmp`, ensuring that no persistent malicious code can be written to the container's main filesystem and that temporary data is purged upon container shutdown.

*   **Resource Limits**: To prevent resource exhaustion attacks and contain potential runaway processes, containers are configured with strict resource limits for memory (e.g., 1GB RAM) and CPU (e.g., 1 CPU). These limits can be adjusted based on deployment needs but should always be set to reasonable values.

*   **Enhanced Docker Security Options**:
    *   **Seccomp (Secure Computing Mode)**: Docker containers utilize seccomp profiles to restrict the system calls available to processes within the container, mitigating a wide range of kernel-level vulnerabilities.
    *   **AppArmor**: AppArmor profiles are employed to enforce mandatory access controls, further limiting container capabilities and access to host resources. Users are encouraged to replace the default unconfined profiles with custom, fine-grained AppArmor profiles tailored to their specific operational requirements.

*   **Network Segmentation**: Wilsons-Raiders deployments leverage custom Docker bridge networks (e.g., `wr_net`) to segment internal container communication from other networks. This isolates components and limits the blast radius in case of a compromise.

## Guidance for Secure Deployment

*   **Custom AppArmor/Firejail Profiles**: This file serves as an example and guidance for creating custom AppArmor or Firejail profiles. It is strongly recommended to develop and deploy profiles that specifically restrict the capabilities of each Wilsons-Raiders container to only what is absolutely necessary for its function.
*   **Regular Updates**: Keep your host operating system, Docker daemon, and Wilsons-Raiders application images regularly updated to patch known vulnerabilities.
*   **Vulnerability Scanning**: Periodically scan your Wilsons-Raiders deployment and its underlying infrastructure for vulnerabilities.

By adhering to these principles and actively managing your deployment's security posture, you can significantly reduce the risks associated with operating an advanced security automation platform.