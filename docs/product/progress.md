# Sentinel — Progress

## Goal
Complete the Sentinel platform by migrating non-core Python backend to Go/Scala, with Python only for ML, and get the app running. Next focus: **AI-Powered Industrial Safety Intelligence** — multi-agent compound risk detection with RAG over OISD/Factory Act regulations.

## Migration Strategy: Strangler Fig
Incremental module-by-module replacement — Go gateway front-ends Python, native handlers absorb endpoints one at a time.

---

## Phase 0 — Scaffolding ✅
| Deliverable | Files |
|---|---|
| Go module (`services/go/`) with `cmd/gateway`, `cmd/core` | `services/go/go.mod`, `cmd/gateway/main.go`, `cmd/core/main.go` |
| Scala sbt project (4 sub-projects: common, streams, cep, sink) | `services/scala/build.sbt` |
| Protobuf contracts (6 .proto + buf config, java options) | `contracts/proto/*.proto`, `buf.yaml`, `buf.gen.yaml` |
| Docker Compose with all 12+ services | `docker-compose.yml` |
| Makefile with build/test/lint + proto-java target | `Makefile` |
| CI/CD set to `workflow_dispatch` only | `.github/workflows/ci.yml` |

## Phase 1 — Gateway (Strangler Fig Facade) ✅
| Sub-phase | Deliverable | Tests |
|---|---|---|
| **1a** | Go gateway: reverse proxy to Python, health endpoints, graceful shutdown | 4 |
| **1b** | WebSocket proxy with path rewrite `/ws/` → `/api/v1/ws/` | 5 |
| **1c** | System endpoints (`/version`, `/status`), middleware (CORS, rate-limit, request-id) | 12 |
| **1d** | Auth middleware (stub: anonymous→viewer, bearer→admin), nginx routes to gateway | 15 |

### Python cleanup (Phase 1c–1d)
| Deleted | Reason |
|---|---|
| `backend/system/api/routes.py` | /version + /status now served by Go gateway |
| `backend/middleware/{rate_limit,request_id,logging}.py` | Handled by Go gateway middleware chain |

## Phase 2 — World Engine & Timeline ✅
| Sub-phase | Deliverable | Tests |
|---|---|---|
| **2a** | Go world entity models (17 types), enums, builder, factory | 4 |
| **2b** | SnapshotStore (versioned, retention), DiffEngine, gRPC WorldService | 7 |
| **2c** | EventBus, Simulator, Hub (WS client mgmt, broadcast diffs) | 5 |
| **2d** | Timeline engine: InMemoryStore, gRPC TimelineService | 8 |
| **2e** | RedisSnapshotStore + ClickHouseTimelineStore (graceful degrade), native `/ws/world-state` | 4 |

### Python cleanup (Phase 2a–2e)
| Deleted | Reason |
|---|---|
| `backend/world/{builder,manager,registry,routes,sample_data,tests}/` | World state managed by Go core |
| `backend/world_state/{builder,diff,manager,routes,schemas,tests,websocket}/` | Snapshots served by Go core |
| `backend/simulator/` (10 files) | Tick-loop, event bus, hub in Go core |
| `backend/timeline/` (9 of 11 files) | Timeline store + gRPC in Go core |

| Kept | Reason |
|---|---|
| `backend/world/models/` (4 files) | Entity types imported by chronos, compliance, risk, planner |
| `backend/world_state/snapshot/models.py` | WorldState model imported by all ML modules |
| `backend/timeline/engine/core.py` (stub) | TimelineEngine singleton imported by ML modules |
| `backend/timeline/timeline/entry.py` (stub) | TimelineEntry model imported by ML module tests |
| `backend/intelligence/contracts/events.py` | SimulationEvent moved from simulator |

## Phase 3 — Platform Services ✅
| Sub-phase | Module | Status |
|---|---|---|
| **3a** | Workers — CRUD, live tracking, gRPC WorkerService, REST handlers in gateway | ✅ Done |
| **3b** | Permits (hot work, confined space, PTW lifecycle) | ✅ Done |
| **3c** | Access control (zones, badges, restrictions) | ✅ Done |
| **3d** | Shift management | ✅ Done |

## Phase 4 — Safety & Intelligence
| Module | Status |
|---|---|
| Risk engine (hazard graph, scoring, zone risk) | Pending |
| Chronos (predictive analytics via Python ML) | Pending |
| Compliance (violations, audit trail) | Pending |
| Planner (evacuation, rescue path planning) | Pending |

## Phase 5 — Vision & Edge
| Module | Status |
|---|---|
| PPE detection (Python vision) | Pending |
| Camera integration (RTSP ingest) | Pending |
| Edge device management | Pending |

## Phase 6 — Scala Streaming Pipeline ✅
| Sub-phase | Module | Status |
|---|---|---|
| **6a** | Foundation — shared `common` lib, protobuf Java codegen, Config/Serde/ClickHouse ZIO layers | ✅ Done |
| **6b** | Go Kafka publisher — world sim publishes diffs to Kafka `raw-events` | ✅ Done |
| **6c** | Kafka event streams — consume raw-events, JSON parse/enrich, produce to `enriched-events` | ✅ Done |
| **6d** | ClickHouse sink — consume enriched-events, init schema, insert rows | ✅ Done |
| **6e** | CEP — consume enriched-events, evaluate rules (missing_version, unknown_source, null_payload), produce alerts | ✅ Done |

## Phase 7 — AI-Powered Industrial Safety Intelligence 🥇
Multi-agent compound risk detection — the core differentiator for hackathon evaluation.

