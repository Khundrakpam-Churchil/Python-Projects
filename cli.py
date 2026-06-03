import sys
import os
from network_simulation import Network
from dijkstra import dijkstra, shortest_path, routing_table
from data_io import save_json, load_json, save_csv, load_csv, save_xml, load_xml
from visualization import plot_network


def print_menu():
    print('\nMenu:')
    print('1. Generate Network')
    print('2. Load Network (JSON)')
    print('3. Save Network (JSON)')
    print('4. View Topology')
    print('5. Run Dijkstra Algorithm')
    print('6. Show Statistics')
    print('7. Export Data')
    print('8. Simulate congestion / failed links')
    print('9. Run Demo')
    print('0. Exit')


def compute_stats(net: Network):
    nodes = net.nodes()
    edges = net.edges()
    total_nodes = len(nodes)
    total_connections = len(edges)
    latencies = [w for (_, _, w) in edges]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    # density
    n = total_nodes
    if net.directed:
        possible = n * (n - 1)
    else:
        possible = n * (n - 1) / 2
    density = total_connections / possible if possible else 0
    return {
        'total_nodes': total_nodes,
        'total_connections': total_connections,
        'avg_latency': avg_latency,
        'max_latency': max_latency,
        'min_latency': min_latency,
        'density': density
    }


def main():
    net = None
    while True:
        print_menu()
        choice = input('Choose an option: ').strip()
        if choice == '1':
            n = int(input('Number of nodes (10-50): ').strip() or 10)
            density = float(input('Density (0.0-1.0, e.g. 0.2): ').strip() or 0.2)
            directed = input('Directed graph? (y/N): ').strip().lower() == 'y'
            net = Network(directed=directed)
            net.generate(num_nodes=n, density=density)
            print('Generated', net)
        elif choice == '2':
            path = input('JSON path to load: ').strip()
            if not os.path.exists(path):
                print('File not found')
                continue
            data = load_json(path)
            net = Network.from_dict(data)
            print('Loaded', net)
        elif choice == '3':
            if net is None:
                print('No network in memory')
                continue
            path = input('Path to save JSON: ').strip()
            save_json(path, net.to_dict())
            print('Saved to', path)
        elif choice == '4':
            if net is None:
                print('No network in memory')
                continue
            plot_network(net.adj, directed=net.directed, title='Network Topology')
        elif choice == '5':
            if net is None:
                print('No network in memory')
                continue
            src = input('Source node (e.g. N0): ').strip()
            dst = input('Destination node (e.g. N5): ').strip()
            if src not in net.adj or dst not in net.adj:
                print('Source or destination not in network')
                continue
            dist, prev, visited = dijkstra(net.adj, src)
            path = shortest_path(prev, src, dst)
            print('\nDijkstra result:')
            print('Source:', src)
            print('Destination:', dst)
            print('Shortest path:', ' -> '.join(path) if path else 'UNREACHABLE')
            print('Total latency:', dist.get(dst, float('inf')))
            print('Nodes visited:', visited)
            plot_network(net.adj, directed=net.directed, highlight_path=path, title='Shortest Path')
        elif choice == '6':
            if net is None:
                print('No network in memory')
                continue
            s = compute_stats(net)
            print('\n' + '='*50)
            print('NETWORK STATISTICS')
            print('='*50)
            print(f'Total Nodes:        {s["total_nodes"]}')
            print(f'Total Connections:  {s["total_connections"]}')
            print(f'Average Latency:    {s["avg_latency"]:.2f} ms')
            print(f'Max Latency:        {s["max_latency"]:.2f} ms')
            print(f'Min Latency:        {s["min_latency"]:.2f} ms')
            print(f'Network Density:    {s["density"]:.2%}')
            print('='*50)
            
        elif choice == '7':
            if net is None:
                print('No network in memory')
                continue
            fmt = input('Export format (csv/xml): ').strip().lower()
            path = input('Path to save: ').strip()
            data = net.to_dict()
            if fmt == 'csv':
                save_csv(path, data)
            elif fmt == 'xml':
                save_xml(path, data)
            else:
                print('Unknown format')
                continue
            print('Exported to', path)
        elif choice == '8':
            if net is None:
                print('No network in memory')
                continue
            # backup then simulate
            net.backup_state()
            f = float(input('Failure rate (0.0-1.0): ').strip() or 0)
            c = float(input('Congestion factor (e.g. 0.5 for +50%): ').strip() or 0)
            removed = net.fail_links(f)
            if c > 0:
                net.simulate_congestion(c)
            print('Removed edges:', removed)
            print('Simulation applied. Use View Topology or Run Dijkstra to see effects.')
        elif choice == '9':
            # run demo script if present
            demo_path = os.path.join(os.getcwd(), 'run_demo.py')
            if os.path.exists(demo_path):
                print('Running demo...')
                os.system(f'"{sys.executable}" "{demo_path}"')
            else:
                print('run_demo.py not found in workspace')
        elif choice == '0':
            print('Exiting')
            sys.exit(0)
        else:
            print('Invalid choice')


if __name__ == '__main__':
    main()
