# Sentinel API Book

Welcome to the Sentinel Developer API. Sentinel operates using a decoupled, event-driven streaming architecture.

## 1. REST Endpoints (Control Plane)

### Health & Metrics
- **`GET /api/v1/health`**
  - Returns the orchestration health of the primary node.
- **`GET /api/v1/metrics`**
  - Prometheus-compatible metrics scraping endpoint.

### World State
- **`GET /api/v1/state/snapshot`**
  - Returns the latest static snapshot of the plant, including all active workers, sensors, and equipment.
- **`GET /api/v1/state/history?window=10m`**
  - Returns historical snapshots for analytics.

## 2. WebSocket Duplex Streams (Data Plane)

Sentinel streams intelligence via high-frequency multiplexed WebSocket channels.

### `ws://localhost:8000/api/v1/ws/stream`
The primary data firehose. Clients subscribe to topics by sending an initial handshake.

**Handshake Request:**
```json
{
  "type": "SUBSCRIBE",
  "channels": ["timeline", "chronos", "risk", "planner"]
}
```

**Payload Types:**

#### 1. Timeline Update
Dispatched continuously (1-10hz) as sensors stream new data.
```json
{
  "channel": "timeline",
  "data": {
    "version": 14205,
    "timestamp": "2026-06-26T12:04:01Z",
    "payload": { ... } // WorldState object
  }
}
```

#### 2. Risk Detection
Dispatched when the Compound Risk Engine flags a threshold violation.
```json
{
  "channel": "risk",
  "data": {
    "risk_id": "rsk_928374",
    "severity": "CRITICAL",
    "title": "Explosion Hazard",
    "affected_zones": ["zone_A", "zone_B"]
  }
}
```

#### 3. Counterfactual Recommendation
Dispatched milliseconds after a Risk is detected, offering the best mitigation strategy.
```json
{
  "channel": "planner",
  "data": {
    "plan_id": "pln_01928",
    "action": "EVACUATE_ZONE",
    "target": "zone_A",
    "projected_risk_reduction": 0.98
  }
}
```

## 3. Webhook Integrations
Sentinel can be configured to fire outgoing HTTP POST requests to Enterprise ERPs (e.g., SAP) when critical compliance violations occur. Configure webhook endpoints in `backend/config.py`.
