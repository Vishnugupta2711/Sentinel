import pytest
from world_state.snapshot.models import WorldState
from world.models.entities import Worker, Equipment, Sensor
from hazard_graph.engine.core import HazardGraphEngine
from hazard_graph.edges.models import EdgeType
from hazard_graph.nodes.models import NodeType

@pytest.fixture
def engine():
    return HazardGraphEngine()

def test_graph_builder_and_updates(engine: HazardGraphEngine):
    # Setup initial state
    w1 = Worker(id="w1", name="Worker 1", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="z1")
    e1 = Equipment(id="e1", name="Pump", equipment_type="PUMP", manufacturer="Test", status="ONLINE", zone_id="z1")
    s1 = Sensor(id="s1", name="Temp", sensor_type="TEMPERATURE", unit="C", threshold=100.0, last_updated="2026-06-26T00:00:00Z", status="ONLINE", zone_id="z1")
    
    from hazard_graph.nodes.models import Node
    engine.graph.add_node(Node(id="z1", type=NodeType.ZONE, label="Z1"))
    engine.graph.add_node(Node(id="z2", type=NodeType.ZONE, label="Z2"))
    
    state1 = WorldState(version=1, workers=[w1], equipment=[e1], sensors=[s1])
    
    # Sync graph
    engine.updates.sync(state1)
    
    with engine.graph._lock:
        assert len(engine.graph.nodes) == 5
        
        # Check edges for Worker LOCATED_IN
        w_edges = engine.graph.out_edges.get("w1", [])
        assert len(w_edges) == 1
        assert w_edges[0].type == EdgeType.LOCATED_IN
        assert w_edges[0].target == "z1"

    # Worker moves to z2 in next tick
    w1_moved = Worker(id="w1", name="Worker 1", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="z2")
    state2 = WorldState(version=2, workers=[w1_moved], equipment=[e1], sensors=[s1])
    engine.updates.sync(state2)
    
    with engine.graph._lock:
        w_edges = engine.graph.out_edges.get("w1", [])
        assert len(w_edges) == 1
        assert w_edges[0].target == "z2" # Moved!
        assert w_edges[0].type == EdgeType.LOCATED_IN

def test_graph_pathfinding(engine: HazardGraphEngine):
    # Setup graph structure: W1 -> Z1 -> Z2 -> Z3
    from hazard_graph.nodes.models import Node
    from hazard_graph.edges.models import Edge
    engine.graph.add_node(Node(id="z1", type=NodeType.ZONE, label="Z1"))
    engine.graph.add_node(Node(id="z2", type=NodeType.ZONE, label="Z2"))
    engine.graph.add_node(Node(id="z3", type=NodeType.ZONE, label="Z3"))
    
    w1 = Worker(id="w1", name="Worker 1", role="OPERATOR", department="A", shift="DAY", worker_status="ACTIVE", zone_id="z1")
    state = WorldState(version=1, workers=[w1])
    engine.updates.sync(state)
    
    # Manually stitch a topological path for Z1-Z2-Z3
    engine.graph.add_edge(Edge(source="z1", target="z2", type=EdgeType.CONNECTED_TO))
    engine.graph.add_edge(Edge(source="z2", target="z3", type=EdgeType.CONNECTED_TO))
    
    # Path from worker to z3
    path = engine.queries.shortest_path("w1", "z3")
    assert path == ["w1", "z1", "z2", "z3"]
