import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple


def build_nx_graph(adj, directed=False):
    G = nx.DiGraph() if directed else nx.Graph()
    for u, nbrs in adj.items():
        G.add_node(u)
        for v, w in nbrs.items():
            G.add_edge(u, v, latency=w)
    return G


def plot_network(adj, directed=False, highlight_path: List[str] = None, title: str = 'Network'):
    G = build_nx_graph(adj, directed=directed)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(G, pos, node_size=500)
    nx.draw_networkx_labels(G, pos)

    edge_labels = nx.get_edge_attributes(G, 'latency')

    if highlight_path and len(highlight_path) >= 2:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
    else:
        path_edges = []

    other_edges = [e for e in G.edges() if e not in path_edges]

    nx.draw_networkx_edges(G, pos, edgelist=other_edges, width=1, alpha=0.7)
    if path_edges:
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=3, edge_color='r')

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
