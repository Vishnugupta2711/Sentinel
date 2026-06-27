# Technical Whitepaper: The Sentinel Architecture

## Abstract
Sentinel represents a paradigm shift in industrial safety monitoring, moving away from post-hoc relational analytics towards predictive, state-driven inference. By conceptualizing the physical plant as a series of immutable `WorldState` snapshots, Sentinel applies deterministic and heuristic AI models to predict compound failures with ultra-low latency.

## 1. The World State Engine
Traditional architectures map telemetry to distinct database tables (e.g., `Sensors`, `Workers`, `Permits`). This creates an N+1 query problem when attempting to analyze spatial relationships. Sentinel solves this via the **World State Engine**.

At any given tick ($t$), Sentinel aggregates all disparate data into a single, immutable, serialized `WorldStateSnapshot`. This snapshot is zlib-compressed and appended to an in-memory `collections.deque` within the `TimelineStore`. This guarantees that AI engines can access $O(1)$ temporal slices of the entire facility's state without performing expensive SQL JOINs.

## 2. Intelligence Dispatcher & Concurrency
The AI pipeline relies on an asynchronous event loop powered by `uvloop`. The `IntelligenceDispatcher` categorizes models into two topological rings:

1. **Independent Ring**: Models with no data dependencies (Computer Vision, RAG Memory) execute concurrently via `asyncio.gather`.
2. **Dependent Ring**: Models that form a causal chain execute sequentially using tightly optimized Python delegates. 

Because feature extraction scales at $O(S)$ (where $S$ is the number of active sensors) rather than $O(S \times T)$ (where $T$ is the temporal window), the entire analytical chain (`Chronos` $\rightarrow$ `Risk` $\rightarrow$ `Planner` $\rightarrow$ `Compliance`) completes its critical path in under 0.5ms (p99).

## 3. The React/Three.js Data Plane
To visualize complex spatial risks, Sentinel bypasses standard DOM manipulation in favor of WebGL. 
The Next.js 14 frontend maintains a persistent WebSocket multiplexer. The duplex stream updates a localized `Zustand` store, which natively drives mutations in the `@react-three/fiber` canvas, achieving a consistent 60fps framerate even while plotting hundreds of dynamic hazards.

## 4. Enterprise Security Posture
Sentinel is orchestrated via Docker Compose (and Helm for Kubernetes). To meet stringent industrial infosec requirements:
- The Python application is executed under a restricted `appuser`.
- Network ingress is terminated at an Nginx proxy enforcing strict Content Security Policies (CSP) and preventing MIME-sniffing.
- Internal telemetry is continuously scraped by Prometheus for operational observability.
