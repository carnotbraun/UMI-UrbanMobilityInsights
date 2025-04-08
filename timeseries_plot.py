# Authors: Carnot Braun & Allan M. de Souza
# Email: carnotbraun@gmail.com & allanms@unicamp.br
# Description: Script for plotting a time series of CO2 emissions from RSUs.

import pandas as pd
import matplotlib.pyplot as plt
import os

# Set the font size of the plots
plt.rcParams.update({'font.size': 20})

def load_data(): # passar env_id como argumento
    """Load data from CSV files in a folder."""
    #env = {1: 'Lust', 2: 'Most', 3: 'Cologne'}
    #folder_path = f'/data/{env[env_id].lower()}_edges/'
    folder_path = '../To/The_Edges_scenario/'
    files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    dfs = []
    
    for file in files:
        df = pd.read_csv(os.path.join(folder_path, file), sep=';',
                         names=['step', 'road_id', 'road_speed', 'co2_emission',
                                'fuel_consumption', 'average_vehicles'])
        
        # Ensure numeric values, coercing errors to NaN
        df['step'] = pd.to_numeric(df['step'], errors='coerce')
        df['road_speed'] = pd.to_numeric(df['road_speed'], errors='coerce')
        df['co2_emission'] = pd.to_numeric(df['co2_emission'], errors='coerce')
        df['fuel_consumption'] = pd.to_numeric(df['fuel_consumption'], errors='coerce')
        df['average_vehicles'] = pd.to_numeric(df['average_vehicles'], errors='coerce')
        
        # Convert 'step' values from seconds to hours
        df['step'] = df['step'] / 3600  # Convert seconds to hours
        
        # Convert 'c02_emission' values from milligrams to grams
        df['co2_emission'] = df['co2_emission'] / 1000_000  # Convert mg to g
        
        dfs.append(df)
    
    return pd.concat(dfs)

def plot_co2_emission_over_time(data):
    """Plot CO2 emission over time."""
    plt.figure(figsize=(7, 5.5))
    data.groupby('step')['co2_emission'].sum().plot(kind='line', color='b')
    plt.xlim(0, 24)
    plt.xticks(range(0, 25, 4), [f'{i}:00' for i in range(0, 25, 4)])
    plt.xlabel('Horário do Dia')
    plt.ylabel('Emissão de CO2 (kg)')
    plt.grid(True, linestyle=':', alpha=0.6)
    #plt.savefig(f'rsu_cologne', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main function."""
    #env_id = 3  # Change to the desired environment ID
    data = load_data() #env_id)
    plot_co2_emission_over_time(data)

if __name__ == "__main__":
    main()
