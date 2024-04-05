import os
import folium
from folium.plugins import HeatMap
import pandas as pd
import traci
import sumolib

# Connect to SUMO
sumo_cmd = "/Users/carnotbraun/tese-mestrado/simu/sumo/bin/sumo"
sumo_cfg = "/Users/carnotbraun/tese-mestrado/simu/LuSTScenario/scenario/due.actuated.sumocfg"
sumo_net = "/Users/carnotbraun/tese-mestrado/simu/LuSTScenario/scenario/lust.net.xml"
traci.start([sumo_cmd, "-c", sumo_cfg, "--net-file", sumo_net, "--scale", '0.3'])

# Function to convert SUMO coordinates to real-world coordinates (latitude, longitude)
def convert_sumo_coords_to_lat_lon(coords):
    lon, lat = traci.simulation.convertGeo(coords[0], coords[1])
    return lat, lon

# Get edge coordinates from SUMO
net = sumolib.net.readNet(sumo_net)
edges_data = {edge.getID(): edge.getShape() for edge in net.getEdges()}

# Create a Folium Map centered around LuST
map_obj = folium.Map(location=[49.60967, 6.12960], zoom_start=12)

# Path to the folder containing CSV files for different zones
folder_path = '/Users/carnotbraun/tese-mestrado/simu/data/rsus_lust_csv'

# Iterate over each CSV file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        # Load the CSV file containing RSU data for the current zone
        rsu_data = pd.read_csv(os.path.join(folder_path, filename))
        
        # Merge RSU data with edge coordinates based on edge IDs
        rsu_data['edge_coords'] = rsu_data['road_id'].map(edges_data)
        
        # Convert SUMO coordinates to real-world latitude and longitude
        rsu_data['Latitude'], rsu_data['Longitude'] = zip(*rsu_data['edge_coords'].apply(lambda x: convert_sumo_coords_to_lat_lon(x) if x else (None, None)))
        
        # Drop rows with missing latitude or longitude
        rsu_data = rsu_data.dropna(subset=['Latitude', 'Longitude'])
        
        # Create a list of tuples containing (latitude, longitude, CO2 emission) for each edge
        heat_data = rsu_data[['Latitude', 'Longitude', 'CO2_emission']].values.tolist()
        
        # Add heatmap layer to the map
        HeatMap(heat_data, radius=15).add_to(map_obj)

# Save the map as an HTML file
map_obj.save('lust_heatmap.html')

# Disconnect from SUMO
traci.close()
