from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel

class EdgeType(str, Enum):
    LOCATED_IN = "LOCATED_IN"
    CONNECTED_TO = "CONNECTED_TO"
    WORKS_ON = "WORKS_ON"
    MONITORS = "MONITORS"
    ATTACHED_TO = "ATTACHED_TO"
    CONTAINS = "CONTAINS"
    GENERATES = "GENERATES"
    DEPENDS_ON = "DEPENDS_ON"
    BLOCKS = "BLOCKS"
    PROTECTS = "PROTECTS"
    CAUSES = "CAUSES"
    AFFECTS = "AFFECTS"

class Edge(BaseModel):
    source: str
    target: str
    type: EdgeType
    weight: float = 1.0
    attributes: Dict[str, Any] = {}
