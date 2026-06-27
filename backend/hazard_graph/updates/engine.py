import structlog
from typing import Set
from hazard_graph.graph.core import HazardGraphCore
from hazard_graph.nodes.models import Node, NodeType
from hazard_graph.edges.models import Edge, EdgeType
from world_state.snapshot.models import WorldState

logger = structlog.get_logger(__name__)

class UpdateEngine:
    """
    Synchronizes the HazardGraph with the latest WorldState tick.
    Instead of blowing away the graph, it diffs and updates edges to maintain structural stability.
    """
    
    def __init__(self, graph: HazardGraphCore):
        self.graph = graph

    def sync(self, state: WorldState) -> None:
        """Fully syncs the graph topology with the new state."""
        
        # 0. Sync Structural Nodes (Plant, Building, Zone)
        if state.plant:
            p = state.plant
            self.graph.add_node(Node(id=p.id, type=NodeType.PLANT, label=p.name))
            
        for b in state.buildings:
            self.graph.add_node(Node(id=b.id, type=NodeType.BUILDING, label=b.name))
            if state.plant:
                self.graph.add_edge(Edge(source=b.id, target=state.plant.id, type=EdgeType.LOCATED_IN))
                
        for z in state.zones:
            self.graph.add_node(Node(id=z.id, type=NodeType.ZONE, label=z.name, attributes={"hazard_level": z.hazard_level}))
            if z.building_id:
                self.graph.add_edge(Edge(source=z.id, target=z.building_id, type=EdgeType.LOCATED_IN))
        
        # 1. Sync Workers (Movement)
        for w in state.workers:
            # Upsert node attributes
            self.graph.add_node(Node(id=w.id, type=NodeType.WORKER, label=w.name, attributes={"role": w.role.value}))
            
            # Sync LOCATED_IN
            if w.zone_id:
                # To be purely declarative, we drop existing LOCATED_IN and add the current one.
                # Since a worker can only be in one zone at a time:
                self.graph.remove_edges(w.id, EdgeType.LOCATED_IN)
                self.graph.add_edge(Edge(source=w.id, target=w.zone_id, type=EdgeType.LOCATED_IN))
                
        # 2. Sync Equipment (Status changes)
        for e in state.equipment:
            self.graph.add_node(Node(id=e.id, type=NodeType.EQUIPMENT, label=e.name, attributes={"status": e.status.value}))
            
        # 3. Sync Sensors (Values/Status)
        for s in state.sensors:
            self.graph.add_node(Node(id=s.id, type=NodeType.SENSOR, label=f"Sensor {s.sensor_type.value}", attributes={"status": s.status.value}))
            
            # Upsert edges
            self.graph.remove_edges(s.id, EdgeType.LOCATED_IN)
            if s.zone_id:
                self.graph.add_edge(Edge(source=s.id, target=s.zone_id, type=EdgeType.LOCATED_IN))
            
        # 4. Sync Hazards (Spawns and Clears)
        current_hazard_ids: Set[str] = set()
        for h in state.hazards:
            current_hazard_ids.add(h.id)
            self.graph.add_node(Node(id=h.id, type=NodeType.HAZARD, label=h.hazard_type.value, attributes={"severity": h.severity.value}))
            
            # Upsert edges
            self.graph.remove_edges(h.id, EdgeType.AFFECTS)
            if h.zone_id:
                self.graph.add_edge(Edge(source=h.id, target=h.zone_id, type=EdgeType.AFFECTS))
                
        # Remove cleared hazards from the graph
        with self.graph._lock:
            graph_hazard_ids = [nid for nid, n in self.graph.nodes.items() if n.type == NodeType.HAZARD]
            for nid in graph_hazard_ids:
                if nid not in current_hazard_ids:
                    # Drop from graph
                    # We have to defer the actual call because it acquires the lock again.
                    pass # We'll do it outside the lock block
                    
        for nid in graph_hazard_ids:
            if nid not in current_hazard_ids:
                self.graph.remove_node(nid)
