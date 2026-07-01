# Sentinel — Progress

## Goal
Complete the Sentinel platform by migrating non-core Python backend to Go/Scala, with Python only for ML, and get the app running.

## Migration Strategy: Strangler Fig
Incremental module-by-module replacement — Go gateway front-ends Python, native handlers absorb endpoints one at a time.

---

## Phase 0 — Scaffolding ✅
| Deliverable | Files |
|---|---|
| Go module (`services/go/`) with `cmd/gateway`, `cmd/core` | `services/go/go.mod`, `cmd/gateway/main.go`, `cmd/core/main.go` |
| Scala sbt project (3 sub-projects: streams, cep, sink) | `services/scala/build.sbt` |
| Protobuf contracts (5 .proto files + buf config) | `contracts/proto/*.proto`, `buf.yaml`, `buf.gen.yaml` |
| Docker Compose with all services | `docker-compose.yml` |
| Makefile with build/test/lint targets | `Makefile` |
| CI/CD (Go lint/build/test + Scala build/test + proto lint) | `.github/workflows/ci.yml` |
| CI restricted to `push: [main]` only | `.github/workflows/ci.yml` |

## Phase 1 — Gateway (Strangler Fig Facade) ✅
| Sub-phase | Deliverable | Tests |
|---|---|---|
| **1a** | Go gateway: reverse proxy to Python, health endpoints, graceful shutdown | 4 |
| **1b** | WebSocket proxy with path rewrite `/ws/` → `/api/v1/ws/` | 5 |
| **1c** | System endpoints (`/version`, `/status`), middleware (CORS, rate-limit, request-id) | 12 |
| **1d** | Auth middleware (stub: anonymous→viewer, bearer→admin), nginx routes to gateway | 15 |

### Python cleanup (Phase 1c)
| Deleted | Reason |
|---------|--------|
| `backend/system/api/routes.py` | /version + /status now served by Go gateway |
| `backend/middleware/{rate_limit,request_id,logging}.py` | Handled by Go gateway middleware chain |

## Phase 2 — World Engine & Timeline ✅
| Sub-phase | Deliverable | Tests |
|---|---|---|
| **2a** | Go world entity models (17 types), enums, builder, factory | 4 |
| **2b** | SnapshotStore (versioned, retention), DiffEngine (added/removed/updated per entity type), gRPC WorldService (Get/Stream/List) + proto generation | 7 |
| **2c** | EventBus (topic pub/sub), Simulator (tick loop mutating sensors/workers/weather), Hub (WS client mgmt, broadcast diffs) | 5 |
| **2d** | Timeline engine: InMemoryStore (Record/Query/Replay), gRPC TimelineService + proto generation | 8 |
| **2e** | RedisSnapshotStore + ClickHouseTimelineStore (graceful degrade), native `/ws/world-state` handler in gateway via gRPC stream to core, docker-compose wired | 4 |

### Python cleanup (Phase 2a–2d)
| Deleted | Reason |
|---------|--------|
| `backend/world/{builder,manager,registry,routes,sample_data,tests}/` | World state managed by Go core gRPC |
| `backend/world_state/{builder,diff,manager,routes,schemas,tests,websocket}/` | Snapshots served by Go core |
| `backend/simulator/` (10 files) | Tick-loop, event bus, hub in Go core |
| `backend/timeline/` (9 of 11 files) | Timeline store + gRPC in Go core |

| Kept | Reason |
|------|--------|
| `backend/world/models/` (4 files) | Entity types imported by chronos, compliance, risk, planner |
| `backend/world_state/snapshot/models.py` | WorldState model imported by all ML modules |
| `backend/timeline/engine/core.py` (stub) | TimelineEngine singleton imported by ML modules |
| `backend/timeline/timeline/entry.py` (stub) | TimelineEntry model imported by ML module tests |
| `backend/intelligence/contracts/events.py` | SimulationEvent moved from deleted simulator into intelligence |

## Phase 3 — Platform Services ⏳
| Sub-phase | Module | Status |
|---|---|---|
| **3a** | Workers — CRUD, live tracking, gRPC WorkerService, REST handlers in gateway | ✅ Done |
| **3b** | Permits (hot work, confined space, PTW lifecycle) | Pending |
| **3c** | Access control (zones, badges, restrictions) | Pending |
| **3d** | Shift management | Pending |

