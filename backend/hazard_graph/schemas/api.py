from typing import List, Optional
from pydantic import BaseModel
from hazard_graph.nodes.models import Node
from hazard_graph.edges.models import Edge

class GraphSnapshotResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class PathResponse(BaseModel):
    path: Optional[List[str]]
    length: int

class CentralityResponse(BaseModel):
    node_id: str
    degree: int
