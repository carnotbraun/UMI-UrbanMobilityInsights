import os
import sys
import pandas as pd
#import seaborn as sns
#import numpy as np
import matplotlib.pyplot as plt
#from bs4 import BeautifulSoup
#import xmltodict
import folium
from folium.plugins import HeatMap

from sumolib.visualization import helpers

# Add SUMO tools directory to the system path
sys.path.append(os.path.join('c:', os.sep, '/Users/carnotbraun/tese-mestrado/simu/sumo/tools'))

import sumolib

# Definindo variáveis
PATH_RSU = '/Users/carnotbraun/tese-mestrado/simu/data/rsus_lust_csv/'
NET_FILE = '/Users/carnotbraun/tese-mestrado/simu/LuSTScenario/scenario/lust.net.xml'

# Função para obter as bordas do cenário
def get_bbox(net):
    bbox = []
    for x, y in net.getBBoxXY():
        lat, lon = net.convertXY2LonLat(x, y)
        bbox.append((lon, lat))
    return bbox

# Função para obter as arestas da rede
def get_edges(net):
    edges_dict = {}
    edges = net.getEdges()
    for edge in edges:
        edge_id = edge.getID()
        from_node = edge.getFromNode()
        to_node = edge.getToNode()
        x_from, y_from = from_node.getCoord()
        lon_from, lat_from = net.convertXY2LonLat(x_from, y_from)
        x_to, y_to = to_node.getCoord()
        lon_to, lat_to = net.convertXY2LonLat(x_to, y_to)
        edges_dict[edge_id] = {'From': (lon_from, lat_from), 'To': (lon_to, lat_to)}
    return edges_dict

# Função para processar os valores
def get_values(df, edges, net):
    coords = []
    values = []
    file = open('/Users/carnotbraun/tese-mestrado/simu/data/heatmap/co2_lust.txt', 'a')
    for _, row in df.iterrows():
        edge_id = row['road_id']
        value = row['c02_emission']
        sum_co2 = row['sum_co2']
        if not net.hasEdge(edge_id):
            continue
        values.append(value)
        x_from, y_from = edges[edge_id]['From']
        coords.append([x_from, y_from, value])
        x_to, y_to = edges[edge_id]['To']
        coords.append([x_to, y_to, value])
        file.write(f'{edge_id} \t {value} \t {sum_co2}\n')
    file.close()
    return coords, values

# Carregando a rede sumo
net = sumolib.net.readNet(NET_FILE)

# Obtendo as bordas do cenário
bbox = get_bbox(net)

# Obtendo as arestas da rede
edges = get_edges(net)

# Processando os valores
coords_total = []
for rsu_id in range(13):
    df = pd.read_csv(f'{PATH_RSU}RSU_{rsu_id}.csv')
    df['step_novo'] = df['step'].apply(lambda x: x // (60 * 10))
    df = df.groupby(['step_novo', 'road_id']).sum().reset_index()
    df_filtered = df[df['step_novo'] == 42]
    df_filtered['sum_co2'] = df_filtered['c02_emission'].sum()
    coords, values = get_values(df_filtered, edges, net)
    coords_total.extend(coords) 

# Criando o mapa de calor
luxemburgo = folium.Map(location=bbox[0], blur=100, radius=500)
HeatMap(coords_total).add_to(luxemburgo)
luxemburgo.save('heatmap.html')

# Plotando o mapa de calor
plt.figure(figsize=(8, 8))
plt.scatter(*zip(*coords_total), c='r', alpha=0.5)
plt.show()
