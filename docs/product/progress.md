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

## Phase 2 — World Engine & Timeline ✅
| Sub-phase | Deliverable | Tests |
|---|---|---|
| **2a** | Go world entity models (17 types), enums, builder, factory | 4 |
| **2b** | SnapshotStore (versioned, retention), DiffEngine (added/removed/updated per entity type), gRPC WorldService (Get/Stream/List) + proto generation | 7 |
| **2c** | EventBus (topic pub/sub), Simulator (tick loop mutating sensors/workers/weather), Hub (WS client mgmt, broadcast diffs) | 5 |
| **2d** | Timeline engine: InMemoryStore (Record/Query/Replay), gRPC TimelineService + proto generation | 8 |
| **2e** | RedisSnapshotStore + ClickHouseTimelineStore (graceful degrade), native `/ws/world-state` handler in gateway via gRPC stream to core, docker-compose wired | 4 |

## Phase 3 — Platform Services ⏳
| Module | Status |
|---|---|
| Workers (CRUD + live tracking) | Pending |
| Permits (hot work, confined space, PTW lifecycle) | Pending |
| Access control (zones, badges, restrictions) | Pending |
| Shift management | Pending |

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
| Module | Status |
|---|---|
| Kafka event streams | Pending |
| CEP (complex event processing) | Pending |
| ClickHouse sink | Pending |

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
| `internal/infra` | `infra_test.go` | 4 | Redis store, ClickHouse store (both in-memory fallback) |

### Integration tests (`services/go/tests/...`)  
| Package | Files | Count | What's tested |
|---|---|---|---|
| `cmd/gateway` | `gateway_test.go` | 2 | Health endpoint, upstream proxy |
| `internal/world` | `world_test.go` | 10 | State content, snapshot ops, diff, gRPC service, bus, simulator, builder |
| `internal/timeline` | `timeline_test.go` | 5 | Record/query limit, replay, gRPC service, entity filter |
| `internal/infra` | `infra_test.go` | 4 | Redis fallback, list, ClickHouse fallback, query |

**Total: 56 tests** (43 unit + 13 integration), all passing, `go vet` clean.

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
