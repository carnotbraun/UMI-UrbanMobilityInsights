import os
import csv
from bs4 import BeautifulSoup
from scipy.spatial.distance import euclidean
import traci
import pickle

# Create Road Network Graph Representation
def read_network(network_file):
    with open(network_file, encoding="utf8") as net_file:
        data = net_file.read()
        soup = BeautifulSoup(data, "lxml")

    edges_dict = {}

    for edge_tag in soup.findAll("edge"):
        edge_id = edge_tag["id"]
        if not edge_id.startswith(':'):
            edges_dict[edge_id] = {}
            edges_dict[edge_id]['from'] = edge_tag["from"]
            edges_dict[edge_id]['to'] = edge_tag["to"]

    return edges_dict

# Get Positions of Each RSU
def get_rsus():
    rsus = []

    with open('/Users/carnotbraun/tese-mestrado/simu/utils/rsus_lust_v0.txt', 'r') as rsu_file:
        for line in rsu_file:
            line = line.strip().split('\t')
            rsus.append({'x': float(line[0]), 'y': float(line[1])})

    return rsus

# Check Euclidean Distance
RADIUS = 2_000
def check_coverage(node_from, node_to, rsu_position):
    position_from = traci.junction.getPosition(node_from)
    position_to = traci.junction.getPosition(node_to)
    dist_from = euclidean(rsu_position, position_from)
    dist_to = euclidean(rsu_position, position_to)

    return True if dist_from <= RADIUS or dist_to <= RADIUS else False

# Check Roads Covered by Each RSU
def get_covered_roads(rsus, edges):
    edges_per_rsu = {}

    for idx, rsu in enumerate(rsus):
        rsu_position = (rsu['x'], rsu['y'])
        edges_per_rsu[str(idx)] = []

        for edge in edges:
            node_from = edges[edge]['from']
            node_to = edges[edge]['to']
            edge_id = edge

            if check_coverage(node_from, node_to, rsu_position):
                edges_per_rsu[str(idx)].append(edge_id)

    return edges_per_rsu

def main():
    sumo_exec = "/Users/carnotbraun/tese-mestrado/simu/sumo/bin/sumo"
    sumo_cmd = [sumo_exec, '-c', 
                '/Users/carnotbraun/tese-mestrado/simu/LuSTScenario/scenario/due.actuated.sumocfg']
    traci.start(sumo_cmd)

    edges = read_network('/Users/carnotbraun/tese-mestrado/simu/LuSTScenario/scenario/lust.net.xml')
    rsus = get_rsus()
    edges_per_rsu = get_covered_roads(rsus, edges)

    # Read data from CSV files
    csv_files = [f'/Users/carnotbraun/tese-mestrado/simu/data/lust_edges/{edge}.csv' for rsu_edges in edges_per_rsu.values() for edge in rsu_edges]
    roads_in_rsu = {}

    for csv_file in csv_files:
        rsu_id = os.path.basename(csv_file).split('.')[0]
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            road_count = sum(1 for _ in reader)
            roads_in_rsu[rsu_id] = road_count

    for rsu, road_count in roads_in_rsu.items():
        print(f"RSU {rsu}: {road_count} roads covered")

    # Save covered roads for each RSU
    for rsu in edges_per_rsu:
        with open(f'/Users/carnotbraun/tese-mestrado/simu/data/lust_test/RSU_{rsu}.pickle', 'wb') as rsu_file:
            print(f'Writing Roads Covered by RSU {rsu}...')
            pickle.dump(edges_per_rsu[rsu], rsu_file, protocol=pickle.HIGHEST_PROTOCOL)

    traci.close()

if __name__ == "__main__":
    main()
