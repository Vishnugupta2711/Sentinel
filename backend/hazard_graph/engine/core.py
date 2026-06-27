from hazard_graph.graph.core import HazardGraphCore
from hazard_graph.updates.engine import UpdateEngine
from hazard_graph.queries.pathfinding import GraphQueries
from hazard_graph.analytics.centrality import GraphAnalytics

class HazardGraphEngine:
    """Composition root for the Dynamic Hazard Graph module."""
    
    def __init__(self):
        self.graph = HazardGraphCore()
        
        self.updates = UpdateEngine(self.graph)
        self.queries = GraphQueries(self.graph)
        self.analytics = GraphAnalytics(self.graph)

# Singleton for FastAPI injection
hazard_graph_engine = HazardGraphEngine()

def get_hazard_graph_engine() -> HazardGraphEngine:
    return hazard_graph_engine
