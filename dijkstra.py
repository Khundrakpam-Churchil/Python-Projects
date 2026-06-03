import heapq
from typing import Dict, Tuple, List


def dijkstra(adj: Dict[str, Dict[str, int]], source: str) -> Tuple[Dict[str, int], Dict[str, str], List[str]]:
    dist: Dict[str, int] = {node: float('inf') for node in adj}
    prev: Dict[str, str] = {}
    dist[source] = 0
    visited_order: List[str] = []

    heap: List[Tuple[int, str]] = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        visited_order.append(u)
        for v, w in adj[u].items():
            alt = dist[u] + w
            if alt < dist.get(v, float('inf')):
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))

    return dist, prev, visited_order


def shortest_path(prev: Dict[str, str], source: str, target: str) -> List[str]:
    if target not in prev and source != target:
        # may be directly the source or unreachable
        if source == target:
            return [source]
        return []
    path = []
    u = target
    while u != source:
        path.append(u)
        u = prev.get(u)
        if u is None:
            return []
    path.append(source)
    path.reverse()
    return path


def routing_table(adj: Dict[str, Dict[str, int]], source: str) -> Dict[str, Tuple[str, int]]:
    dist, prev, _ = dijkstra(adj, source)
    table: Dict[str, Tuple[str, int]] = {}
    for node in adj:
        if node == source:
            continue
        path = shortest_path(prev, source, node)
        if not path:
            table[node] = (None, float('inf'))
        else:
            next_hop = path[1] if len(path) > 1 else node
            table[node] = (next_hop, dist[node])
    return table