| Agent / Module | Status |
|---|---|
| **Gas Sensor Agent** — real-time gas leak detection, concentration tracking, threshold alerting | Pending |
| **Work Permit Agent** — hot work, confined space PTW lifecycle, zone overlap validation | Pending |
| **Shift Agent** — shift changeover tracking, personnel location, handover gaps | Pending |
| **Correlation Layer** — compound risk scoring across agent outputs, temporal windowing | Pending |
| **RAG Agent** — OISD / Factory Act document ingestion, incident pattern retrieval | Pending |
| **Alert Engine** — priority-queued alerts, multi-channel dispatch | Pending |
| **Demo Simulator** — synthetic IoT time-series + mock permit logs + incident corpus | Pending |

### Why This Wins
- **Perfect for agentic AI** — multi-agent architecture maps naturally to compound risk detection
- **Achievable "wow" moment** — demo: gas sensor + hot work permit + shift changeover = high risk flagged 3 hours before threshold
- **Data is simulatable** — synthetic IoT time-series + mock permit logs + small incident corpus
- **Technical depth** — compound risk detection accuracy, false negative reduction, prediction lead time are measurable
- **RAG adds regulatory layer** — OISD/Factory Act doc retrieval without extra effort

## Phase 8 — Production Polish
| Feature | Status |
|---|---|
| ClickHouse production schema | Pending |
| Redis caching layer | Pending |
| Monitoring (Prometheus/Grafana dashboards) | Pending |
| Load testing | Pending |
| Documentation | Pending |

---

## Test Inventory

### Unit tests (`services/go/internal/...`)
| Package | Files | Count | What's tested |
|---|---|---|---|
| `cmd/gateway` | `main_test.go` | 5 | Health, WS proxy, system endpoints, middleware integration |
| `internal/middleware` | `auth_test.go`, `cors_test.go`, `ratelimit_test.go`, `requestid_test.go` | 8 | Auth stubs, CORS preflight, per-IP rate limiting, request ID propagation |
| `internal/system` | `handler_test.go` | 2 | Version/status response format |
| `internal/world` | `world_test.go`, `eventbus_test.go` | 16 | Models, builder, snapshot store, diff engine, gRPC service, event bus, simulator, hub |
| `internal/timeline` | `timeline_test.go` | 8 | Store CRUD, query filtering, pagination, retention, gRPC service |
| `internal/worker` | `worker_test.go` | 3 | Store CRUD, list, gRPC service |
| `internal/infra` | `infra_test.go` | 4 | Redis store, ClickHouse store (both in-memory fallback) |

### Integration tests (`services/go/tests/...`)
| Package | Files | Count | What's tested |
|---|---|---|---|
| `cmd/gateway` | `gateway_test.go` | 2 | Health endpoint, upstream proxy |
| `internal/world` | `world_test.go` | 10 | State content, snapshot ops, diff, gRPC service, bus, simulator, builder |
| `internal/timeline` | `timeline_test.go` | 5 | Record/query limit, replay, gRPC service, entity filter |
| `internal/infra` | `infra_test.go` | 4 | Redis fallback, list, ClickHouse fallback, query |

**Total: 59 Go tests (46 unit + 13 integration)** — all passing, `go vet` clean. Scala: 4 sub-projects compile clean, test clean.

---

## Architecture

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
               │ Python  │  │  │  core  │  gRPC  │  nats?   │
               │ backend │  │  │  :9000 │◄──────►│  Kafka   │
               │ :8000   │  │  └───┬────┘        │  :9092   │
               └─────────┘  │      │             └────┬─────┘
                            │      │ raw-events       │
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

**Gateway middleware chain**: RateLimiter → CORS → RequestID → Auth → Logging → mux

**Data stores**: ClickHouse (time-series events), Redis (live state), Neo4j (hazard graph), Qdrant (vectors) — all in docker-compose.

---

## Tech Stack

| Component | Language | Role |
|---|---|---|
| Gateway | Go 1.26.3 | Reverse proxy, WS, auth, middleware |
| Core | Go 1.26.3 | World engine, gRPC services, Kafka publisher |
| Streams/Sink/CEP | Scala 3.8.4 / sbt 1.12.13 | Kafka consumers, enrichment, ClickHouse writes, alert rules |
| ML/AI | Python 3.10 + FastAPI | Chronos (prediction), Risk, Compliance, Vision, Intelligence |
| Persistence | ClickHouse, Redis, Neo4j, Qdrant | Time-series, live state, hazard graph, vectors |
| Messaging | Kafka (segmentio/kafka-go, zio-kafka) | Event pipeline |

---

## Key Decisions

| Decision | Rationale |
|---|---|
| Strangler Fig pattern | Zero-downtime incremental migration |
| Frontend always talks to Go gateway | Single entry point; gateway proxies Python or serves natively |
| WS path rewrite `/ws/` → `/api/v1/ws/` | Frontend connects to `/ws/vision/`, gateway forwards to Python |
| `httputil.ReverseProxy` for both REST and WS | Handles Upgrade header natively in Go 1.22+ |
| Scala services are Kafka consumers (no gRPC) | Decoupled async pipeline; Go core publishes, Scala services consume |
| `KAFKA_BROKER` env var for all Kafka connections | Single config point across Go and Scala |
| Proto files include `java_multiple_files` + `java_package` | Enables clean Java class generation for Scala; harmless for Go/Python/TS |
| ZIO layers for Config/ClickHouse/KafkaProducer | ZIO 2 + zio-kafka provide structured concurrency and resource safety |
| CEP rules are sealed trait with per-event evaluation | Extensible for future sliding-window/stateful rules |
| ClickHouse schema created on sink startup | Self-bootstrapping; no manual DDL needed |
