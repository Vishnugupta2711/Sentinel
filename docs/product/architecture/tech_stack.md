# Sentinel Technology Stack

Sentinel is built on a modern, ultra-low-latency, containerized technology stack designed for enterprise scalability and rigorous real-time AI processing.

## Frontend: Mission Control
- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **State Management:** Zustand (for transient state), Context API
- **Real-Time:** WebSockets for millisecond-latency UI updates
- **Visualization:** Three.js / React Three Fiber (3D Plant Mapping), D3.js (Metrics)
- **Styling:** TailwindCSS with strict Palantir/Gotham-inspired design tokens
- **Build:** Alpine Linux standalone container optimized for edge deployment

## Backend: Sentinel API & Engines
- **Framework:** FastAPI (Python 3.10+)
- **Architecture:** Domain-Driven Design (DDD), SOLID, heavily modularized
- **Dependency Injection:** Native Python DI container ensuring complete testability
- **Data Validation:** Pydantic V2
- **Logging:** Structlog (JSON structured logs for ELK/Datadog ingestion)

## AI & Intelligence Engines
- **Vision Engine:** Deep SORT, YOLOv8/v10 (conceptualized integrations), ByteTrack for multi-object tracking.
- **Chronos Prediction Engine:** Generative trajectory forecasting and physics-informed hazard trajectory mapping.
- **Compound Risk Engine:** Heuristic and machine-learning-based risk multipliers operating on the Hazard Graph.
- **Counterfactual Planner:** Decision tree and simulation-based scenario analysis for optimal emergency response.
- **Compliance Engine:** Rules-based validator executing OISD/OSHA standard checks against live World State.

## Infrastructure & Persistence
- **Message Broker:** Kafka (Confluent 7.4) & Zookeeper – The backbone of the Event-Driven Architecture.
- **Primary Database:** PostgreSQL 15 – Relational storage for configurations, audit logs, and compliance records.
- **In-Memory World State:** Redis 7 – Ultra-fast volatile state representing the exact position and status of all entities.
- **Hazard Graph:** Neo4j 5 – Graph database mapping relationships between workers, zones, PPE, and environmental hazards.
- **Vector Search:** Qdrant – High-performance vector database for semantic logging and anomaly retrieval.

## Cloud & Deployment (Ops)
- **Containerization:** Docker & Docker Compose (10 interconnected services)
- **Proxy & Edge:** NGINX (Reverse proxy, Load Balancing, WebSocket termination)
- **Monitoring:** Prometheus & Grafana (Real-time hardware, API, and algorithmic latency tracking)
- **CI/CD:** GitHub Actions (Automated linting, testing, and SSH deployment to AWS EC2)
- **Environment:** AWS VPC, Application Load Balancers, Target Groups
