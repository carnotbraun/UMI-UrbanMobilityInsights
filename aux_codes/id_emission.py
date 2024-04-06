import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from bs4 import BeautifulSoup

# Add SUMO tools directory to the system path
sys.path.append(os.path.join('c:', os.sep, '/Users/carnotbraun/tese-mestrado/simu/sumo/tools'))

import traci
import sumolib
from folium.plugins import HeatMap

# Read SUMO network
NET_FILE = '/Users/carnotbraun/tese-mestrado/simu/TAPASCologne/cologne.net.xml'
net = sumolib.net.readNet(NET_FILE)

def get_edges(net):
    edges_dict = {}
    edges = net.getEdges()

    for edge in edges:
        edge_id = edge.getID()
        from_node = edge.getFromNode()
        to_node = edge.getToNode()

        x, y = from_node.getCoord()
        lat_from, lon_from = net.convertXY2LonLat(x, y)
        x, y = to_node.getCoord()
        lat_to, lon_to = net.convertXY2LonLat(x, y)

        edges_dict[edge_id] = {'From': (lon_from, lat_from), 'To': (lon_to, lat_to)}

    return edges_dict

edges = get_edges(net)

def get_bbox(net):
    bbox = []
    for x, y in net.getBBoxXY():
        lat, lon = net.convertXY2LonLat(x, y)
        bbox.append((lon, lat))
    return bbox

def get_values(df):
    coords = []
    values = []

    # Open the file for writing
    with open('/Users/carnotbraun/tese-mestrado/code/co2_tapas.txt', 'a') as file:
        # Loop through CSV files in the directory
        PATH_RSU = '/Users/carnotbraun/tese-mestrado/simu/data/rsus_cologne_csv/'
        for file_name in os.listdir(PATH_RSU):
            if file_name.endswith('.csv'):
                file_path = os.path.join(PATH_RSU, file_name)
                df = pd.read_csv(file_path)
                # Group by road_id and calculate cumulative CO2 emissions
                grouped = df.groupby('road_id')['c02_emission'].cumsum()

                for i, row in df.iterrows():
                    edge_id = row['road_id']
                    value = grouped[i]  # Get cumulative value at this time step

                    values.append(value)

                    x, y = edges[edge_id]['From']
                    coords.append([x, y, value])
                    x, y = edges[edge_id]['To']
                    coords.append([x, y, value])
                    
                    # Write edge_id and value to the file
                    file.write(f'{edge_id} \t {value}\n')

    return coords, values

# Example usage:
df = pd.DataFrame()  # Provide your DataFrame here
coords, values = get_values(df)

