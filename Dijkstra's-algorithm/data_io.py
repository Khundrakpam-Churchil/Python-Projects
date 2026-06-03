import json
import csv
import xml.etree.ElementTree as ET
from typing import Dict


def save_json(path: str, data: Dict) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_json(path: str) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_csv(path: str, data: Dict) -> None:
    # data expected: {'nodes': [...], 'edges': [{'src':..,'dst':..,'latency':..}, ...]}
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'src', 'dst', 'latency'])
        for n in data.get('nodes', []):
            writer.writerow(['node', n, '', ''])
        for e in data.get('edges', []):
            writer.writerow(['edge', e.get('src'), e.get('dst'), e.get('latency')])


def load_csv(path: str) -> Dict:
    nodes = []
    edges = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        for row in reader:
            if not row:
                continue
            typ = row[0]
            if typ == 'node':
                nodes.append(row[1])
            elif typ == 'edge':
                edges.append({'src': row[1], 'dst': row[2], 'latency': int(row[3])})
    return {'nodes': nodes, 'edges': edges}


def save_xml(path: str, data: Dict) -> None:
    root = ET.Element('network')
    ET.SubElement(root, 'directed').text = str(data.get('directed', False))
    nodes_el = ET.SubElement(root, 'nodes')
    for n in data.get('nodes', []):
        ET.SubElement(nodes_el, 'node').text = n
    edges_el = ET.SubElement(root, 'edges')
    for e in data.get('edges', []):
        edge_el = ET.SubElement(edges_el, 'edge')
        ET.SubElement(edge_el, 'src').text = e.get('src')
        ET.SubElement(edge_el, 'dst').text = e.get('dst')
        ET.SubElement(edge_el, 'latency').text = str(e.get('latency'))
    tree = ET.ElementTree(root)
    tree.write(path, encoding='utf-8', xml_declaration=True)


def load_xml(path: str) -> Dict:
    tree = ET.parse(path)
    root = tree.getroot()
    nodes = [n.text for n in root.find('nodes').findall('node')] if root.find('nodes') is not None else []
    edges = []
    for e in root.find('edges').findall('edge') if root.find('edges') is not None else []:
        src = e.find('src').text
        dst = e.find('dst').text
        lat = int(e.find('latency').text)
        edges.append({'src': src, 'dst': dst, 'latency': lat})
    return {'directed': root.find('directed').text.lower() == 'true', 'nodes': nodes, 'edges': edges}
