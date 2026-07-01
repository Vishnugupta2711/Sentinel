# Sentinel Migration Strategy

> **Version:** 2.0
> **Status:** Draft
> **Migration Pattern:** Strangler Fig
> **Target Architecture:** Polyglot Event-Driven Microservices

---

# Table of Contents

1. Vision
2. Migration Principles
3. Current Architecture
4. Target Architecture
5. Technology Stack
6. Service Ownership
7. Data Contracts
8. Communication Strategy
9. Migration Phases
10. Current Audit
11. Success Criteria
12. Future Work

---

# Vision

Sentinel is transitioning from a Python-centric monolith into a distributed, event-driven industrial intelligence platform.

The migration follows the **Strangler Fig Pattern**, allowing existing functionality to remain operational while new Go and Scala services progressively replace application responsibilities. Python will ultimately be reduced to AI/ML inference services only.

The migration prioritizes:

- Zero downtime
- Backward compatibility
- Incremental delivery
- Contract-first development
- Independent deployability
- Production readiness

---

# Migration Principles

The migration is guided by the following engineering principles.

## Contract First

Protocol Buffers define every inter-service request, response and event schema.

No service owns handwritten DTOs.

Every language generates its models from the same contracts.

---

## Domain Ownership

Every language owns a specific domain.

Go

- Platform
- APIs
- State
- Orchestration

Scala

- Event Processing
- Kafka Streams
- CEP

Python

- Artificial Intelligence
- Machine Learning

---

## Event Driven

All asynchronous communication occurs through Kafka.

Services never call databases owned by another service.

---

## Independent Deployment

Every service must be independently deployable.

---

# Current Architecture

Current Backend

```

Next.js

↓

FastAPI

↓

World

↓

Simulation

↓

Timeline

↓

Risk

↓

Vision

↓

Planner

↓

Compliance

↓

Debrief

↓

Investigation

```

---

# Target Architecture

```

                    Internet

                        │

                 NGINX / Traefik

                        │

                 API Gateway (Go)

                        │

        ┌───────────────┼──────────────┐

        │               │              │

   Core Services   Auth Service   Notification

        │

   Kafka Event Bus

        │

 ┌──────┴─────────┐

 │                │

Scala Streams   Scala CEP

 │                │

 └────────┬───────┘

          │

 Python AI Services

Chronos

Vision

Risk

Compliance

          │

Redis

ClickHouse

Neo4j

Qdrant

```

---

# Technology Stack

| Layer | Technology | Responsibility |
|--------|------------|----------------|
| Frontend | Next.js + TypeScript | Mission Control |
| Contracts | Protocol Buffers + Buf | Shared data contracts |
| API Gateway | Go (Fiber/Echo) | REST, WebSockets, Authentication |
| Core Platform | Go | World, Timeline, Simulation |
| Streaming | Scala | Kafka Streams, CEP |
| AI | Python | Chronos, Vision, Risk, Compliance |
| Messaging | Kafka | Event Backbone |
| Cache | Redis | Live State |
| Analytics | ClickHouse | Event Storage |
| Graph | Neo4j | Hazard Graph |
| Vector Search | Qdrant | Semantic Search |

---

# Service Ownership

## Go

Owns

- API Gateway
- World
- World State
- Timeline
- Simulation
- Investigation
- Debrief
- Scheduler
- Notifications
- WebSockets
- Report Generation
- Orchestration

---

## Scala

Owns

- Kafka Consumers
- Kafka Producers
- Stream Processing
- Complex Event Processing
- Event Correlation
- ClickHouse Ingestion

Scala exposes no public APIs.

---

## Python

Owns

- Chronos
- Vision
- Risk
- Compliance
- RAG
- Embeddings

Python owns no application state.

---

# Data Contracts

Sentinel follows a **Contract-First Architecture**.

All service interfaces are defined using **Protocol Buffers (protobuf)**.

```

contracts/

├── proto/

│ ├── common.proto

│ ├── world.proto

│ ├── timeline.proto

│ ├── simulation.proto

│ ├── hazard.proto

│ ├── intelligence.proto

│ ├── chronos.proto

│ ├── planner.proto

│ ├── vision.proto

│ ├── compliance.proto

│ ├── investigation.proto

│ ├── debrief.proto

│ └── events.proto

│

├── buf.yaml

├── buf.gen.yaml

└── gen/

├── go/

├── scala/

├── python/

└── ts/

```

Every service generates code from the same protobuf definitions.

