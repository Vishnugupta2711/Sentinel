#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Sentinel — Health Check Script
# Quick verification that all services are operational
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local cmd="$2"
    local result

    if result=$(eval "$cmd" 2>/dev/null); then
        echo -e "  ${GREEN}✓${NC} ${name}"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗${NC} ${name}"
        FAIL=$((FAIL + 1))
    fi
}

warn_check() {
    local name="$1"
    local cmd="$2"

    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} ${name}"
        PASS=$((PASS + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} ${name} (non-critical)"
        WARN=$((WARN + 1))
    fi
}

echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${CYAN}  SENTINEL — System Health Check${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""

# ─── Docker Containers ───────────────────────────────────────
echo -e "${BOLD}Docker Containers:${NC}"
check "Backend running"   "docker ps --format '{{.Names}}' | grep -q sentinel-backend"
check "Frontend running"  "docker ps --format '{{.Names}}' | grep -q sentinel-frontend"
check "NGINX running"     "docker ps --format '{{.Names}}' | grep -q sentinel-nginx"
check "Redis running"     "docker ps --format '{{.Names}}' | grep -q sentinel-redis"
check "PostgreSQL running" "docker ps --format '{{.Names}}' | grep -q sentinel-postgres"
check "Kafka running"     "docker ps --format '{{.Names}}' | grep -q sentinel-kafka"
check "Zookeeper running" "docker ps --format '{{.Names}}' | grep -q sentinel-zookeeper"
warn_check "Neo4j running"     "docker ps --format '{{.Names}}' | grep -q sentinel-neo4j"
warn_check "Qdrant running"    "docker ps --format '{{.Names}}' | grep -q sentinel-qdrant"
warn_check "Prometheus running" "docker ps --format '{{.Names}}' | grep -q sentinel-prometheus"
warn_check "Grafana running"    "docker ps --format '{{.Names}}' | grep -q sentinel-grafana"
echo ""

# ─── HTTP Endpoints ──────────────────────────────────────────
echo -e "${BOLD}HTTP Endpoints:${NC}"
check "Backend Health"    "curl -sf http://localhost:8000/api/v1/health/live"
check "Backend API Status" "curl -sf http://localhost:8000/api/v1/system/status"
check "Swagger Docs"      "curl -sf http://localhost:8000/docs"
check "Prometheus Metrics" "curl -sf http://localhost:8000/metrics"
check "NGINX Proxy"       "curl -sf http://localhost:80/nginx-health"
warn_check "Frontend"         "curl -sf http://localhost:3000/"
warn_check "Prometheus UI"    "curl -sf http://localhost:9090/-/healthy"
warn_check "Grafana UI"       "curl -sf http://localhost:3001/api/health"
echo ""

# ─── Summary ─────────────────────────────────────────────────
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
TOTAL=$((PASS + FAIL + WARN))
echo -e "  Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}, ${YELLOW}${WARN} warnings${NC} / ${TOTAL} total"

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}${BOLD}✓ SENTINEL IS OPERATIONAL${NC}"
else
    echo -e "  ${RED}${BOLD}✗ SENTINEL HAS FAILURES — INVESTIGATE IMMEDIATELY${NC}"
fi
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════${NC}"
echo ""

exit $FAIL