## Phase 4 — Safety & Intelligence ⏳
| Module | Status |
|---|---|
| Risk engine (hazard graph, scoring, zone risk) | Pending |
| Chronos (predictive analytics via Python ML) | Pending |
| Compliance (violations, audit trail) | Pending |
| Planner (evacuation, rescue path planning) | Pending |

## Phase 5 — Vision & Edge ⏳
| Module | Status |
|---|---|
| PPE detection (Python vision) | Pending |
| Camera integration (RTSP ingest) | Pending |
| Edge device management | Pending |

## Phase 6 — Scala Streaming ⏳
| Sub-phase | Module | Status |
|---|---|---|
| **6a** | Foundation — shared `common` lib, protobuf Java codegen, Config/Serde/ClickHouse ZIO layers, Kafka consumers wired | ✅ Done |
| **6b** | Go Kafka publisher — world sim publishes diffs to Kafka | Pending |
| **6c** | Kafka event streams — consume, deserialize, validate | Pending |
| **6d** | ClickHouse sink — persist enriched events | Pending |
| **6e** | CEP (complex event processing) — pattern rules, alerts | Pending |

## Phase 7 — Production Polish ⏳
| Feature | Status |
|---|---|
| ClickHouse production schema | Pending |
| Redis caching layer | Pending |
| Monitoring (Prometheus/Grafana dashboards) | Pending |
| Load testing | Pending |
| Docs | Pending |

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

**Total: 59 tests** (46 unit + 13 integration), all passing, `go vet` clean.

### Test locations
- `tests/go/` → symlink to `services/go/tests/`

---

## Architecture

```
                    ┌──────────┐
                    │  nginx   │  :80
                    └────┬─────┘
                    │    │
               ┌────▼┐ ┌▼──────────┐
               │front│ │  gateway  │  Go — strangler fig facade
               │ end  │ └──┬────┬──┘
               │:3000 │    │    │
               └──────┘    │    │
                    ┌──────▼┐  │  ┌───────┐
                    │backend│  │  │ core  │  Go — world engine
                    │Python │  │  │ :9000 │  gRPC
                    │:8000  │  │  └───────┘
                    └───────┘  │
                         ┌────▼────────┐
                         │ /ws/world-  │  native (served by gateway
                         │   state     │  via gRPC stream from core)
                         └─────────────┘
```

**Gateway middleware chain**: RateLimiter → CORS → RequestID → Auth → Logging → mux

**Data stores**: ClickHouse (timeline), Redis (live state), Neo4j (hazard graph), Qdrant (vectors) — all in docker-compose.

---

## Key Decisions

| Decision | Rationale |
|---|---|
| Strangler Fig pattern | Zero-downtime incremental migration |
| Frontend always talks to Go gateway | Single entry point; gateway proxies Python or serves natively |
| WS path rewrite `/ws/` → `/api/v1/ws/` | Frontend connects to `/ws/vision/`, gateway forwards to Python |
| `httputil.ReverseProxy` for both REST and WS | Handles Upgrade header natively in Go 1.22+ |
| `if: vars.CI_ENABLED != 'false'` on all CI jobs | Toggle all workflows via GitHub repo variable, no file edits |
| `services/go/tests/` for integration tests | Same Go module, can access `internal/` packages |
| Phase 3 services: new proto + Go internal package + gRPC in core + native HTTP in gateway | Follows the world/timeline pattern; REST ↔ gRPC translation done in gateway handlers |
| Worker store wraps world.SnapshotStore (seeded from initial snapshot) | Workers live inside PlantState; worker service reads/writes via snapshot-compatible store |
| Scala `common` sub-project with Java protobuf codegen | protoc generates Java classes from contracts/proto/*.proto into common/src/main/java/ |
| ZIO layers in common: AppConfig (env), ClickHouseClient (HTTP), ProtobufSerde (Kafka) | Each service depends on common; `make build-scala` regenerates Java protos first |
| Kafka topics follow naming convention: `raw-events` → `enriched-events` → `alerts` | streams consumes raw, produces enriched; cep/enriched → alerts; sink consumes enriched |
| Scala services are consumers only (no gRPC) | They read from Kafka topics produced by Go core (planned Phase 6b) |
