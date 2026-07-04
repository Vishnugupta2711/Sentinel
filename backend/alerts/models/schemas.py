from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now


class AlertPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertStatus(str, Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class AlertChannel(str, Enum):
    WEBSOCKET = "WEBSOCKET"
    DASHBOARD = "DASHBOARD"
    SIREN = "SIREN"
    SMS = "SMS"
    EMAIL = "EMAIL"


class Alert(BaseModel):
    alert_id: str = Field(default_factory=generate_uuid)
    title: str
    description: str
    priority: AlertPriority
    status: AlertStatus = AlertStatus.NEW
    source_agent: str
    source_signals: List[str] = Field(default_factory=list)
    zone_id: Optional[str] = None
    correlation_id: Optional[str] = None
    score: float = 0.0
    channels: List[AlertChannel] = Field(default_factory=lambda: [AlertChannel.DASHBOARD])
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    ttl_seconds: int = 3600
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))


class AlertQueue(BaseModel):
    queue_id: str = Field(default_factory=generate_uuid)
    alerts: List[Alert] = Field(default_factory=list)
    priority_counts: Dict[str, int] = Field(default_factory=lambda: {
        "EMERGENCY": 0, "CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0
    })
