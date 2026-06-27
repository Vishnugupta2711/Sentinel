# Sentinel Deployment Guide

This guide details how to deploy Sentinel to a production Kubernetes cluster or via Docker Compose for enterprise readiness.

## 1. Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.0+
- Minimum Specs: 4 vCPUs, 8GB RAM

## 2. Docker Compose (Single Node)

For rapid deployments or edge-servers inside physical plants, run:

```bash
docker-compose up --build -d
```

### Services Deployed:
- `backend`: FastAPI Python Engine (Port 8000)
- `frontend`: Next.js Static Server (Port 3000)
- `nginx`: Reverse Proxy handling SSL/TLS termination and CSP enforcement (Port 80/443)
- `prometheus`: Scrapes metrics from `backend` (Port 9090)

## 3. Kubernetes (Cluster)

For high-availability, Sentinel can be scaled horizontally.

1. Ensure the `IntelligenceDispatcher` is configured to use Redis Pub/Sub instead of local memory queues (`config.yaml`).
2. Deploy the standard Helm chart (located in `infra/helm`).

```bash
helm install sentinel infra/helm/sentinel-stack
```

## 4. Security Hardening
Sentinel is shipped hardened by default:
- **Rootless Containers**: The `Dockerfile` establishes a low-privileged `appuser`.
- **Gunicorn Workers**: The backend is bound with `uvicorn` using single workers optimized for `uvloop`.
- **Nginx Headers**: All HTTP requests are protected by X-Frame-Options, X-Content-Type-Options, and robust Content Security Policies.
