import zlib
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from world_state.snapshot.models import WorldState
from utils.uuid import generate_uuid
from utils.datetime import format_iso, utc_now

class TimelineEntry(BaseModel):
    """
    A single point in time in the historical timeline.
    It holds either a raw WorldState or a zlib-compressed binary blob to save memory.
    """
    entry_id: str = Field(default_factory=generate_uuid)
    timestamp: str = Field(default_factory=lambda: format_iso(utc_now()))
    version: int
    simulation_tick: int
    
    # We store the state as Optional because it might be compressed
    _raw_state: Optional[WorldState] = None
    _compressed_state: Optional[bytes] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def set_state(self, state: WorldState):
        self._raw_state = state
        self._compressed_state = None
        
    def get_state(self) -> WorldState:
        """Transparently returns the WorldState, decompressing if necessary."""
        if self._raw_state:
            return self._raw_state
        if self._compressed_state:
            # Decompress and deserialize
            json_str = zlib.decompress(self._compressed_state).decode('utf-8')
            # Assuming WorldState can parse raw JSON string, but actually model_validate_json is better
            self._raw_state = WorldState.model_validate_json(json_str)
            # We don't clear compressed state here, we just cache the raw state
            return self._raw_state
        raise ValueError("TimelineEntry has no state.")

    def compress(self):
        """Compresses the raw state and drops the object reference to save memory."""
        if self._raw_state and not self._compressed_state:
            json_str = self._raw_state.model_dump_json()
            self._compressed_state = zlib.compress(json_str.encode('utf-8'), level=9)
            self._raw_state = None
            
    @property
    def is_compressed(self) -> bool:
        return self._compressed_state is not None and self._raw_state is None
