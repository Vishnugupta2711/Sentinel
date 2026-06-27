# README Presentation Assets

This document contains markdown snippets and badge configurations designed to be copied directly into the main `README.md` repository to ensure it reflects the enterprise nature of the product.

## 1. Hero Header

```markdown
<div align="center">
  <img src="docs/product/branding/sentinel_logo.svg" alt="Sentinel Logo" width="200" />
  <h1>Sentinel: Industrial AI Operating System</h1>
  <p><em>Transforming industrial safety through real-time deterministic computer vision and predictive planning.</em></p>
  <br />
</div>
```

## 2. Dynamic Badges
Use shields.io for crisp, flat-square badges matching our dark theme.

```markdown
<div align="center">
  <img src="https://img.shields.io/badge/Architecture-Event--Driven-06B6D4?style=flat-square&logo=apachekafka&logoColor=white" />
  <img src="https://img.shields.io/badge/Latency-%3C%2020ms-34D399?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Frontend-Next.js%2016-000000?style=flat-square&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/State-In--Memory-DC382D?style=flat-square&logo=redis&logoColor=white" />
</div>
```

## 3. Folder Structure Visualization
```markdown
## System Architecture

\`\`\`text
Sentinel/
├── backend/                # Core AI Engines & Services
│   ├── api/                # FastAPI Gateway & WebSockets
│   ├── intelligence/       # Core Logic (Risk, Chronos, Planner)
│   ├── domain/             # DDD Entities & Value Objects
│   └── infrastructure/     # Kafka, Redis, PostgreSQL Repositories
├── frontend/               # Mission Control (Next.js)
│   ├── app/                # Server Components & Routing
│   ├── components/         # Design System & UI Elements
│   └── store/              # Zustand Real-Time State
├── docs/product/           # Executive Documentation & Diagrams
└── docker-compose.yml      # Production Orchestration
\`\`\`
```

## 4. Visual Workflow Integration
```markdown
## How Sentinel Works

1. **Ingestion**: Raw RTSP camera streams are processed instantly.
2. **State Generation**: The Vision Engine extracts bounding boxes and projects them into a 3D semantic World State.
3. **Compound Risk**: The Risk Engine uses a Neo4j Hazard Graph to identify intersecting dangers.
4. **Prediction**: The Chronos Engine forecasts trajectories to predict accidents before they happen.
5. **Mitigation**: The Counterfactual Planner recommends the precise action to save lives.

![System Flow](docs/product/diagrams/ai_pipeline.svg)
```

## 5. UI Showcase
```markdown
## Mission Control Interface

![Mission Control](docs/product/screenshots/mission_control.png)

*The real-time Mission Control interface streaming thousands of events per second with zero browser lag.*
```
