from bs4 import BeautifulSoup
import math
import pandas as pd
import sumolib
from sumolib import net
import random
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.collections import LineCollection
import matplotlib.patches as patches

def read_network(network):
    f = open(network)
    data = f.read()
    soup = BeautifulSoup(data, "xml")    
    f.close()
    return soup

def get_vertex_positions(soup):                    
    vertex_positions = {}
    for junction_tag in soup.findAll("junction"):
        junction_id = junction_tag["id"]
        if junction_id.startswith(":"): 
            continue
        else:
            x = float(junction_tag['x'])
            y = float(junction_tag['y'])
            vertex_positions[junction_id] = (x, y)
    return vertex_positions

def compute_k(h, l, comm_radius):
    scenario_area = h * l
    communication_area = math.pi * comm_radius**2
    return math.ceil(scenario_area/communication_area)

def get_scenario_area(soup):
    location_tag = soup.find("location")
    boundary = location_tag['convBoundary']
    boundary = boundary.split(',')
    p1 = (float(boundary[0]), float(boundary[1]))
    p2 = (float(boundary[2]), float(boundary[3]))
    p3 = (p2[0], p1[1])
    p4 = (p1[0], p2[1])
    l = math.hypot(p1[0] - p3[0], p1[1] - p3[1])
    h = math.hypot(p1[0] - p4[0], p1[1] - p4[1])
    return h, l

def plot_clusters(data, k, labels, center, ax):
    for i in range(k):
        dados_clusters = data[np.where(labels==i)]

        plt.plot(dados_clusters[:,0], dados_clusters[:,1], 'o')

    plt.scatter(center[:,0], center[:,1], marker='x', s = 500, linewidths=2, color='black')
    for x,y in center:
        circle = patches.Circle((x, y), radius=6000, edgecolor='blue', alpha=0.25)
        ax.add_patch(circle)

def get_rsus(rsu_file):
    rsus = []

    with open(rsu_file, 'r') as rsu_file:
        for line in rsu_file:
            line = line.strip().split('\t')
            rsus.append({'x': float(line[0]), 'y': float(line[1])})

    return rsus

NET_FILE = '/Users/carnotbraun/tese-mestrado/simu/MoSTScenario/scenario/in/most.net.xml'
RSU_FILE = '/Users/carnotbraun/tese-mestrado/simu/utils/most_rsus.txt'

print('Reading network file ...')
soup = read_network(NET_FILE)
print('Getting vertex positions ...')
vertex_positions = get_vertex_positions(soup)
h, l = get_scenario_area(soup)

net = sumolib.net.readNet(NET_FILE)
# Read data from co2_lust.txt
df_edges = pd.read_csv('/Users/carnotbraun/tese-mestrado/simu/data/heatmap/co2_most.txt', 
                       sep='\t', names=['edge', 'co2'])
df_edges['edge'] = df_edges['edge'].apply(lambda x: x.replace(' ', ''))

# Calculate total CO2 emissions for each edge
total_co2 = df_edges.groupby('edge')['co2'].sum()

# Get edge shapes and corresponding total CO2 emissions
shapes = []
values = []

for edge_id, co2 in total_co2.items():
    e = net.getEdge(edge_id)
    shapes.append(e.getShape())
    values.append(co2)

# Set color scale
min_value = min(values)
max_value = max(values)
color_scale = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize
                                           (vmin=min_value, vmax=max_value), cmap='viridis')

# Create LineCollection for plotting
line_segments_edges = LineCollection(shapes, colors=color_scale.to_rgba(values), linewidths=[1,])

# Plot the graph
fig, axs = plt.subplots(figsize=(8, 8))
axs.add_collection(line_segments_edges)
axs.autoscale_view(True, True, True)
axs.xaxis.set_ticklabels([])
axs.yaxis.set_ticklabels([])

# Plot RSUs
rsus = get_rsus(RSU_FILE)
for rsu in rsus:
    circle = patches.Circle((rsu['x'], rsu['y']), radius=1000, edgecolor='blue', alpha=0.25)
    axs.add_patch(circle)

# Configure limits of axes to ensure all RSUs are within the plot
min_x = min(rsu['x'] for rsu in rsus)
max_x = max(rsu['x'] for rsu in rsus)
min_y = min(rsu['y'] for rsu in rsus)
max_y = max(rsu['y'] for rsu in rsus)

x_padding = (max_x - min_x) * 0.2 # Aumenta a zona das RSUs
y_padding = (max_y - min_y) * 0.2 # Aumenta a zona das RSUs

axs.set_xlim(min_x - x_padding, max_x + x_padding)
axs.set_ylim(min_y - y_padding, max_y + y_padding)

# Add colorbar
print('Adding colorbar ...')
plt.colorbar(color_scale, ax=axs)
plt.title('MoST Edges CO2')
plt.show()
