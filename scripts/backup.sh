#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Sentinel — PostgreSQL Backup Script
# Run via cron: 0 2 * * * /opt/sentinel/scripts/backup.sh
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────
BACKUP_DIR="${BACKUP_DIR:-/opt/sentinel/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="sentinel-postgres"
DB_USER="${POSTGRES_USER:-sentinel}"
DB_NAME="${POSTGRES_DB:-sentinel}"

# ─── Colors ──────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[BACKUP]${NC} $(date '+%Y-%m-%d %H:%M:%S') — $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') — $1"; }
fail() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') — $1" >&2; exit 1; }

# ─── Create Backup Directory ─────────────────────────────────
mkdir -p "${BACKUP_DIR}/postgres"
mkdir -p "${BACKUP_DIR}/config"
mkdir -p "${BACKUP_DIR}/redis"

# ═══════════════════════════════════════════════════════════════
# PostgreSQL Backup
# ═══════════════════════════════════════════════════════════════
log "Starting PostgreSQL backup..."

PG_BACKUP_FILE="${BACKUP_DIR}/postgres/sentinel_${TIMESTAMP}.sql.gz"

docker exec "${CONTAINER_NAME}" pg_dump \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --format=custom \
    --compress=9 \
    --verbose \
    2>/dev/null | gzip > "${PG_BACKUP_FILE}" || fail "PostgreSQL backup failed"

PG_SIZE=$(du -sh "${PG_BACKUP_FILE}" | cut -f1)
log "PostgreSQL backup complete: ${PG_BACKUP_FILE} (${PG_SIZE})"

# ═══════════════════════════════════════════════════════════════
# Redis Backup (trigger RDB snapshot)
# ═══════════════════════════════════════════════════════════════
log "Starting Redis backup..."

docker exec sentinel-redis redis-cli BGSAVE >/dev/null 2>&1 || warn "Redis BGSAVE skipped"
sleep 2

REDIS_BACKUP_FILE="${BACKUP_DIR}/redis/dump_${TIMESTAMP}.rdb"
docker cp sentinel-redis:/data/dump.rdb "${REDIS_BACKUP_FILE}" 2>/dev/null || warn "Redis backup skipped (no dump.rdb)"

if [ -f "${REDIS_BACKUP_FILE}" ]; then
    REDIS_SIZE=$(du -sh "${REDIS_BACKUP_FILE}" | cut -f1)
    log "Redis backup complete: ${REDIS_BACKUP_FILE} (${REDIS_SIZE})"
fi

# ═══════════════════════════════════════════════════════════════
# Configuration Backup
# ═══════════════════════════════════════════════════════════════
log "Backing up configuration files..."

CONFIG_BACKUP="${BACKUP_DIR}/config/config_${TIMESTAMP}.tar.gz"
tar -czf "${CONFIG_BACKUP}" \
    -C "$(dirname "$0")/.." \
    docker-compose.yml \
    .env \
    nginx/nginx.conf \
    prometheus/prometheus.yml \
    prometheus/alerts.yml \
    grafana/provisioning \
    2>/dev/null || warn "Some config files missing"

log "Configuration backup complete: ${CONFIG_BACKUP}"

# ═══════════════════════════════════════════════════════════════
# Retention Cleanup
# ═══════════════════════════════════════════════════════════════
log "Cleaning backups older than ${RETENTION_DAYS} days..."

find "${BACKUP_DIR}" -type f -mtime +${RETENTION_DAYS} -delete 2>/dev/null
REMAINING=$(find "${BACKUP_DIR}" -type f | wc -l | tr -d ' ')

log "Backup complete. ${REMAINING} backup files retained."
log "═══════════════════════════════════════════════════════════"
