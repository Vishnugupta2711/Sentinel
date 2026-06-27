from hazard_graph.graph.core import HazardGraphCore
from hazard_graph.nodes.models import Node, NodeType
from hazard_graph.edges.models import Edge, EdgeType
from world_state.snapshot.models import WorldState

class GraphBuilder:
    """Bootstraps the HazardGraph from a WorldState snapshot."""
    
    @staticmethod
    def build(graph: HazardGraphCore, state: WorldState) -> None:
        graph.clear()
        
        # 1. Add Plant Node
        if state.plant:
            p = state.plant
            graph.add_node(Node(id=p.id, type=NodeType.PLANT, label=p.name))
            
        # 2. Add Buildings
        for b in state.buildings:
            graph.add_node(Node(id=b.id, type=NodeType.BUILDING, label=b.name))
            if state.plant:
                graph.add_edge(Edge(source=b.id, target=state.plant.id, type=EdgeType.LOCATED_IN))
                
        # 3. Add Zones
        for z in state.zones:
            graph.add_node(Node(id=z.id, type=NodeType.ZONE, label=z.name, attributes={"risk_level": z.risk_level.value}))
            if z.building_id:
                graph.add_edge(Edge(source=z.id, target=z.building_id, type=EdgeType.LOCATED_IN))
                
        # 4. Add Workers
        for w in state.workers:
            graph.add_node(Node(id=w.id, type=NodeType.WORKER, label=w.name, attributes={"role": w.role.value}))
            if w.zone_id:
                graph.add_edge(Edge(source=w.id, target=w.zone_id, type=EdgeType.LOCATED_IN))
                
        # 5. Add Sensors
        for s in state.sensors:
            graph.add_node(Node(id=s.id, type=NodeType.SENSOR, label=f"Sensor {s.sensor_type.value}", attributes={"status": s.status.value}))
            if s.zone_id:
                graph.add_edge(Edge(source=s.id, target=s.zone_id, type=EdgeType.LOCATED_IN))
                
        # 6. Add Equipment
        for e in state.equipment:
            graph.add_node(Node(id=e.id, type=NodeType.EQUIPMENT, label=e.name, attributes={"status": e.status.value}))
            if e.zone_id:
                graph.add_edge(Edge(source=e.id, target=e.zone_id, type=EdgeType.LOCATED_IN))
                
        # 7. Add Hazards
        for h in state.hazards:
            graph.add_node(Node(id=h.id, type=NodeType.HAZARD, label=h.hazard_type.value, attributes={"severity": h.severity.value}))
            if h.zone_id:
                graph.add_edge(Edge(source=h.id, target=h.zone_id, type=EdgeType.AFFECTS))