No handwritten cross-service DTOs are permitted.

Schema evolution follows semantic versioning.

---

# Communication Strategy

| Communication | Technology |
|---------------|------------|
| Browser → Gateway | REST + WebSocket |
| Gateway → Go | gRPC |
| Go → Python | gRPC |
| Go → Scala | Kafka |
| Scala → Go | Kafka |
| Python → Kafka | Kafka Events |
| Payload Serialization | Protocol Buffers |

---

# Migration Phases

---

## Phase 0: Platform Foundation

**Goal:** Establish monorepo, protobuf contracts, and CI/CD pipelines for Go, Scala, Python, and TypeScript.

### Deliverables

- `services/go/` — Go module with `cmd/`, `internal/`, `pkg/` layout
- `services/scala/` — sbt project with cats-effect or ZIO, Kafka Streams deps
- `contracts/` — Protobuf definitions for every domain, `buf.yaml`, `buf.gen.yaml`, generated code for Go/Scala/Python/TS
- `docker-compose.yml` — ClickHouse, Redpanda (Kafka-compatible), Redis, Neo4j, Qdrant added alongside existing containers
- CI/CD — GitHub Actions: build + lint Go, Scala, Python; protobuf lint via `buf lint`; Docker image build
- `Makefile` — targets: `buf-gen`, `buf-lint`, `build-go`, `build-scala`, `test-all`

### What Python sheds

Nothing yet — everything still runs in Python.

### Verify

- `make buf-gen` produces valid Go, Scala, Python, TS code
- `make build-go` compiles without errors
- `make build-scala` compiles without errors
- `docker compose up` starts all infra containers healthy
- CI passes on PR

---

## Phase 1: Go API Gateway (Strangler Facade)

**Goal:** Frontend talks exclusively to Go. Go proxies unknown routes to Python. No frontend changes needed beyond URL config.

### Deliverables

- `services/go/cmd/gateway/` — HTTP server (Fiber or Echo) with:
  - Reverse-proxy handler for `/api/v1/*` → `http://backend:8000`
  - Native health endpoints: `GET /health/live`, `GET /health/ready`
  - Native system endpoints: `GET /api/v1/system/version`, `GET /api/v1/system/status`
  - WebSocket multiplexer: `WS /ws/*` accepts frontend connections, fans out to Python WS streams
  - Request logging, rate limiting, CORS, request ID propagation
- `NEXT_PUBLIC_API_URL=http://localhost/api/v1` → Go (unchanged from current config)
- `NEXT_PUBLIC_WS_URL=ws://localhost/ws` → Go (unchanged from current config)
- Python `backend` container still runs — Go proxies to it
- Authentication middleware stub (validates JWT, passes user context via header to upstream)

### What Python sheds

- `system/` module (reimplemented natively in Go)
- Health endpoint responsibility

### Verify

- Frontend loads and proxies all API/WS traffic through Go with identical behaviour
- `GET /health/live` returns 200 from Go without hitting Python
- WebSocket connections to Go fan out to Python streams correctly
- go test ./... passes

---

## Phase 2: Core Platform (Go + Redis + ClickHouse)

**Goal:** World state, simulation, and timeline run in Go with Redis (live state) and ClickHouse (history). Python retains copies until switchover validated.

### Deliverables

**Go services:**

- `services/go/internal/world/` — Entity models (Plant, Zone, Worker, Sensor, Hazard, etc.), builder, `PlantState`, enums
- `services/go/internal/worldstate/` — Snapshot manager, immutable snapshots, diff engine, versioning; backed by Redis HSET
- `services/go/internal/simulator/` — Tick loop (1/sec), sensor drift, worker movement, weather simulation, event bus (channel-based pub/sub), hazard lifecycle
- `services/go/internal/timeline/` — Entry model (protobuf), ClickHouse-backed storage (async batch insert), time-range/entity queries, replay state machine
- `services/go/pkg/ws/` — Reusable WebSocket hub (connection tracking, broadcast, per-client channels)
- `services/go/cmd/core/` — Binary that hosts all three domains; gRPC server for Python AI engines to query live state
- Gateway updated: `/api/v1/world/*`, `/api/v1/simulator/*`, `/api/v1/timeline/*` routes now served natively from Go core, not proxied

**Infrastructure:**

- Redis — world state snapshots stored as JSON (key: `ws:{version}`, TTL-managed)
- ClickHouse — timeline events stored in `timeline` table (MergeTree engine, ordered by timestamp + entity_id)

