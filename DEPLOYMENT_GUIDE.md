# WilsonsRaider-ChimeraEdition Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Options](#deployment-options)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Tool Integration Setup](#tool-integration-setup)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Observability](#monitoring--observability)
9. [Troubleshooting](#troubleshooting)

---

## Overview

WilsonsRaider-ChimeraEdition is a production-grade AI-powered autonomous bug bounty hunting platform with comprehensive security integrations:

**Core Platform**: Python-based scanning and orchestration engine
**Integrations**:
- **TheHive**: Incident response and case management
- **Wazuh**: Security monitoring and SIEM
- **Shuffle**: Security orchestration and automation (SOAR)
- **Cortex**: Threat intelligence and observable analysis
- **n8n**: Workflow automation
- **HashiCorp Vault**: Secrets management

---

## Prerequisites

### Hardware Requirements

**Minimum (Development)**:
- CPU: 4 cores
- RAM: 16 GB
- Storage: 100 GB SSD

**Recommended (Production)**:
- CPU: 16+ cores
- RAM: 64+ GB
- Storage: 500+ GB NVMe SSD

### Software Requirements

**Docker Deployment**:
- Docker Engine 24.0+
- Docker Compose 2.20+

**Kubernetes Deployment**:
- Kubernetes 1.27+
- kubectl 1.27+
- Helm 3.12+
- Storage provisioner (Rook-Ceph, Longhorn, or cloud provider)

**Recommended Tools**:
- ArgoCD (GitOps)
- Cert-Manager (TLS certificates)
- Prometheus + Grafana (Monitoring)
- Istio/Linkerd (Service mesh)

---

## Deployment Options

### 1. Docker Compose (Development/Testing)

Use for local development and testing.

```bash
# Clone repository
git clone https://github.com/yourusername/WilsonsRaider-ChimeraEdition.git
cd WilsonsRaider-ChimeraEdition

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Launch with Docker Compose
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

**Access Points**:
- WilsonsRaider Dashboard: http://localhost:8000
- TheHive: http://localhost:9000
- Wazuh Dashboard: https://localhost:443
- Shuffle: https://localhost:3001
- n8n: http://localhost:5678
- Vault: http://localhost:8200

### 2. Kubernetes (Production)

Use for production deployments with high availability and scalability.

---

## Docker Deployment

### Step 1: Environment Setup

Create `.env` file:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password

# Vault
VAULT_TOKEN=your_vault_token

# TheHive
THEHIVE_API_KEY=your_thehive_api_key

# Wazuh
WAZUH_USERNAME=admin
WAZUH_PASSWORD=your_wazuh_password
WAZUH_INDEXER_PASSWORD=your_indexer_password

# Shuffle
SHUFFLE_API_KEY=your_shuffle_api_key

# Cortex
CORTEX_API_KEY=your_cortex_api_key

# n8n
N8N_USER=admin
N8N_PASSWORD=your_n8n_password
N8N_API_KEY=your_n8n_api_key

# OpenAI
OPENAI_API_KEY=sk-your_openai_api_key
```

### Step 2: Build and Launch

```bash
# Build custom image
docker build -t wilsons-raider:latest -f Dockerfile.enhanced .

# Launch all services
docker-compose -f docker-compose.production.yml up -d

# View logs
docker-compose -f docker-compose.production.yml logs -f wilsons-raider

# Stop services
docker-compose -f docker-compose.production.yml down
```

### Step 3: Verify Services

```bash
# Check health
curl http://localhost:8000/api/health

# Expected output:
# {
#   "status": "healthy",
#   "integrations": {
#     "thehive": true,
#     "wazuh": true,
#     "shuffle": true,
#     "cortex": true,
#     "n8n": true
#   }
# }
```

---

## Kubernetes Deployment

### Step 1: Prerequisites

```bash
# Verify Kubernetes cluster
kubectl cluster-info

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install cert-manager for TLS
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Install NGINX Ingress Controller
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

### Step 2: Create Namespace

```bash
kubectl apply -f k8s/base/namespace.yaml
```

### Step 3: Configure Secrets

**Option A: Manual (Development)**

```bash
# Edit secrets file with your values
vim k8s/base/secrets.yaml

# Apply secrets
kubectl apply -f k8s/base/secrets.yaml
```

**Option B: Sealed Secrets (Production)**

```bash
# Install Sealed Secrets controller
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system

# Create sealed secret
kubeseal --format=yaml < k8s/base/secrets.yaml > k8s/base/sealed-secrets.yaml

# Apply sealed secret
kubectl apply -f k8s/base/sealed-secrets.yaml
```

**Option C: External Secrets Operator (Recommended)**

```bash
# Install External Secrets Operator
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace

# Configure SecretStore (Vault backend)
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: wilsons-raider
spec:
  provider:
    vault:
      server: "http://vault:8200"
      path: "secret"
      version: "v2"
      auth:
        tokenSecretRef:
          name: vault-token
          key: token
EOF
```

### Step 4: Deploy Core Components

```bash
# Apply RBAC
kubectl apply -f k8s/base/rbac.yaml

# Create PVCs
kubectl apply -f k8s/base/pvc.yaml

# Deploy services
kubectl apply -f k8s/base/service.yaml

# Deploy application
kubectl apply -f k8s/base/deployment.yaml

# Configure ingress
kubectl apply -f k8s/base/ingress.yaml

# Apply network policies
kubectl apply -f k8s/base/networkpolicy.yaml
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -n wilsons-raider

# Check services
kubectl get svc -n wilsons-raider

# Check ingress
kubectl get ingress -n wilsons-raider

# View logs
kubectl logs -n wilsons-raider -l app=wilsons-raider --tail=100 -f
```

---

## Tool Integration Setup

### TheHive Configuration

1. Access TheHive: http://localhost:9000
2. Create organization: "WilsonsRaider"
3. Generate API key: Settings → API Keys → New
4. Update secret with API key

### Wazuh Configuration

1. Access Wazuh Dashboard: https://localhost:443
2. Login with admin credentials
3. Navigate to Settings → API Configuration
4. Enable API and note credentials
5. Configure custom rules for WilsonsRaider events

### Shuffle Configuration

1. Access Shuffle: https://localhost:3001
2. Create workflows for incident response
3. Configure app integrations (TheHive, Wazuh, email, Slack)
4. Generate API key and update secrets

### Cortex Configuration

1. Access Cortex: http://localhost:9001
2. Create organization and user
3. Configure analyzers:
   - VirusTotal
   - AbuseIPDB
   - Shodan
   - OTXQuery
   - MaxMind GeoIP
4. Generate API key

---

## Security Hardening

### Container Security

```bash
# Scan images with Trivy
trivy image wilsons-raider:latest

# Run as non-root
docker run --user 1001:1001 wilsons-raider:latest

# Enable read-only filesystem
docker run --read-only --tmpfs /tmp wilsons-raider:latest
```

### Kubernetes Security

**Pod Security Standards**:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: wilsons-raider
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**OPA Gatekeeper Policies**:

```bash
# Install Gatekeeper
helm install gatekeeper gatekeeper/gatekeeper \
  --namespace gatekeeper-system \
  --create-namespace

# Apply policies
kubectl apply -f k8s/policies/
```

**Network Policies**: Already configured in `k8s/base/networkpolicy.yaml`

### Secrets Management

**Best Practices**:
1. Use External Secrets Operator with Vault
2. Enable encryption at rest for etcd
3. Use RBAC to limit secret access
4. Rotate secrets regularly
5. Never commit secrets to Git

---

## Monitoring & Observability

### Prometheus & Grafana

```bash
# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Create ServiceMonitor for WilsonsRaider
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: wilsons-raider
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: wilsons-raider
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
EOF
```

**Pre-built Dashboards**: Import `k8s/monitoring/grafana-dashboard.json`

### Logging (ELK/Loki)

```bash
# Install Loki stack
helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace \
  --set promtail.enabled=true \
  --set grafana.enabled=true
```

### Distributed Tracing (Jaeger)

```bash
# Install Jaeger Operator
kubectl create namespace observability
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.49.0/jaeger-operator.yaml
```

---

## Troubleshooting

### Common Issues

**1. Pods Not Starting**

```bash
# Check pod status
kubectl describe pod <pod-name> -n wilsons-raider

# Check logs
kubectl logs <pod-name> -n wilsons-raider

# Common fixes:
# - Verify secrets are configured
# - Check resource limits
# - Verify PVCs are bound
```

**2. Integration Not Working**

```bash
# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
wget -O- http://thehive:9000/api/status

# Check DNS resolution
nslookup thehive.wilsons-raider.svc.cluster.local

# Verify network policies allow traffic
kubectl describe networkpolicy -n wilsons-raider
```

**3. Performance Issues**

```bash
# Check resource usage
kubectl top pods -n wilsons-raider

# Increase resources
kubectl edit deployment wilsons-raider -n wilsons-raider
# Update resources.limits and resources.requests

# Scale horizontally
kubectl scale deployment wilsons-raider --replicas=3 -n wilsons-raider
```

### Health Checks

```bash
# Platform health
curl http://localhost:8000/api/health

# TheHive health
curl http://localhost:9000/api/status

# Wazuh API health
curl -k -u admin:password https://localhost:55000/

# Cortex health
curl http://localhost:9001/api/status
```

---

## Additional Resources

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](docs/API_REFERENCE.md)
- [Security Best Practices](docs/SECURITY.md)
- [Contributing Guide](CONTRIBUTING.md)

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/WilsonsRaider-ChimeraEdition/issues
- Documentation: https://docs.wilsons-raider.io
- Community: https://discord.gg/wilsons-raider
