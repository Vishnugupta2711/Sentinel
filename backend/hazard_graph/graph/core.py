import threading
from typing import Dict, List, Set, Tuple
from hazard_graph.nodes.models import Node
from hazard_graph.edges.models import Edge, EdgeType


class HazardGraphCore:
    """
    High-performance in-memory adjacency list representing the semantic topology
    of the plant.

    PERF improvements:
    - Edge dedup uses a set of (target, type) tuples → O(1) instead of O(E) scan
    - remove_edges uses a single-pass partition loop instead of 3× comprehensions
    - remove_node cascades in one locked pass
    """

    def __init__(self):
        self._lock = threading.Lock()

        # ID → Node
        self.nodes: Dict[str, Node] = {}

        # Source ID → List[Edge]
        self.out_edges: Dict[str, List[Edge]] = {}
        # Target ID → List[Edge]  (for reverse lookups)
        self.in_edges: Dict[str, List[Edge]] = {}

        # Source ID → Set[(target, edge_type)] for O(1) duplicate detection
        self._out_edge_keys: Dict[str, Set[Tuple[str, EdgeType]]] = {}

    def add_node(self, node: Node) -> None:
        with self._lock:
            self.nodes[node.id] = node
            if node.id not in self.out_edges:
                self.out_edges[node.id]    = []
                self.in_edges[node.id]     = []
                self._out_edge_keys[node.id] = set()

    def remove_node(self, node_id: str) -> None:
        with self._lock:
            if node_id not in self.nodes:
                return

            del self.nodes[node_id]

            # Remove outgoing edges and their reverse entries
            for edge in self.out_edges.pop(node_id, []):
                tgt = self.in_edges.get(edge.target)
                if tgt is not None:
                    tgt[:] = [e for e in tgt if e.source != node_id]
            self._out_edge_keys.pop(node_id, None)

            # Remove incoming edges and their forward entries
            for edge in self.in_edges.pop(node_id, []):
                src_out = self.out_edges.get(edge.source)
                src_keys = self._out_edge_keys.get(edge.source)
                if src_out is not None:
                    src_out[:] = [e for e in src_out if e.target != node_id]
                if src_keys is not None:
                    src_keys.discard((node_id, edge.type))

    def add_edge(self, edge: Edge) -> None:
        with self._lock:
            if edge.source not in self.nodes or edge.target not in self.nodes:
                return

            # O(1) duplicate check via the key set
            key = (edge.target, edge.type)
            if key not in self._out_edge_keys[edge.source]:
                self._out_edge_keys[edge.source].add(key)
                self.out_edges[edge.source].append(edge)
                self.in_edges[edge.target].append(edge)

    def remove_edges(self, source: str, edge_type: EdgeType) -> None:
        """Removes all edges of a specific type from source. Single-pass partition."""
        with self._lock:
            if source not in self.out_edges:
                return

            kept, removed = [], []
            for e in self.out_edges[source]:
                (removed if e.type == edge_type else kept).append(e)

            self.out_edges[source] = kept

            for edge in removed:
                self._out_edge_keys[source].discard((edge.target, edge_type))
                tgt = self.in_edges.get(edge.target)
                if tgt is not None:
                    tgt[:] = [e for e in tgt if not (e.source == source and e.type == edge_type)]

    def clear(self):
        with self._lock:
            self.nodes.clear()
            self.out_edges.clear()
            self.in_edges.clear()
            self._out_edge_keys.clear()
