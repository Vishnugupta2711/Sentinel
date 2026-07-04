# Sentinel Edge-Based Deployment Architecture

## Overview
The Sentinel platform is designed for a highly distributed, edge-native deployment model. This ensures low latency, cost-efficiency, and leveraging specialized cloud providers for specific microservice workloads.

---

## 1. Frontend & API Gateway (Vercel)
- **Frontend (TypeScript/Next.js):** 
  - Deployed to Vercel's Edge Network for global CDN distribution, fast static asset delivery, and serverless React rendering.
- **Go Gateway (Go 1.26):** 
  - Deployed as Serverless/Edge Functions on Vercel. 
  - Handles lightweight middleware (Auth, CORS, Rate Limiting) at the edge, acting as the primary entry point for all API traffic before proxying to specialized backends.

## 2. Machine Learning & AI Intelligence (Hugging Face Spaces)
- **Python Backend (FastAPI):** 
  - Hosted on Hugging Face (HF) Spaces using Docker Spaces or Gradio Fast.
  - **Workloads:** Risk Engine, RAG Agent, Chronos, and Vision modules run here.
  - **Why:** Leverages HF's GPU infrastructure and proximity to model weights (e.g., Llama-3, custom vision models) for high-performance ML inference.

## 3. Streaming Data Pipeline (GitHub Actions)
- **Scala CEP & Sink (ZIO):** 
  - The Kafka consumers (streams, complex event processing, ClickHouse sink) are orchestrated via GitHub Actions.
  - **Architecture:** GitHub Actions can run scheduled jobs or continuous long-lived worker instances that consume from Kafka topics (`raw-events`), evaluate ZIO-based CEP rules, and insert enriched data into the remote ClickHouse instance.

## 4. Managed Persistence & Messaging (Serverless)
To support the edge architecture without managing VMs, the state layer relies on serverless data providers:
- **ClickHouse Cloud / Aiven:** Remote time-series database for historical event storage.
- **Upstash (Redis):** Serverless Redis for real-time live world state snapshots.
- **Upstash (Kafka) / Confluent Cloud:** Serverless Kafka broker for the `raw-events` and `enriched-events` event bus.
- **Qdrant Cloud:** Managed vector database for the RAG agent's regulatory knowledge base.
