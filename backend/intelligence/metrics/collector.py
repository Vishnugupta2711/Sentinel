import threading
from typing import Dict, Any
from utils.datetime import format_iso, utc_now

class MetricsCollector:
    """In-memory tracking of module execution metrics."""
    
    def __init__(self):
        self._lock = threading.Lock()
        # Structure: {module_name: {"executions": int, "errors": int, "total_latency": float, "last_executed": str}}
        self._metrics: Dict[str, Dict[str, Any]] = {}

    def record_execution(self, module_name: str, latency_ms: float, success: bool) -> None:
        """Records an execution event."""
        with self._lock:
            if module_name not in self._metrics:
                self._metrics[module_name] = {
                    "executions": 0,
                    "errors": 0,
                    "total_latency_ms": 0.0,
                    "last_executed": None
                }
            
            m = self._metrics[module_name]
            m["executions"] += 1
            if not success:
                m["errors"] += 1
            m["total_latency_ms"] += latency_ms
            m["last_executed"] = format_iso(utc_now())

    def get_metrics(self) -> Dict[str, Any]:
        """Returns computed metrics."""
        with self._lock:
            result = {}
            for name, m in self._metrics.items():
                execs = m["executions"]
                avg_latency = m["total_latency_ms"] / execs if execs > 0 else 0.0
                success_rate = ((execs - m["errors"]) / execs * 100) if execs > 0 else 100.0
                
                result[name] = {
                    "executions": execs,
                    "errors": m["errors"],
                    "average_latency_ms": round(avg_latency, 2),
                    "success_rate_percent": round(success_rate, 2),
                    "last_executed": m["last_executed"]
                }
            return result
