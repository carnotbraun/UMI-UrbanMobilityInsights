import pandas as pd
import sumolib 
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.collections import LineCollection

NET_FILE = '/Users/carnotbraun/tese-mestrado/simu/LuSTScenario/scenario/lust.net.xml'
# Read data from co2_lust.txt
net = sumolib.net.readNet(NET_FILE)
df_edges = pd.read_csv('/Users/carnotbraun/tese-mestrado/simu/data/heatmap/co2_lust.txt', sep='\t', names=['edge', 'co2'])
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
color_scale = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=min_value, vmax=max_value), cmap='magma')

# Create LineCollection for plotting
line_segments = LineCollection(shapes, colors=color_scale.to_rgba(values), linewidths=[1,])

# Plot the graph
fig, axs = plt.subplots(figsize=(8, 8))
axs.add_collection(line_segments)
axs.autoscale_view(True, True, True)
axs.xaxis.set_ticklabels([])
axs.yaxis.set_ticklabels([])

# Add colorbar
plt.colorbar(color_scale, ax=axs)
plt.title('LuST Edges CO2')
plt.show()
