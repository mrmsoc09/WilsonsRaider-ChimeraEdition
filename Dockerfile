# Hardened Dockerfile for Wilsons-Raiders
FROM python:3.12-slim as base

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     gosu tini ca-certificates     && rm -rf /var/lib/apt/lists/*

# Add non-root user
RUN useradd -m -u 1001 wilson

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions and use non-root user
RUN chown -R wilson:wilson /app
USER wilson

# Set entrypoint with tini for signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "orchestrator/orchestrator.py"]

# Security: Read-only filesystem (except /tmp)
# Uncomment the following line if your app supports it
# VOLUME ["/tmp"]
# RUN chmod 1777 /tmp
# LABEL docker.security.readonly="true"

# AppArmor/Firejail profiles should be mounted/applied at runtime
# See docs/security.md for profile examples
