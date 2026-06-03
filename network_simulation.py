import random
import copy
from typing import Dict, List, Tuple


class Network:
    def __init__(self, directed: bool = False):
        self.directed = directed
        # adjacency: node -> {neighbor: weight}
        self.adj: Dict[str, Dict[str, int]] = {}
        # backup of original latencies for reset/analysis
        self._backup_adj: Dict[str, Dict[str, int]] = {}

    def add_node(self, node: str) -> None:
        if node not in self.adj:
            self.adj[node] = {}

    def add_edge(self, src: str, dst: str, latency: int) -> None:
        self.add_node(src)
        self.add_node(dst)
        self.adj[src][dst] = latency
        if not self.directed:
            self.adj[dst][src] = latency

        # keep backup in sync
        self._backup_adj = copy.deepcopy(self.adj)

    def nodes(self) -> List[str]:
        return list(self.adj.keys())

    def edges(self) -> List[Tuple[str, str, int]]:
        seen = set()
        out = []
        for u, nbrs in self.adj.items():
            for v, w in nbrs.items():
                if self.directed or (v, u) not in seen:
                    out.append((u, v, w))
                    seen.add((u, v))
        return out

    def generate(self, num_nodes: int = 10, density: float = 0.2,
                 min_latency: int = 1, max_latency: int = 100) -> None:
        if num_nodes < 1:
            raise ValueError("num_nodes must be >= 1")
        # Create node names: N0..N{n-1}
        for i in range(num_nodes):
            self.add_node(f"N{i}")

        nodes = self.nodes()
        # For each possible pair, add edge with probability density
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() <= density:
                    latency = random.randint(min_latency, max_latency)
                    self.add_edge(f"N{i}", f"N{j}", latency)

                # backup generated state
                self._backup_adj = copy.deepcopy(self.adj)

    def to_dict(self) -> Dict:
        return {
            "directed": self.directed,
            "nodes": self.nodes(),
            "edges": [{"src": u, "dst": v, "latency": w} for (u, v, w) in self.edges()]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Network":
        net = cls(directed=bool(data.get("directed", False)))
        for n in data.get("nodes", []):
            net.add_node(n)
        for e in data.get("edges", []):
            net.add_edge(e["src"], e["dst"], int(e["latency"]))
        net._backup_adj = copy.deepcopy(net.adj)
        return net

    def backup_state(self) -> None:
        self._backup_adj = copy.deepcopy(self.adj)

    def reset_state(self) -> None:
        if self._backup_adj:
            self.adj = copy.deepcopy(self._backup_adj)

    def simulate_congestion(self, congestion_factor: float) -> None:
        """
        Increase all latencies by congestion_factor (e.g., 0.5 => +50%).
        Modifies `adj` in-place. Call `backup_state()` beforehand to restore later.
        """
        if congestion_factor <= 0:
            return
        for u, nbrs in self.adj.items():
            for v in list(nbrs.keys()):
                orig = nbrs[v]
                new = int(round(orig * (1.0 + congestion_factor)))
                self.adj[u][v] = max(1, new)

    def fail_links(self, failure_rate: float) -> List[Tuple[str, str]]:
        """
        Randomly remove edges with probability `failure_rate`.
        Returns list of removed edges (src,dst).
        """
        if failure_rate <= 0:
            return []
        removed = []
        for u in list(self.adj.keys()):
            for v in list(self.adj[u].keys()):
                if random.random() < failure_rate:
                    # remove edge u->v
                    try:
                        del self.adj[u][v]
                        removed.append((u, v))
                    except KeyError:
                        continue
                    # if undirected, remove reverse
                    if not self.directed and v in self.adj and u in self.adj[v]:
                        try:
                            del self.adj[v][u]
                        except KeyError:
                            pass
        return removed

    def __repr__(self) -> str:
        return f"<Network nodes={len(self.nodes())} edges={len(self.edges())} directed={self.directed}>"
