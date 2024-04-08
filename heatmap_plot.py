# Author: Carnot Braun & Allan M. de Souza
# Email: carnotbraun@gmail.com & allanms@unicamp.br
# Description: Script for plotting a heatmap of CO2 emissions from RSUs.

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
 
def load_rsus_data(folder_path):
    """Load CO2 data from RSUs from CSV files in a folder."""
    dfs = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            rsu_id = extract_rsu_id(filename)
            try:
                df = pd.read_csv(file_path, sep=',', header=0)
                # 15 minutes interval
                df['step'] = pd.to_datetime(df['step'], unit='s')
                df = df.groupby([pd.Grouper(key='step', freq='600s')]).sum().reset_index()
                df['step'] = pd.to_datetime(df['step']).dt.strftime('%H:%M')
                df['rsu_id'] = int(rsu_id)
                dfs.append(df)
            except Exception as e:
                print(f"Error while reading file {filename}: {str(e)}")
    return pd.concat(dfs)

def extract_rsu_id(filename):
    """Extract the RSU ID from the file name."""
    return filename.split('_')[-1].split('.')[0]

def plot_heatmap(data, environment):
    """Plot a heatmap of CO2 emissions from RSUs."""
    plt.figure(figsize=(6, 4))
    ax = sns.heatmap(data, cmap='gnuplot_r')
    ax.set_xlabel('Horário do Dia')
    ax.set_ylabel('RSU')
    #plt.title(f'{environment} CO2 Emission')
    plt.savefig(f'{environment.lower()}_co2_heatmap', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main function."""
    env = {1: 'Lust', 2: 'Most', 3: 'Cologne'}
    env_id = 2  # Change to the desired environment
    folder_path = f'/Users/carnotbraun/tese-mestrado/simu/data/rsus_{env[env_id].lower()}_csv'
    try:
        data = load_rsus_data(folder_path)
        data = data.set_index('rsu_id')
        data = data.reset_index()
        print(data.head())
        pivot_df = data.pivot_table(index='rsu_id', columns='step', values='c02_emission', aggfunc='sum')
        plot_heatmap(pivot_df, env[env_id])
    except Exception as e:
        print(f"Error during script execution: {str(e)}")

if __name__ == "__main__":
    main()