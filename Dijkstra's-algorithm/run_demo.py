import json
import os
from network_simulation import Network
from dijkstra import dijkstra, shortest_path
from data_io import save_json, save_csv, save_xml


def run_demo():
    here = os.getcwd()
    sample = os.path.join(here, 'sample_network.json')
    if not os.path.exists(sample):
        print('sample_network.json not found')
        return
    data = json.load(open(sample))
    net = Network.from_dict(data)
    print('Loaded network:', net)

    # baseline shortest path
    src, dst = 'N0', 'N4'
    dist, prev, visited = dijkstra(net.adj, src)
    path = shortest_path(prev, src, dst)
    print('\nBaseline:')
    print('Path', path, 'Latency', dist.get(dst))

    # apply failures and congestion
    net.backup_state()
    removed = net.fail_links(0.2)
    net.simulate_congestion(0.5)
    print('\nAfter failures (+20%) and congestion (+50%):')
    print('Removed edges:', removed)
    dist2, prev2, visited2 = dijkstra(net.adj, src)
    path2 = shortest_path(prev2, src, dst)
    print('Path', path2, 'Latency', dist2.get(dst))

    # save outputs
    out_json = os.path.join(here, 'demo_output.json')
    save_json(out_json, net.to_dict())
    save_csv(os.path.join(here, 'demo_output.csv'), net.to_dict())
    save_xml(os.path.join(here, 'demo_output.xml'), net.to_dict())
    print('\nSaved demo outputs to demo_output.{json,csv,xml}')


if __name__ == '__main__':
    run_demo()
