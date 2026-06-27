# Sentinel Hackathon Judge Guide

Welcome, Judges! 

**Sentinel** is an autonomous AI safety platform for industrial plants. This guide explains how to interact with the project and what to look for when judging our submission.

## How to View the Demo
We built a specialized **"Guided Demo Mode"** just for you.

1. Open `http://localhost:3000` (or the deployed URL provided by the team).
2. Click the **Guided Demo Toggle** in the top right corner of the screen.
3. Click **Start Guided Demo**.
4. The platform will automatically walk you through a simulated timeline of a catastrophic failure, and how Sentinel prevents it using AI.
5. You can **Pause** the demo at any time using the Spacebar or the Pause button in the UI to inspect the underlying data.

## Judging Criteria

When reviewing Sentinel, please consider our execution across these three axes:

### 1. Innovation (The AI Engine)
Sentinel doesn't just display sensor data. It acts as an autonomous reasoning agent. Look at the **Chronos Forecaster**, which uses our $O(S)$ feature extractor to predict state deviations 30 minutes in advance with a latency of less than 1 millisecond.

### 2. User Experience (The Interactive Twin)
Traditional industrial software is slow and ugly. We built Sentinel using Next.js, React 18, and WebGL to render a beautiful, 60fps digital twin of the plant. Look out for the smooth micro-animations and "Hero Moments" during the demo.

### 3. Enterprise Readiness
Sentinel is not a duct-tape hack. It is hardened for production:
- We enforce non-root user execution in Docker.
- We utilize `uvloop` for ultra-high-throughput websockets.
- We implement CSP headers via Nginx.
- We ship with Prometheus metrics enabled out-of-the-box.

We hope you enjoy the product!
