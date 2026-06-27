import fs from 'fs';
import { execSync } from 'child_process';
import path from 'path';

const OUT_DIR = 'docs/product/diagrams';

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

const diagrams = {
  'system_architecture': `
graph TD
    subgraph UI[Mission Control Frontend]
        MC[Mission Control Core]
        RP[Risk Panel]
        PL[Planner]
        VP[Vision Panel]
    end
    
    subgraph BE[Sentinel Backend API]
        API[FastAPI Gateway]
        WS[WebSocket Manager]
    end
    
    subgraph Intelligence[AI Engines]
        VE[Vision Engine]
        CE[Compliance Engine]
        RE[Risk Engine]
        CH[Chronos Prediction]
        PE[Planner Engine]
    end
    
    subgraph Data[Data Persistence & State]
        PG[(PostgreSQL<br/>Audit/Config)]
        RD[(Redis<br/>World State)]
        NJ[(Neo4j<br/>Hazard Graph)]
        QD[(Qdrant<br/>Vectors)]
    end
    
    subgraph Bus[Message Broker]
        KF[Kafka Event Bus]
    end

    UI <-->|REST / WS| BE
    BE -->|Commands| Intelligence
    Intelligence -->|Events| KF
    KF -->|Stream| BE
    Intelligence <-->|Read/Write| Data
  `,
  
  'ai_pipeline': `
flowchart LR
    A[Raw Video/IoT Stream] --> B(Vision Engine)
    B -->|Detections| C{World State}
    C --> D(Compliance Engine)
    C --> E(Risk Engine)
    E --> F[Hazard Graph]
    F --> G(Chronos Predictor)
    G --> H(Counterfactual Planner)
    H --> I[Mitigation Strategy]
  `,

  'data_flow': `
flowchart LR
    Plant[Plant Sensors/Cameras] --> Sim[Simulator / Ingest]
    Sim --> EB[Event Bus]
    EB --> WS[(World State)]
    WS --> TL[Timeline Event Store]
    TL --> HG[(Hazard Graph)]
    HG --> Chronos[Chronos Engine]
    Chronos --> Risk[Risk Engine]
    Risk --> Plan[Planner]
    Plan --> MC[Mission Control]
  `,

  'seq_incident_prediction': `
sequenceDiagram
    autonumber
    participant VE as Vision Engine
    participant EB as Event Bus
    participant RE as Risk Engine
    participant CH as Chronos
    participant MC as Mission Control

    VE->>EB: Publish PPE Violation Event
    EB->>RE: Consume Event
    RE->>RE: Evaluate Compound Risk (Score: 85)
    RE->>CH: Request Trajectory Prediction
    CH-->>RE: Forecast: Severe Incident in 5m
    RE->>EB: Publish Critical Risk Alert
    EB->>MC: WebSocket Broadcast
    MC->>MC: Render Red Alert UI
  `,

  'world_state': `
stateDiagram-v2
    [*] --> Ingest
    Ingest --> ObjectTracking
    ObjectTracking --> SpatialMapping
    SpatialMapping --> RiskEvaluation
    RiskEvaluation --> [*]
  `,

  'hazard_graph': `
graph TD
    W[Worker: John] -- IN_ZONE --> Z[Zone: High Temp]
    W -- LACKS --> PPE[PPE: Hard Hat]
    Z -- HAS_HAZARD --> H[Hazard: Molten Metal]
    H -- INCREASES_RISK --> W
  `,

  'chronos': `
flowchart TD
    A[Current World State] --> B{Chronos Model}
    B --> C[Prediction t+1m]
    B --> D[Prediction t+5m]
    B --> E[Prediction t+15m]
    C --> F(Risk Scoring)
    D --> F
    E --> F
    F --> G[Future Risk Topology]
  `,

  'planner': `
flowchart LR
    A[Critical Risk Alert] --> B{Counterfactual Planner}
    B --> C[Option 1: Evacuate]
    B --> D[Option 2: Shutdown Machine]
    B --> E[Option 3: Dispatch Supervisor]
    C --> F(Simulate Impact)
    D --> F
    E --> F
    F --> G[Optimal Recommendation]
  `,

  'compliance': `
sequenceDiagram
    participant Rule as OISD Rule Engine
    participant WS as World State
    participant Audit as Audit Log

    WS->>Rule: State Update (Worker in Confined Space)
    Rule->>Rule: Check PTW (Permit to Work)
    Rule-->>WS: Invalid Permit Detected
    Rule->>Audit: Log Violation (CMP-102)
  `,

  'mission_control': `
graph TD
    A[Mission Control UI] --> B(3D Plant View)
    A --> C(Risk Matrix)
    A --> D(Compliance Status)
    A --> E(Timeline)
    
    B --> F[WebSocket Updates]
    C --> F
    D --> F
    E --> F
  `,

  'seq_emergency_response': `
sequenceDiagram
    participant Planner
    participant User
    participant Actuator

    Planner->>User: Recommend Emergency Shutdown (95% Success Prob)
    User->>Planner: Approve Action
    Planner->>Actuator: Send Shutdown Command
    Actuator-->>Planner: Confirmation
    Planner->>User: Action Executed Successfully
  `,
  
  'deployment': `
graph TD
    subgraph AWS VPC
        subgraph Public Subnet
            ALB[Application Load Balancer]
        end
        subgraph Private Subnet
            EKS[EKS Cluster]
            MSK[Kafka MSK]
            RDS[PostgreSQL]
            EC[ElastiCache Redis]
        end
    end
    Internet --> ALB
    ALB --> EKS
    EKS --> MSK
    EKS --> RDS
    EKS --> EC
  `
};

for (const [name, content] of Object.entries(diagrams)) {
    const mmdPath = path.join(OUT_DIR, `${name}.mmd`);
    const svgPath = path.join(OUT_DIR, `${name}.svg`);
    fs.writeFileSync(mmdPath, content.trim());
    console.log(`Generating ${svgPath}...`);
    try {
      execSync(`npx -y @mermaid-js/mermaid-cli -i ${mmdPath} -o ${svgPath} -t dark -b transparent`);
      console.log(`Success: ${name}`);
    } catch (e) {
      console.error(`Failed to generate ${name}`, e.message);
    }
}
