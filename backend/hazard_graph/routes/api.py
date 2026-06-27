from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from hazard_graph.engine.core import HazardGraphEngine, get_hazard_graph_engine
from hazard_graph.schemas.api import GraphSnapshotResponse, PathResponse, CentralityResponse
from hazard_graph.nodes.models import Node
from hazard_graph.edges.models import Edge

router = APIRouter(prefix="/graph", tags=["Hazard Graph"])

@router.get("/", response_model=GraphSnapshotResponse)
async def get_entire_graph(engine: HazardGraphEngine = Depends(get_hazard_graph_engine)):
    with engine.graph._lock:
        nodes = list(engine.graph.nodes.values())
        edges = []
        for src, edge_list in engine.graph.out_edges.items():
            edges.extend(edge_list)
        return GraphSnapshotResponse(nodes=nodes, edges=edges)

@router.get("/nodes", response_model=List[Node])
async def get_nodes(engine: HazardGraphEngine = Depends(get_hazard_graph_engine)):
    with engine.graph._lock:
        return list(engine.graph.nodes.values())

@router.get("/edges", response_model=List[Edge])
async def get_edges(engine: HazardGraphEngine = Depends(get_hazard_graph_engine)):
    with engine.graph._lock:
        edges = []
        for src, edge_list in engine.graph.out_edges.items():
            edges.extend(edge_list)
        return edges

@router.get("/node/{node_id}", response_model=Node)
async def get_node(node_id: str, engine: HazardGraphEngine = Depends(get_hazard_graph_engine)):
    with engine.graph._lock:
        if node_id not in engine.graph.nodes:
            raise HTTPException(status_code=404, detail="Node not found.")
        return engine.graph.nodes[node_id]

@router.get("/path", response_model=PathResponse)
async def get_path(
    source: str = Query(...), 
    target: str = Query(...),
    engine: HazardGraphEngine = Depends(get_hazard_graph_engine)
):
    path = engine.queries.shortest_path(source, target)
    if not path:
        return PathResponse(path=None, length=0)
    return PathResponse(path=path, length=len(path) - 1)

@router.get("/analytics/centrality", response_model=List[CentralityResponse])
async def get_centrality(engine: HazardGraphEngine = Depends(get_hazard_graph_engine)):
    top = engine.analytics.critical_assets(top_n=10)
    return [CentralityResponse(node_id=nid, degree=deg) for nid, deg in top]
