import pandas as pd
import os
import pickle

# Folder path
folder_path = '/Users/carnotbraun/tese-mestrado/simu/data/most_edges'
#Adapt the range for all in the folder path
for rsu_id in range(6):
    # Creating a list to store the DataFrames of each CSV file
    dfs = []

    # Load the list of edges for the current RSU
    roads_file = open(f'/Users/carnotbraun/tese-mestrado/simu/data/rsus_most/RSU_{rsu_id}.pickle', 'rb')
    rsu_edge_list = pickle.load(roads_file)

    # Iterating over the CSV files and reading the data
    for file in rsu_edge_list:
        df = pd.read_csv(os.path.join(folder_path, f'{file}.csv'), sep=';',
                         names=['step', 'road_id', 'road_speed', 'c02_emission',
                                'fuel_consumption', 'average_vehicles', 'noise_emission'])
        dfs.append(df)

    # Concatenating all the DataFrames into a single DataFrame
    combined_df = pd.concat(dfs)

    # Save the combined DataFrame to CSV
    combined_df.to_csv(f'/Users/carnotbraun/tese-mestrado/simu/data/rsus_most_csv/RSU_{rsu_id}.csv', index=False)