### What Python sheds

- `world/` module
- `world_state/` module
- `simulator/` module
- `timeline/` module

### Verify

- Python simulator stopped → Go simulator produces identical snapshots
- Frontend WS streams from Go show same world state as before
- Timeline queries against ClickHouse return correct time ranges
- `docker compose down && up` — state persists in Redis + ClickHouse
- All world/timeline/simulator API tests pass against Go endpoints

---

## Phase 3: Hazard Graph (Go + Neo4j)

**Goal:** In-memory Python hazard graph replaced by Neo4j-backed Go service. Pathfinding, centrality, and CRUD served natively.

### Deliverables

- `services/go/internal/hazardgraph/` — Graph core (Cypher queries via Neo4j Go driver), CRUD for nodes/edges, BFS shortest path, centrality analytics
- `services/go/internal/hazardgraph/sync/` — Event listener on Redis pub/sub: when world state changes, sync graph topology
- Gateway updated: `/api/v1/graph/*` routes served natively from Go

### What Python sheds

- `hazard_graph/` module

### Verify

- Neo4j browser shows nodes and edges matching world state
- `GET /api/v1/graph/path?from=...&to=...` returns correct shortest path
- `GET /api/v1/graph/analytics/centrality` returns ranked nodes
- All hazard graph API tests pass against Go endpoints

---

## Phase 4: Scala Streaming Layer

**Goal:** All Kafka consumers, producers, and stream processing move to Scala. ClickHouse ingestion runs via Scala. Python no longer touches Kafka directly.

### Deliverables

**Scala services:**

- `services/scala/streams/` — Kafka Streams topology:
  - `world-state-events` → enrich, deduplicate, write to ClickHouse
  - `sensor-events` → windowed aggregates, anomaly detection, write to ClickHouse
  - `risk-events` → persist to ClickHouse
  - `planner-events` → persist to ClickHouse
- `services/scala/cep/` — Complex event processing:
  - Correlate multiple event streams (e.g., gas leak + hot work permit = escalation)
  - Emit derived events back to Kafka
- `services/scala/sink/` — ClickHouse batch inserter with buffer/flush (async, configurable batch size / interval)
- Python Kafka producer code removed — Go services produce directly to Kafka via `github.com/segmentio/kafka-go`

### What Python sheds

- `kafka-python` dependency
- Any direct Kafka producer/consumer code

### Verify

- Events produced by Go/Serices appear in ClickHouse within configured flush interval
- CEP rules fire correctly for correlated event patterns
- Kafka consumer lag stays near zero under load
- All tests pass

---

## Phase 5: Go Orchestrator + Python AI-Only

**Goal:** Python stripped to AI/ML inference only. Intelligence dispatcher, debrief, investigation, and inter-service orchestration run in Go.

### Deliverables

**Go services:**

- `services/go/internal/orchestrator/` — gRPC client to Python AI engines (Chronos, Risk, Compliance, Vision), sequential/parallel execution, timeout handling, circuit breaker, result caching
- `services/go/internal/debrief/` — Report generation: fetches timeline + risk + root cause from ClickHouse/Redis, compiles markdown/HTML reports
- `services/go/internal/investigation/` — Multi-stage pipeline: evidence collection, timeline reconstruction, root cause analysis, compliance audit, report compilation
- `services/go/internal/notifications/` — Alert dispatch (WebSocket push to frontend, configurable Slack/email later)

**Python reduced to:**

- `services/python/chronos/` — Prediction engine (forecast feature extraction, baseline forecaster, scenario generator)
- `services/python/vision/` — CV pipeline (YOLO detection, tracking, PPE analysis) — real model integration
- `services/python/risk/` — Risk rules, scoring calculator
- `services/python/compliance/` — Compliance rules, regulation KB
- `services/python/rag/` — Document retrieval, embeddings
- Python runs as stateless gRPC servers behind Go orchestrator. No HTTP routes, no WebSocket, no state.

### Infrastructure

- gRPC for all Go ↔ Python communication
- Python containers become `sidecar`-style services (no public ports except gRPC health)

### What Python sheds

- `intelligence/` module (orchestration moves to Go)
- `debrief/` module
- `investigation/` module
- `api/` module (all HTTP routes)
- `middleware/` module
- `main.py` (FastAPI app) — replaced by minimal gRPC server
- `intelligence.yaml` — replaced by Go-side config

### Verify

