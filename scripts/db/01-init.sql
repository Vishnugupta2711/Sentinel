-- ═══════════════════════════════════════════════════════════════
-- Sentinel — PostgreSQL Initialization
-- This script runs on first container creation
-- ═══════════════════════════════════════════════════════════════

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ─── Audit Log Table ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    actor VARCHAR(255) DEFAULT 'system',
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

-- ─── System Events Table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL', 'EMERGENCY')),
    source VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_events_severity ON system_events(severity);
CREATE INDEX IF NOT EXISTS idx_system_events_source ON system_events(source);
CREATE INDEX IF NOT EXISTS idx_system_events_created_at ON system_events(created_at);

-- ─── Compliance Records ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS compliance_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    violation_id VARCHAR(50) UNIQUE NOT NULL,
    regulation VARCHAR(100) NOT NULL,
    section VARCHAR(50),
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'OPEN',
    issue TEXT NOT NULL,
    evidence JSONB DEFAULT '[]',
    recommendation TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_records(status);
CREATE INDEX IF NOT EXISTS idx_compliance_severity ON compliance_records(severity);

-- ─── Insert sentinel system boot record ─────────────────────
INSERT INTO audit_log (event_type, entity_type, actor, details)
VALUES ('SYSTEM_BOOT', 'platform', 'sentinel-init', '{"version": "1.0.0", "environment": "production"}');
