from collections import deque
from typing import List, Optional, Set
from hazard_graph.graph.core import HazardGraphCore

class GraphQueries:
    def __init__(self, graph: HazardGraphCore):
        self.graph = graph

    def shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Finds the shortest topological path between two nodes using Breadth-First Search (BFS).
        Treats the graph as undirected for connectivity purposes (e.g., A is LOCATED_IN B implies B contains A).
        """
        with self.graph._lock:
            if source_id not in self.graph.nodes or target_id not in self.graph.nodes:
                return None
                
            queue = deque([(source_id, [source_id])])
            visited: Set[str] = {source_id}
            
            while queue:
                curr_id, path = queue.popleft()
                
                if curr_id == target_id:
                    return path
                    
                # Get neighbors (both incoming and outgoing edges)
                neighbors = set()
                if curr_id in self.graph.out_edges:
                    for e in self.graph.out_edges[curr_id]:
                        neighbors.add(e.target)
                if curr_id in self.graph.in_edges:
                    for e in self.graph.in_edges[curr_id]:
                        neighbors.add(e.source)
                        
                for n_id in neighbors:
                    if n_id not in visited:
                        visited.add(n_id)
                        queue.append((n_id, path + [n_id]))
                        
            return None

    def affected_workers(self, hazard_id: str) -> List[str]:
        """
        Returns a list of worker IDs that are directly affected by the hazard.
        A worker is affected if they are LOCATED_IN the same zone that the hazard AFFECTS.
        """
        with self.graph._lock:
            if hazard_id not in self.graph.nodes:
                return []
                
            affected_zones = []
            if hazard_id in self.graph.out_edges:
                for e in self.graph.out_edges[hazard_id]:
                    if e.type == "AFFECTS":
                        affected_zones.append(e.target)
                        
            workers = set()
            for z_id in affected_zones:
                if z_id in self.graph.in_edges:
                    for e in self.graph.in_edges[z_id]:
                        if e.type == "LOCATED_IN" and self.graph.nodes[e.source].type == "Worker":
                            workers.add(e.source)
                            
            return list(workers)