- `docker compose down --rmi all && docker compose up` — Python runs as gRPC server, Go orchestrator calls it, frontend works end-to-end
- Debrief reports contain real data from ClickHouse (not hardcoded)
- Investigation pipeline returns data-driven results
- No Python process listens on port 8000 (no FastAPI)
- Request path: Browser → Go Gateway → Go Core → (gRPC) → Python AI

---

## Phase 6: Frontend Completion

**Goal:** Every route functional, stores properly wired, tests in place, unused deps removed.

### Deliverables

- **Routes (build 6 stubs):**
  - `/dashboard` — High-level KPIs, system health, recent alerts
  - `/plant-map` — Full-screen 3D plant twin (Three.js / R3F)
  - `/reports` — Debrief report list, viewer, export
  - `/settings` — Simulation controls, config toggles
  - `/simulation` — Dedicated simulation control panel
  - `/knowledge-graph` — Interactive hazard graph (Neo4j visualization via @xyflow/react or custom)
- **Store refactor:**
  - `investigationStore` — Properly typed, owns its API calls via TanStack Query, removes `any` types
  - `debriefStore` — Same treatment, connects to Go debrief API
- **Integrate TanStack React Query** — Replace inline `fetch()` calls across all pages with `useQuery`/`useMutation`
- **Init shadcn/ui** — `npx shadcn@latest init` installs `lib/utils.ts` + base `ui/` components (Button, Card, Dialog, etc.); migrate existing inline styles
- **Remove unused deps:** `@xyflow/react` (if unused after knowledge-graph eval), double-check others
- **Tests:**
  - Store tests (Zustand store behaviour with Vitest)
  - Component tests (render + state coverage for top 10 components)
  - Service tests (api.ts with MSW or nock)

### Verify

- All 9 routes render without errors
- `pnpm run build` succeeds
- `pnpm run lint` passes
- Test coverage >40% for stores and services
- No `any` types in stores
- shadcn components work end-to-end

---

## Phase 7: Production Hardening

**Goal:** Cloud-ready deployment on AWS ECS/EKS with full observability, IaC, and security.

### Deliverables

**Observability:**

- Prometheus metrics: Go (HTTP latency, WS connections, gRPC calls), Scala (Kafka lag, stream throughput), Python (model inference latency)
- Grafana dashboards: per-service SLO dashboard, end-to-end latency waterfall
- Loki: structured log aggregation (all services emit JSON logs)
- Tempo: distributed tracing across Go → gRPC → Python and Go → Kafka → Scala

**Infrastructure as Code:**

- Terraform or Pulumi: VPC, subnets, ECS/EKS cluster, ALB, RDS (if needed), ElastiCache (Redis), MSK (Kafka), EC2 for ClickHouse
- GitHub Actions deploy workflow: build → push ECR → deploy ECS service

**Security:**

- Secrets: AWS Secrets Manager (DB creds, API keys, JWT secret)
- Containers: non-root user, read-only root FS, no shell
- Network: VPC private subnets for services, ALB in public
- CSP headers on NGINX / Go gateway

**Load Testing:**

- k6: spike test (1000 concurrent WS connections), endurance test (24h steady state)
- Measure p50/p95/p99 for API, WS, gRPC, Kafka, ClickHouse queries

### Verify

- `make deploy` pushes all containers to ECR and updates ECS services
- Grafana dashboards show live data within 30s of deploy
- Load test completes with <5% error rate and p99 < 500ms for API
- `docker compose up` still works for local development
- No placeholder secrets in any config file

---

# Current Audit

## Backend

| Module | Status |
|----------|--------|
| World | Complete |
| Timeline | Complete |
| Simulation | Complete |
| Risk | Complete |
| Planner | Complete |
| Compliance | Complete |
| Vision | Partial |
| Debrief | Partial |
| Investigation | Partial |

---

## Frontend

| Area | Status |
|-------|--------|
| Components | Complete |
| Routes | Partial |
| Stores | Partial |
| Tests | Stub |

---

# Success Criteria

The migration is complete when:

- Python contains only ML services.
- Go owns all platform functionality.
- Scala owns all event streaming.
- Protocol Buffers define every service contract.
- Kafka becomes the single event backbone.
- Every service is independently deployable.
- All services expose production health checks.
- Full observability is available.
- Zero breaking API changes occur during migration.

---

# Future Work

After migration completes:

- Sentinel Architecture Specification
- Data Contracts RFC
- Event Flow Specification
- Deployment Guide
- Operations Handbook
- ADR Repository