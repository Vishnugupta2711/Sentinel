from enum import Enum
from typing import Dict, Any, List
import threading
from utils.datetime import format_iso, utc_now

class ExecutionStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class StateManager:
    """Tracks the current execution state of the pipeline."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.status: ExecutionStatus = ExecutionStatus.IDLE
        self.current_context_id: str | None = None
        self.start_time: str | None = None
        self.end_time: str | None = None
        
        # History of recent pipeline runs
        self._history: List[Dict[str, Any]] = []

    def start_execution(self, request_id: str):
        with self._lock:
            self.status = ExecutionStatus.RUNNING
            self.current_context_id = request_id
            self.start_time = format_iso(utc_now())
            self.end_time = None

    def finish_execution(self, success: bool, details: Dict[str, Any] = None):
        with self._lock:
            self.status = ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
            self.end_time = format_iso(utc_now())
            
            # Record in history
            self._history.append({
                "request_id": self.current_context_id,
                "status": self.status.value,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "details": details or {}
            })
            
            # Keep history bound to last 100
            if len(self._history) > 100:
                self._history.pop(0)

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "current_context_id": self.current_context_id,
            "start_time": self.start_time,
            "end_time": self.end_time
        }
