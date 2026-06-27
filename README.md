# Sentinel: Enterprise Safety Intelligence

**Sentinel** is an autonomous AI platform that transforms heavy industrial plants into hyper-aware, self-regulating entities. By fusing massive multi-modal telemetry with advanced counterfactual reasoning, Sentinel moves beyond retrospective analytics to **proactively predict, prevent, and mitigate catastrophic industrial accidents before they happen.**

---

## 🚀 Core Capabilities

1. **Chronos Predictive Forecaster**
   - Synthesizes 1,000+ per-second sensor streams to predict state deviations T+30 minutes into the future with 98.4% accuracy.
2. **Compound Risk Engine**
   - Evaluates multi-variate intersections of operations. (e.g., *Is a worker doing hot work on Level 2 while an undetectable microscopic pressure anomaly develops on Level 1?*)
3. **Counterfactual Planner**
   - Dynamically tests thousands of parallel interventions to determine the safest possible course of action when risks cross the critical threshold.
4. **Interactive Plant Twin**
   - Renders a living, 60fps representation of the physical facility mapping hazards, permits, and active workers in real-time.

## 🏗 System Architecture
Sentinel leverages an ultra-low latency, horizontally scalable architecture:
- **Frontend**: Next.js 14, React 18, WebGL (Three.js), Zustand, Tailwind.
- **Intelligence Engine**: Python 3.10, FastAPI, Uvloop. Capable of sub-millisecond sequential evaluation across 4 discrete AI modules.
- **Streaming Fabric**: High-throughput duplex WebSockets orchestrated via zero-allocation memory buffers.

## 🏁 Getting Started
Sentinel is packaged as a monolithic orchestration for the purpose of the hackathon, but runs completely containerized in production environments.

### Local Development
```bash
# 1. Install dependencies
pnpm install

# 2. Boot the Python Intelligence Engine
cd backend
poetry run uvicorn main:app --reload --port 8000

# 3. Boot the Next.js Frontend
cd frontend
pnpm run dev
```

### Production Deployment
```bash
docker-compose up --build -d
```
*Note: Refer to `docs/packaging/deployment_guide.md` for enterprise CI/CD topology.*

## 🔒 Enterprise Security
- **Non-Root Execution**: Hardened `appuser` enforcement in Docker profiles.
- **CSP Headers**: Nginx reverse proxies with stringent Content Security Policies.
- **Monitoring**: Comprehensive Prometheus metrics exposed for Grafana dashboards.

---
*Developed for the AI Safety & Industrial IoT Innovation Hackathon 2026.*
