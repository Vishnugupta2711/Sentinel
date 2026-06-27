from typing import Dict
from hazard_graph.graph.core import HazardGraphCore

class GraphAnalytics:
    def __init__(self, graph: HazardGraphCore):
        self.graph = graph

    def degree_centrality(self) -> Dict[str, int]:
        """
        Calculates the total degree (in-degree + out-degree) of every node.
        High degree indicates a critical nexus (e.g., a central Zone or critical equipment).
        """
        centrality = {}
        with self.graph._lock:
            for node_id in self.graph.nodes:
                in_deg = len(self.graph.in_edges.get(node_id, []))
                out_deg = len(self.graph.out_edges.get(node_id, []))
                centrality[node_id] = in_deg + out_deg
                
        return centrality

    def critical_assets(self, top_n: int = 5) -> list:
        """
        Returns the top N assets (Equipment/Zones) with the highest degree centrality.
        """
        centrality = self.degree_centrality()
        
        # Sort by degree descending
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:top_n]
