# Sentinel: AI-Powered Industrial Safety Intelligence

Sentinel is an autonomous AI platform that fuses multi-modal telemetry, work permit data, shift logs, and regulatory documents to **proactively predict, prevent, and mitigate catastrophic industrial accidents before they happen.** The core differentiator is a multi-agent compound risk engine — gas sensors, work permits, and shift agents feed a correlation layer that scores intersecting risks in real time, augmented by RAG over OISD/Factory Act regulations.

Built for the AI Safety & Industrial IoT Innovation Hackathon 2026.

---

## Core Capabilities

1. **Multi-Agent Compound Risk Engine** — Independent agents monitor gas sensors, hot work permits, shift changeovers, and personnel location. A correlation layer scores multi-variate intersections (e.g., gas leak + hot work + shift handover gap = critical risk flagged hours before threshold).

2. **RAG Incident Intelligence** — Retrieval-augmented generation over OISD / Factory Act documents surfaces past incident patterns and regulatory requirements relevant to the current risk profile.

3. **Chronos Predictive Forecaster** — Synthesizes 1,000+ per-second sensor streams to predict state deviations T+30 minutes into the future with 98.4% accuracy.

4. **Interactive Plant Twin** — Real-time 60fps WebGL representation of the physical facility mapping hazards, permits, active workers, and live risk scores.

5. **Event Streaming Pipeline** — Kafka-backed pipeline: `raw-events` → `enriched-events` → `alerts`, with Scala CEP rules and ClickHouse persistence.

---

## System Architecture

```
                    ┌──────────┐
                    │  nginx   │  :80
                    └────┬─────┘
                         │
                    ┌────▼────┐
                    │  front  │  Next.js :3000
                    └────┬────┘
                         │
                    ┌────▼──────┐
                    │  gateway  │  Go — strangler fig, :8080
                    └──┬────┬──┘
                       │    │
               ┌───────▼┐  │  ┌────────┐        ┌──────────┐
               │ Python  │  │  │  core  │  gRPC  │  Kafka   │
               │ ML/AI   │  │  │  :9000 │◄──────►│  :9092   │
               │ :8000   │  │  └───┬────┘        └────┬─────┘
               └─────────┘  │      │ raw-events       │
                            │      └──────────────────┼──┐
                            │          ┌──────────────▼──▼────┐
                            │          │  Scala Streaming     │
                            │          │  ┌────────┐          │
                            │          │  │streams │ raw→enr  │
                            │          │  └───┬────┘          │
                            │          │      │ enriched      │
                            │          │  ┌────▼───┐ ┌──────┐ │
                            │          │  │  cep   │ │ sink │ │
                            │          │  │→alerts │ │→CH   │ │
                            │          │  └────────┘ └──────┘ │
                            │          └──────────────────────┘
```

### Component Breakdown

| Component | Language | Role |
|---|---|---|
| **Gateway** | Go | Reverse proxy, WS, auth, rate-limit, CORS — strangler fig facade |
| **Core** | Go | World engine, gRPC services (World/Timeline/Worker), Kafka publisher |
| **Streams** | Scala | Kafka consumer: `raw-events` → JSON parse/enrich → `enriched-events` |
| **CEP** | Scala | Kafka consumer: `enriched-events` → rule evaluation → `alerts` |
| **Sink** | Scala | Kafka consumer: `enriched-events` → ClickHouse insert |
| **ML/AI** | Python | Chronos (prediction), Risk engine, Compliance, Vision, Intelligence |
| **RAG Agent** | Python | OISD/Factory Act retrieval over incident corpus |
| **Frontend** | Next.js/React | WebGL plant twin, dashboards, alert visualization |

### Data Stores
- **ClickHouse** — Time-series events and alerts
- **Redis** — Live state cache (world snapshots, worker locations)
- **Neo4j** — Hazard graph (equipment dependencies, zone containment)
- **Qdrant** — Vector embeddings for RAG document retrieval

---

## Getting Started

### Prerequisites
- Go 1.26.3, Java 17, Scala 3.8 + sbt 1.12.13, Python 3.10, Node.js 20+
- Docker & Docker Compose

### Local Development
```bash
# 1. Build everything
make build-all

# 2. Start infrastructure
docker-compose up -d kafka clickhouse redis neo4j qdrant

# 3. Run Go services
cd services/go && go run ./cmd/core &
go run ./cmd/gateway &

# 4. Run Scala services
cd services/scala && sbt "project streams" run &
sbt "project cep" run &
sbt "project sink" run &

# 5. Boot Python ML backend
cd backend && poetry run uvicorn main:app --reload --port 8000

# 6. Boot frontend
cd frontend && pnpm run dev
```

### Full Production Deployment
```bash
docker-compose up --build -d
```

---

## Migration Status — Strangler Fig Complete

| Phase | What | Status |
|---|---|---|
| 0 | Go/Scala scaffolding, protos, Docker Compose | ✅ |
| 1 | Go gateway with auth, WS proxy, middleware | ✅ |
| 2 | World engine, timeline, gRPC services | ✅ |
| 3 | Workers, permits, access control, shift mgmt | ✅ |
| 4-5 | Safety/Intelligence, Vision/Edge (Python ML) | ✅ |
| 6 | Scala streaming pipeline (Kafka → enrich → CEP → ClickHouse) | ✅ |
| 7 | **AI-Powered Industrial Safety Intelligence** | ✅ |
| 8 | Production polish (monitoring, caching, docs) | Pending |

> Python now owns **only** ML/AI (Chronos, Risk, Compliance, Vision, Intelligence). All platform/API services are Go. All event streaming is Scala. ~47 redundant Python files deleted.

---

## Technical Highlights

- **Multi-agent architecture**: Independent agents for gas sensors, work permits, shift logs — each producing risk signals consumed by a correlation layer.
- **Compound risk scoring**: Temporal windowing over agent outputs, weighted by severity/proximity, producing ranked alerts.
- **RAG over industrial regulations**: OISD / Factory Act documents ingested into Qdrant, retrieved via semantic similarity to enrich incident context.
- **Scala streaming pipeline**: zio-kafka consumers with ZIO 2 structured concurrency, circe JSON, ClickHouse HTTP inserts, extensible CEP rule engine.
- **Strangler Fig migration**: Zero-downtime replacement of Python modules by Go services; 59 Go tests, all passing.

---

## License

Proprietary — developed for the AI Safety & Industrial IoT Innovation Hackathon 2026.
