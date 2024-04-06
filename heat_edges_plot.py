import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.collections import LineCollection

# Read data from co2_lust.txt
df_edges = pd.read_csv('/Users/carnotbraun/tese-mestrado/code/co2_lust.txt', sep='\t', names=['edge', 'co2'])
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

# Normalize CO2 emissions for color mapping
cNorm = matplotlib.colors.Normalize(vmin=min(values), vmax=max(values))
scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap='magma')
colors = scalarMap.to_rgba(values)

# Create LineCollection for plotting
line_segments = LineCollection(shapes, colors=colors, linewidths=[1,])

# Plot the graph
fig, axs = plt.subplots(figsize=(8, 8))
axs.add_collection(line_segments)
axs.autoscale_view(True, True, True)
axs.xaxis.set_ticklabels([])
axs.yaxis.set_ticklabels([])

# Add colorbar
plt.colorbar(scalarMap)

plt.show()
